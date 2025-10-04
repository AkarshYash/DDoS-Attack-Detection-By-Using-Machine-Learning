"""
Shield-AI MVP (single-file prototype)
Requirements:
  pip install fastapi uvicorn starlette sklearn pandas numpy joblib python-multipart python-jose[cryptography]
  Optional: xgboost shap

What this file contains:
 - FastAPI backend for auth, domain registration, flow ingestion, ML scoring, blocking
 - Simple in-memory DB (SQLite via SQLModel could be used; here we use sqlite3 for portability)
 - Minimal frontend served from the same app (single-page HTML/JS/CSS). Includes dark/light theme toggle and a pop help/chat bubble.
 - ML training & scoring hooks that expect CC-DoS 2019M dataset at ./data/cc_ddos_2019m.csv
 - Gemini chatbot integration placeholder (set GEMINI_API_KEY env var, implement actual call per Google API docs)

This is a portable starting point — expand into modular services, add Celery, TimescaleDB, Kafka, or k8s for production.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sqlite3
import os
import json
import time
from typing import List, Dict, Any
import threading
import traceback

# ML imports
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Security
import hashlib
import secrets
import base64
from jose import JWTError, jwt

# Config
SECRET_KEY = os.environ.get("SHIELD_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 3600 * 24
DATA_PATH = "./data/cc_ddos_2019m.csv"  # user should place dataset here
MODEL_PATH = "./models"
os.makedirs(MODEL_PATH, exist_ok=True)

app = FastAPI(title="Shield-AI MVP")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple sqlite-based persistence for users, domains, blocks, flows
DB_PATH = "shield_ai.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()

def init_db():
    cur.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, role TEXT, org TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS domains (id INTEGER PRIMARY KEY, org TEXT, domain TEXT, token TEXT, verified INTEGER DEFAULT 0)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS blocks (id INTEGER PRIMARY KEY, domain TEXT, ip TEXT, start_ts INTEGER, end_ts INTEGER, reason TEXT, by TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS flows (id INTEGER PRIMARY KEY, domain TEXT, src_ip TEXT, dst_ip TEXT, protocol TEXT, packet_count INTEGER, byte_count INTEGER, ts INTEGER, features_json TEXT, score REAL)''')
    conn.commit()

init_db()

# ----- Auth helpers -----

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_SECONDS):
    to_encode = data.copy()
    to_encode.update({"exp": int(time.time()) + expires_delta})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# ----- Simple user & domain API -----

@app.post('/api/register')
async def register(email: str = Form(...), password: str = Form(...), role: str = Form('employee'), org: str = Form('personal')):
    pwd = hash_password(password)
    try:
        cur.execute('INSERT INTO users (email, password_hash, role, org) VALUES (?, ?, ?, ?)', (email, pwd, role, org))
        conn.commit()
    except sqlite3.IntegrityError:
        return JSONResponse({"error": "email_exists"}, status_code=400)
    token = create_access_token({"sub": email, "role": role, "org": org})
    return {"access_token": token, "token_type": "bearer"}

@app.post('/api/login')
async def login(email: str = Form(...), password: str = Form(...)):
    pwd = hash_password(password)
    cur.execute('SELECT id, role, org FROM users WHERE email=? AND password_hash=?', (email, pwd))
    row = cur.fetchone()
    if not row:
        return JSONResponse({"error": "invalid_credentials"}, status_code=401)
    token = create_access_token({"sub": email, "role": row[1], "org": row[2]})
    return {"access_token": token, "token_type": "bearer"}

@app.post('/api/register_domain')
async def register_domain(domain: str = Form(...), token: str = Form(...)):
    # token used to associate with JWT in headers in UI (bearer). Here token param is optional.
    # Generate domain monitoring token for agents
    dtoken = base64.urlsafe_b64encode(secrets.token_bytes(16)).decode()
    cur.execute('INSERT INTO domains (org, domain, token, verified) VALUES (?, ?, ?, ?)', ("unknown", domain, dtoken, 0))
    conn.commit()
    return {"domain": domain, "monitor_token": dtoken}

@app.get('/api/domains')
async def list_domains():
    cur.execute('SELECT id, org, domain, token, verified FROM domains')
    rows = cur.fetchall()
    return [{"id": r[0], "org": r[1], "domain": r[2], "token": r[3], "verified": r[4]} for r in rows]

# ----- Flow ingestion & ML scoring -----

# In-memory ML models
models = {
    'rf': None,
    'iso': None,
    'scaler': None
}

FEATURE_COLUMNS = ['packet_count', 'byte_count', 'protocol_num']

def extract_features(flow: Dict[str, Any]) -> List[float]:
    # flow example: {src_ip, dst_ip, protocol, packet_count, byte_count}
    proto_map = {'TCP':6, 'UDP':17, 'ICMP':1}
    proto_num = proto_map.get(flow.get('protocol','TCP').upper(), 0)
    pkt = int(flow.get('packet_count', 0))
    bytec = int(flow.get('byte_count', 0))
    return [pkt, bytec, proto_num]

@app.post('/api/ingest_flow')
async def ingest_flow(domain: str = Form(...), src_ip: str = Form(...), dst_ip: str = Form(...), protocol: str = Form('TCP'), packet_count: int = Form(0), byte_count: int = Form(0)):
    ts = int(time.time())
    features = extract_features({'protocol': protocol, 'packet_count': packet_count, 'byte_count': byte_count})
    score = score_features(features)
    cur.execute('INSERT INTO flows (domain, src_ip, dst_ip, protocol, packet_count, byte_count, ts, features_json, score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (domain, src_ip, dst_ip, protocol, packet_count, byte_count, ts, json.dumps(features), float(score)))
    conn.commit()
    # broadcast via websocket (simple pub)
    broadcaster.broadcast({'type':'flow', 'domain': domain, 'src_ip': src_ip, 'score': score, 'ts': ts})
    # Auto-block if score above threshold
    if score >= 0.9:
        block_ip(domain, src_ip, duration_seconds=3600, reason='auto-high-score', by='system')
    return {'status': 'ok', 'score': score}

# ----- Blocking API -----

def block_ip(domain: str, ip: str, duration_seconds: int = 3600, reason: str = 'manual', by: str = 'admin'):
    start_ts = int(time.time())
    end_ts = start_ts + duration_seconds
    cur.execute('INSERT INTO blocks (domain, ip, start_ts, end_ts, reason, by) VALUES (?, ?, ?, ?, ?, ?)', (domain, ip, start_ts, end_ts, reason, by))
    conn.commit()
    broadcaster.broadcast({'type':'block', 'domain': domain, 'ip': ip, 'start_ts': start_ts, 'end_ts': end_ts, 'reason': reason})

@app.post('/api/block')
async def api_block(domain: str = Form(...), ip: str = Form(...), duration_seconds: int = Form(3600), reason: str = Form('manual'), by: str = Form('admin')):
    block_ip(domain, ip, duration_seconds, reason, by)
    return {'status': 'blocked', 'ip': ip}

@app.post('/api/unblock')
async def api_unblock(block_id: int = Form(...)):
    cur.execute('DELETE FROM blocks WHERE id=?', (block_id,))
    conn.commit()
    return {'status': 'unblocked'}

@app.get('/api/blocks')
async def list_blocks():
    cur.execute('SELECT id, domain, ip, start_ts, end_ts, reason, by FROM blocks')
    rows = cur.fetchall()
    return [{'id': r[0], 'domain': r[1], 'ip': r[2], 'start_ts': r[3], 'end_ts': r[4], 'reason': r[5], 'by': r[6]} for r in rows]

# ----- ML: train & score -----

def train_models(data_path=DATA_PATH):
    try:
        df = pd.read_csv(data_path)
    except Exception as e:
        print('Failed to load dataset:', e)
        return {'error': 'no_dataset'}
    # NOTE: CC-DoS dataset will require domain-specific parsing. Here we assume some columns exist.
    # This is a simplified pipeline: pick packet_count, byte_count, protocol (as num), label (attack:1/0)
    if 'label' not in df.columns:
        # try to guess or map
        if 'attacked' in df.columns:
            df['label'] = df['attacked'].astype(int)
        else:
            print('Dataset missing label column. Please preprocess CC-DoS into CSV with a "label" column.')
            return {'error': 'no_label'}
    def proto_map(v):
        try:
            return int(v)
        except:
            return 6
    X = df[['packet_count','byte_count']].copy()
    X['protocol_num'] = df['protocol'].apply(proto_map) if 'protocol' in df.columns else 6
    y = df['label']
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X[FEATURE_COLUMNS])
    X_train, X_test, y_train, y_test = train_test_split(Xs, y, test_size=0.2, random_state=42)
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    iso = IsolationForest(contamination=0.01, random_state=42)
    iso.fit(X_train)
    # save
    joblib.dump(rf, os.path.join(MODEL_PATH, 'rf.joblib'))
    joblib.dump(iso, os.path.join(MODEL_PATH, 'iso.joblib'))
    joblib.dump(scaler, os.path.join(MODEL_PATH, 'scaler.joblib'))
    models['rf'] = rf
    models['iso'] = iso
    models['scaler'] = scaler
    print('Training complete. Models saved to', MODEL_PATH)
    return {'status': 'trained'}

def load_models():
    try:
        models['rf'] = joblib.load(os.path.join(MODEL_PATH, 'rf.joblib'))
        models['iso'] = joblib.load(os.path.join(MODEL_PATH, 'iso.joblib'))
        models['scaler'] = joblib.load(os.path.join(MODEL_PATH, 'scaler.joblib'))
        print('Models loaded')
    except Exception as e:
        print('Could not load models:', e)

load_models()

def score_features(features: List[float]) -> float:
    try:
        scaler = models.get('scaler')
        rf = models.get('rf')
        iso = models.get('iso')
        X = np.array(features).reshape(1, -1)
        if scaler:
            Xs = scaler.transform(X)
        else:
            Xs = X
        probs = rf.predict_proba(Xs)[0][1] if rf else 0.0
        iso_score = 0.5
        if iso:
            iso_raw = iso.decision_function(Xs)[0]
            # convert decision function to 0-1 like anomaly score
            iso_score = 1.0 - (1.0 / (1.0 + np.exp(-iso_raw)))
        # combine
        score = (0.7 * probs) + (0.3 * iso_score)
        return float(score)
    except Exception as e:
        print('scoring error', e)
        return 0.0

@app.post('/api/train_models')
async def api_train_models():
    res = train_models()
    return res

# ----- Simple Gemini chatops placeholder -----

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

def query_gemini(prompt: str):
    # Placeholder: implement according to Google's GenAI API docs with GEMINI_API_KEY.
    # Example: call REST endpoint with auth and send prompt. Return assistant response.
    if not GEMINI_API_KEY:
        return "Gemini API key not set. Set GEMINI_API_KEY env var and implement the REST call in query_gemini()."
    # TODO: implement real call
    return f"[Gemini placeholder reply] I received your prompt: {prompt[:200]}"

@app.post('/api/chat')
async def chat_endpoint(request: Request):
    body = await request.json()
    prompt = body.get('prompt', '')
    resp = query_gemini(prompt)
    return {'reply': resp}

# ----- WebSocket broadcaster for realtime UI -----

class Broadcaster:
    def __init__(self):
        self.connections: List[WebSocket] = []
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)
    def disconnect(self, ws: WebSocket):
        try:
            self.connections.remove(ws)
        except:
            pass
    def broadcast(self, message: dict):
        # spawn thread to avoid blocking
        for ws in list(self.connections):
            try:
                threading.Thread(target=lambda w, m: self._send_sync(w, m), args=(ws, message), daemon=True).start()
            except Exception:
                pass
    def _send_sync(self, ws: WebSocket, message: dict):
        try:
            import asyncio
            asyncio.run(ws.send_json(message))
        except Exception:
            try:
                self.disconnect(ws)
            except:
                pass

broadcaster = Broadcaster()

@app.websocket('/ws')
async def websocket_endpoint(ws: WebSocket):
    await broadcaster.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            # echo or handle
            await ws.send_text(f'ack:{data}')
    except WebSocketDisconnect:
        broadcaster.disconnect(ws)

# ----- Serve a simple single-page UI -----

INDEX_HTML = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Shield-AI — MVP</title>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <style>
    :root{--bg:#f5f7fb;--fg:#0b1220;--card:#fff}
    .dark{--bg:#0b1220;--fg:#e6eef8;--card:#0e1620}
    body{background:var(--bg);color:var(--fg);font-family:Inter,Segoe UI,system-ui,Arial;margin:0;padding:0}
    header{padding:12px 20px;display:flex;align-items:center;justify-content:space-between;background:linear-gradient(90deg, rgba(63,94,251,0.08), rgba(252,70,107,0.04));}
    .container{padding:20px}
    .card{background:var(--card);border-radius:10px;padding:12px;margin-bottom:12px;box-shadow:0 6px 18px rgba(2,6,23,0.06)}
    .grid{display:grid;grid-template-columns:1fr 360px;gap:16px}
    .small{font-size:13px;color:rgba(0,0,0,0.6)}
    .theme-toggle{cursor:pointer;padding:8px;border-radius:8px;border:1px solid rgba(0,0,0,0.06)}
    /* chat bubble */
    #helpBtn{position:fixed;right:18px;bottom:18px;border-radius:50%;width:64px;height:64px;border:none;background:#007bff;color:#fff;font-weight:700;box-shadow:0 8px 30px rgba(0,0,0,0.2);}
    #chatBox{position:fixed;right:18px;bottom:90px;width:340px;max-height:480px;display:none;flex-direction:column}
    #chatBox .messages{flex:1;overflow:auto;padding:8px}
    #chatBox textarea{width:100%;box-sizing:border-box;height:80px}
    .btn{padding:8px 12px;border-radius:8px;border:none;cursor:pointer}
  </style>
</head>
<body>
  <header>
    <div style="display:flex;align-items:center;gap:12px"><h3 style="margin:0">Shield-AI</h3><div class="small">MVP — DDoS detection & defense</div></div>
    <div style="display:flex;gap:8px;align-items:center"><button class="theme-toggle" id="toggleTheme">Toggle theme</button><button class="btn" id="trainBtn">Train Models</button></div>
  </header>
  <div class="container">
    <div class="grid">
      <div>
        <div class="card">
          <h4>Live Traffic</h4>
          <div id="liveFeed" class="small">No activity yet.</div>
        </div>
        <div class="card">
          <h4>Actions</h4>
          <div style="display:flex;gap:8px"><input id="domainInput" placeholder="domain.tld"/><input id="ipInput" placeholder="1.2.3.4"/><button class="btn" id="blockBtn">Block IP</button></div>
        </div>
        <div class="card">
          <h4>Upload CC-DoS CSV</h4>
          <form id="uploadForm">
            <input type="file" name="file" id="fileInput" accept=".csv" />
            <button class="btn" type="submit">Upload</button>
          </form>
          <div class="small">Place a preprocessed CC-DoS 2019M CSV and train the model.</div>
        </div>
      </div>
      <div>
        <div class="card">
          <h4>Dashboard</h4>
          <div>Active blocks: <span id="blocksCount">0</span></div>
          <div>Recent Alerts: <ul id="alerts"></ul></div>
        </div>
        <div class="card">
          <h4>Admin Panel</h4>
          <div class="small">Register domains, manage users in a full app. This MVP focuses on core flow ingestion and scoring.</div>
        </div>
      </div>
    </div>
  </div>

  <button id="helpBtn">?</button>
  <div id="chatBox" class="card" style="display:flex">
    <div style="display:flex;flex-direction:column;width:100%">
      <div style="display:flex;justify-content:space-between;align-items:center;padding:8px"><strong>Need help?</strong><button id="closeChat">X</button></div>
      <div class="messages" id="messages"></div>
      <textarea id="prompt" placeholder="Describe the incident or ask for advice..."></textarea>
      <div style="display:flex;gap:8px;padding:8px"><button id="sendPrompt" class="btn">Send</button><button id="autoMit" class="btn">Auto-Mitigate</button></div>
    </div>
  </div>

<script>
  const ws = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws');
  ws.onmessage = (ev) => {
    try{ const d=JSON.parse(ev.data); if(d.type==='flow'){ const el=document.getElementById('liveFeed'); el.innerText = `Flow from ${d.src_ip} score=${d.score.toFixed(3)} at ${new Date(d.ts*1000).toLocaleTimeString()}`; const li=document.createElement('li'); li.innerText = `${d.src_ip} score=${d.score.toFixed(3)}`; document.getElementById('alerts').prepend(li);}
      if(d.type==='block'){ document.getElementById('blocksCount').innerText = parseInt(document.getElementById('blocksCount').innerText || '0') + 1; }
    }catch(e){ console.log('ws msg',ev.data)}
  };
  document.getElementById('helpBtn').onclick = ()=>{ document.getElementById('chatBox').style.display='flex'; }
  document.getElementById('closeChat').onclick = ()=>{ document.getElementById('chatBox').style.display='none'; }
  document.getElementById('sendPrompt').onclick = async ()=>{
    const p = document.getElementById('prompt').value;
    const res = await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:p})});
    const j = await res.json();
    const m=document.getElementById('messages');
    const u=document.createElement('div'); u.innerText='You: '+p; m.appendChild(u);
    const a=document.createElement('div'); a.innerText='Assistant: '+j.reply; m.appendChild(a);
  }
  document.getElementById('blockBtn').onclick = async ()=>{
    const domain = document.getElementById('domainInput').value; const ip = document.getElementById('ipInput').value;
    const fd = new FormData(); fd.append('domain', domain); fd.append('ip', ip);
    const r = await fetch('/api/block',{method:'POST',body:fd}); const j = await r.json(); alert(JSON.stringify(j));
  }
  document.getElementById('trainBtn').onclick = async ()=>{
    const r = await fetch('/api/train_models',{method:'POST'}); const j = await r.json(); alert(JSON.stringify(j));
  }
  document.getElementById('uploadForm').onsubmit = async (e)=>{
    e.preventDefault(); const f = document.getElementById('fileInput').files[0]; if(!f) return alert('no file');
    const fd = new FormData(); fd.append('file', f);
    const r = await fetch('/api/upload_dataset',{method:'POST',body:fd}); const j = await r.json(); alert(JSON.stringify(j));
  }
  document.getElementById('toggleTheme').onclick = ()=>{ document.body.classList.toggle('dark'); }
</script>
</body>
</html>
"""

@app.get('/')
async def index():
    return HTMLResponse(INDEX_HTML)

@app.post('/api/upload_dataset')
async def upload_dataset(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        os.makedirs('data', exist_ok=True)
        path = os.path.join('data', 'cc_ddos_2019m.csv')
        with open(path, 'wb') as f:
            f.write(contents)
        return {'status': 'saved', 'path': path}
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=500)

# ----- Simple static route for download example -----
@app.get('/download_report')
async def download_report():
    # simple demo report
    report_path = 'report_example.html'
    with open(report_path, 'w') as f:
        f.write('<h1>Shield-AI Report</h1><p>Example.</p>')
    return FileResponse(report_path, media_type='text/html', filename='shield_report.html')

# ----- Run server -----
if __name__ == '__main__':
    print('Starting Shield-AI MVP on http://127.0.0.1:8000')
    uvicorn.run('shield_ai_mvp:app', host='0.0.0.0', port=8000, reload=True)
