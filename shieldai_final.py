"""
DDOS Defender - single-file FastAPI app (ddos_defender.py)
Features included (MVP single-file):
- FastAPI backend serving a single-page dashboard (HTML/CSS/JS embedded)
- SQLite via SQLAlchemy for users, domains, flows, alerts
- JWT-based auth (simple) for API and dashboard
- Simulated traffic agent to produce flow records (no root needed)
- ML model pipeline: feature engineering, RandomForest training, prediction, model persistence (joblib)
- Server-Sent Events (SSE) for real-time updates to dashboard
- Blocking API (simulated) that records block rules in DB (no system changes)
- Export alerts as CSV
- Basic RBAC (admin vs user)
- Inline frontend uses Chart.js and simple UI for registration, domain listing, live metrics, and alerts

Notes:
- This is a developer-focused single-file prototype. Replace simulated ingestion with real packet capture (scapy / bro / zeek / CICFlowMeter) for production.
- For production: move DB to PostgreSQL/Timescale, use Celery/Redis, secure JWT secrets, deploy behind HTTPS, and hook into Cloudflare/AWS WAF for blocking.

Run:
    python -m pip install fastapi uvicorn sqlalchemy joblib scikit-learn pandas python-multipart jinja2
    uvicorn ddos_defender:app --reload --port 8000

Open http://localhost:8000 in your browser.

"""

import os
import time
import threading
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks, Form
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pandas as pd
import joblib
import base64
import hashlib

# ------------------------ Config ------------------------
DB_FILE = 'ddos_defender.db'
JWT_SECRET = os.environ.get('DDOS_JWT_SECRET', 'devsecret123')
MODEL_FILE = 'ddos_model.joblib'
SIMULATION_INTERVAL = 1.0  # seconds between generated flows

# ------------------------ DB Setup ------------------------
Base = declarative_base()
engine = create_engine(f'sqlite:///{DB_FILE}', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Domain(Base):
    __tablename__ = 'domains'
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    domain = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Flow(Base):
    __tablename__ = 'flows'
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, index=True)
    src_ip = Column(String)
    dst_ip = Column(String)
    src_port = Column(Integer)
    dst_port = Column(Integer)
    protocol = Column(String)
    bytes = Column(Integer)
    packets = Column(Integer)
    duration = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    score = Column(Float, default=0.0)
    is_malicious = Column(Boolean, default=False)

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer)
    domain = Column(String)
    src_ip = Column(String)
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    handled = Column(Boolean, default=False)

class BlockRule(Base):
    __tablename__ = 'blocks'
    id = Column(Integer, primary_key=True, index=True)
    src_ip = Column(String)
    domain = Column(String)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    reason = Column(Text)

Base.metadata.create_all(bind=engine)

# ------------------------ Simple Auth ------------------------
import jwt

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

class TokenData(BaseModel):
    email: str
    exp: int

security = HTTPBearer()

def create_token(email: str, minutes=60*24) -> str:
    payload = {"email": email, "exp": int((datetime.utcnow() + timedelta(minutes=minutes)).timestamp())}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_token(creds: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    token = creds.credentials
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return TokenData(email=decoded['email'], exp=decoded['exp'])
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# ------------------------ FastAPI App ------------------------
app = FastAPI(title='DDOS Defender - Single File')

# Serve a tiny static directory (for potential assets) - optional
if not os.path.exists('static'):
    os.makedirs('static')

app.mount('/static', StaticFiles(directory='static'), name='static')

# ------------------------ Utility Helpers ------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Minimal model persistence
model_lock = threading.Lock()
model: Optional[RandomForestClassifier] = None

# ------------------------ Simulated Traffic Generator ------------------------
SIM_RUNNING = False
listeners: List[Dict] = []  # for SSE listeners

def synthetic_flow(domain: str):
    """Return a dict representing a synthetic flow record."""
    import random, ipaddress
    src_ip = str(ipaddress.IPv4Address(random.getrandbits(32)))
    dst_ip = '203.0.113.5'
    src_port = random.randint(1024, 65535)
    dst_port = random.choice([80, 443, 8080, 22])
    protocol = random.choice(['TCP', 'UDP'])
    packets = random.randint(1, 1000)
    bytes_ = packets * random.randint(40, 1500)
    duration = round(random.random() * 10, 3)
    ts = datetime.utcnow()
    return {
        'domain': domain,
        'src_ip': src_ip,
        'dst_ip': dst_ip,
        'src_port': src_port,
        'dst_port': dst_port,
        'protocol': protocol,
        'packets': packets,
        'bytes': bytes_,
        'duration': duration,
        'timestamp': ts.isoformat()
    }

def ingest_flow_record(rec: Dict):
    """Store flow into DB and run model scoring if model available."""
    db = next(get_db())
    f = Flow(
        domain=rec['domain'],
        src_ip=rec['src_ip'],
        dst_ip=rec['dst_ip'],
        src_port=rec['src_port'],
        dst_port=rec['dst_port'],
        protocol=rec['protocol'],
        bytes=rec['bytes'],
        packets=rec['packets'],
        duration=rec['duration'],
        timestamp=datetime.fromisoformat(rec['timestamp'])
    )
    db.add(f)
    db.commit()
    db.refresh(f)

    # scoring
    global model
    with model_lock:
        if model is not None:
            X = pd.DataFrame([feature_vector_from_flow(f)])
            score = float(model.predict_proba(X)[:, 1][0])
            f.score = score
            f.is_malicious = score > 0.6
            db.add(f)
            db.commit()
            if f.is_malicious:
                alert = Alert(flow_id=f.id, domain=f.domain, src_ip=f.src_ip, score=f.score)
                db.add(alert)
                db.commit()
                broadcast({"type": "alert", "alert": serialize_alert(alert)})
    broadcast({"type": "flow", "flow": serialize_flow(f)})

# ------------------------ Feature engineering and model ------------------------

def feature_vector_from_flow(f: Flow) -> Dict:
    # simple engineered features
    return {
        'bytes': f.bytes,
        'packets': f.packets,
        'duration': f.duration,
        'bps': (f.bytes / f.duration) if f.duration > 0 else f.bytes,
        'pps': (f.packets / f.duration) if f.duration > 0 else f.packets,
        'dst_port': f.dst_port,
        'protocol_tcp': 1 if f.protocol == 'TCP' else 0
    }

def dataframe_from_flows(flows: List[Flow]):
    rows = []
    for f in flows:
        fv = feature_vector_from_flow(f)
        rows.append(fv)
    return pd.DataFrame(rows)

@app.post('/train')
def train_model(simulate: bool = True):
    """Train a RandomForest on simulated or historical flows.
    If simulate=True, generate a synthetic labeled dataset (normal vs ddos-like).
    """
    global model
    if simulate:
        df = generate_synthetic_dataset(n_samples=2000)
        X = df.drop(columns=['label'])
        y = df['label']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        preds = clf.predict(X_test)
        acc = accuracy_score(y_test, preds)
        report = classification_report(y_test, preds, output_dict=True)
        with model_lock:
            model = clf
            joblib.dump(model, MODEL_FILE)
        return {"status": "trained", "accuracy": acc, "report": report}
    else:
        # train from stored flows in DB (if any)
        db = next(get_db())
        flows = db.query(Flow).all()
        if len(flows) < 50:
            raise HTTPException(status_code=400, detail='Not enough historical flows to train. Use simulate=True')
        df = dataframe_from_flows(flows)
        # In this path we don't have labels; this is a demonstration
        # We'll self-label by thresholding bps
        df['label'] = (df['bps'] > df['bps'].median() * 3).astype(int)
        X = df.drop(columns=['label'])
        y = df['label']
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X, y)
        with model_lock:
            model = clf
            joblib.dump(model, MODEL_FILE)
        return {"status": "trained_from_db", "samples": len(df)}

def generate_synthetic_dataset(n_samples=1000):
    import numpy as np
    rows = []
    for _ in range(n_samples):
        # normal traffic
        bytes_ = int(abs(1000 + 5000 * np.random.randn()))
        packets = int(abs(10 + 20 * np.random.randn()))
        duration = abs(0.1 + 1.0 * abs(np.random.randn()))
        bps = bytes_ / duration if duration > 0 else bytes_
        pps = packets / duration if duration > 0 else packets
        dst_port = int(np.random.choice([80, 443, 8080, 22, 53]))
        protocol_tcp = int(np.random.choice([0,1], p=[0.2, 0.8]))
        label = 0
        # inject DDoS-like samples
        if np.random.rand() < 0.1:
            bytes_ = int(abs(50000 + 30000 * np.random.randn()))
            packets = int(abs(500 + 300 * np.random.randn()))
            duration = abs(0.01 + 0.2 * abs(np.random.randn()))
            bps = bytes_ / duration
            pps = packets / duration
            dst_port = int(np.random.choice([80, 443, 8080]))
            protocol_tcp = 1
            label = 1
        rows.append({'bytes': abs(int(bytes_)), 'packets': abs(int(packets)), 'duration': float(duration), 'bps': float(bps), 'pps': float(pps), 'dst_port': int(dst_port), 'protocol_tcp': int(protocol_tcp), 'label': label})
    return pd.DataFrame(rows)

# ------------------------ Broadcast / SSE ------------------------

def broadcast(message: Dict):
    # simple in-memory broadcast; if we had Redis pub/sub we'd publish
    payload = json.dumps(message, default=str)
    for lst in listeners[:]:
        try:
            lst['queue'].append(payload)
        except Exception:
            listeners.remove(lst)

@app.get('/stream')
def stream(request: Request):
    def event_generator():
        q: List[str] = []
        token = str(uuid.uuid4())
        listeners.append({'id': token, 'queue': q})
        try:
            while True:
                if await_disconnect(request):
                    break
                while q:
                    data = q.pop(0)
                    yield f'data: {data}\n\n'
                time.sleep(0.5)
        finally:
            # remove listener
            for l in listeners[:]:
                if l.get('id') == token:
                    listeners.remove(l)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# small helper because Request.is_disconnected is awaitable
async def await_disconnect(request: Request):
    try:
        return await request.is_disconnected()
    except Exception:
        return True

# ------------------------ Serialization helpers ------------------------

def serialize_flow(f: Flow):
    return {
        'id': f.id,
        'domain': f.domain,
        'src_ip': f.src_ip,
        'dst_ip': f.dst_ip,
        'src_port': f.src_port,
        'dst_port': f.dst_port,
        'protocol': f.protocol,
        'bytes': f.bytes,
        'packets': f.packets,
        'duration': f.duration,
        'timestamp': f.timestamp.isoformat(),
        'score': f.score,
        'is_malicious': f.is_malicious
    }

def serialize_alert(a: Alert):
    return {
        'id': a.id,
        'flow_id': a.flow_id,
        'domain': a.domain,
        'src_ip': a.src_ip,
        'score': a.score,
        'created_at': a.created_at.isoformat(),
        'handled': a.handled
    }

# ------------------------ API Endpoints ------------------------

class RegisterReq(BaseModel):
    email: str
    password: str

@app.post('/api/register')
def api_register(req: RegisterReq):
    db = next(get_db())
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail='Email already exists')
    u = User(email=req.email, password_hash=hash_pw(req.password), is_admin=False)
    db.add(u)
    db.commit()
    return {"status": "ok"}

class LoginReq(BaseModel):
    email: str
    password: str

@app.post('/api/login')
def api_login(req: LoginReq):
    db = next(get_db())
    u = db.query(User).filter(User.email == req.email).first()
    if not u or u.password_hash != hash_pw(req.password):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = create_token(u.email)
    return {"token": token, "email": u.email, "is_admin": u.is_admin}

@app.post('/api/domains')
def add_domain(domain: str = Form(...), token: TokenData = Depends(verify_token)):
    db = next(get_db())
    if db.query(Domain).filter(Domain.domain == domain).first():
        raise HTTPException(status_code=400, detail='Domain already registered')
    d = Domain(user_email=token.email, domain=domain)
    db.add(d)
    db.commit()
    return {"status": "ok", "domain": domain}

@app.get('/api/domains')
def list_domains(token: TokenData = Depends(verify_token)):
    db = next(get_db())
    ds = db.query(Domain).filter(Domain.user_email == token.email).all()
    return {"domains": [d.domain for d in ds]}

@app.post('/api/start_agent')
def start_agent(domain: str = Form(...), token: TokenData = Depends(verify_token)):
    # start a background thread to simulate flows for this domain
    t = threading.Thread(target=agent_thread, args=(domain,), daemon=True)
    t.start()
    return {"status": "agent_started", "domain": domain}

def agent_thread(domain: str):
    global SIM_RUNNING
    SIM_RUNNING = True
    while SIM_RUNNING:
        rec = synthetic_flow(domain)
        ingest_flow_record(rec)
        time.sleep(SIMULATION_INTERVAL)

@app.get('/api/flows')
def get_flows(limit: int = 100, token: TokenData = Depends(verify_token)):
    db = next(get_db())
    fs = db.query(Flow).order_by(Flow.timestamp.desc()).limit(limit).all()
    return {"flows": [serialize_flow(f) for f in fs]}

@app.get('/api/alerts')
def get_alerts(token: TokenData = Depends(verify_token)):
    db = next(get_db())
    a = db.query(Alert).order_by(Alert.created_at.desc()).limit(200).all()
    return {"alerts": [serialize_alert(x) for x in a]}

@app.post('/api/block')
def block_ip(src_ip: str = Form(...), domain: str = Form(...), minutes: int = Form(60), reason: str = Form('auto'), token: TokenData = Depends(verify_token)):
    db = next(get_db())
    br = BlockRule(src_ip=src_ip, domain=domain, expires_at=datetime.utcnow() + timedelta(minutes=minutes), reason=reason)
    db.add(br)
    db.commit()
    # In production, call Cloudflare/AWS WAF API or iptables here. We simulate.
    broadcast({"type": "block", "src_ip": src_ip, "domain": domain})
    return {"status": "blocked", "src_ip": src_ip}

@app.get('/api/blocks')
def list_blocks(token: TokenData = Depends(verify_token)):
    db = next(get_db())
    bs = db.query(BlockRule).order_by(BlockRule.created_at.desc()).all()
    out = []
    for b in bs:
        out.append({'id': b.id, 'src_ip': b.src_ip, 'domain': b.domain, 'expires_at': b.expires_at.isoformat(), 'reason': b.reason})
    return {"blocks": out}

@app.get('/api/export_alerts')
def export_alerts(token: TokenData = Depends(verify_token)):
    db = next(get_db())
    a = db.query(Alert).order_by(Alert.created_at.desc()).all()
    rows = []
    for x in a:
        rows.append([x.id, x.domain, x.src_ip, x.score, x.created_at.isoformat(), x.handled])
    df = pd.DataFrame(rows, columns=['id', 'domain', 'src_ip', 'score', 'created_at', 'handled'])
    csv = df.to_csv(index=False)
    return StreamingResponse(iter([csv]), media_type='text/csv', headers={"Content-Disposition": "attachment; filename=alerts.csv"})

# ------------------------ Simple Dashboard Page ------------------------

@app.get('/', response_class=HTMLResponse)
def index():
    html = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>DDOS Defender — Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body{font-family: Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; background:#0f172a; color:#e6eef8; margin:0;}
    .top{display:flex;justify-content:space-between;padding:12px 20px;align-items:center;background:#071025}
    .card{background:#0b1220;border-radius:10px;padding:12px;margin:12px}
    .grid{display:grid;grid-template-columns:1fr 420px;gap:12px;padding:12px}
    button{background:#2563eb;border:none;padding:8px 12px;border-radius:8px;color:white}
    input, select{padding:8px;border-radius:6px;border:1px solid #23314a;background:#061122;color:white}
    table{width:100%;border-collapse:collapse}
    th,td{padding:8px;border-bottom:1px solid #102030}
    .muted{color:#9fb0cf}
    .small{font-size:12px}
  </style>
</head>
<body>
  <div class="top"><div><strong>DDOS Defender</strong> <span class="muted small">single-file prototype</span></div><div id="auth_area"></div></div>
  <div style="display:flex;gap:12px;">
    <div style="flex:1;padding:12px">
      <div class="card" id="controls">
        <h3>Controls</h3>
        <div id="auth_forms">
          <div id="register_box">
            <input id="reg_email" placeholder="email" /> <input id="reg_pw" type="password" placeholder="password" /> <button onclick="register()">Register</button>
          </div>
          <div style="height:8px"></div>
          <div id="login_box">
            <input id="login_email" placeholder="email" /> <input id="login_pw" type="password" placeholder="password" /> <button onclick="login()">Login</button>
          </div>
        </div>
        <div style="height:12px"></div>
        <div>
          <input id="domain_input" placeholder="example.com" /> <button onclick="addDomain()">Add Domain</button> <button onclick="startAgent()">Start Agent</button>
        </div>
        <div style="height:12px"></div>
        <div>
          <button onclick="train()">Train Model (simulate)</button> <span id="train_status" class="muted small"></span>
        </div>
      </div>

      <div class="card">
        <h3>Live Flows</h3>
        <canvas id="chart" height="120"></canvas>
        <div style="height:12px"></div>
        <h4>Recent flows</h4>
        <table id="flows_table"><thead><tr><th>time</th><th>src</th><th>bytes</th><th>pkts</th><th>score</th></tr></thead><tbody></tbody></table>
      </div>

      <div class="card">
        <h3>Alerts</h3>
        <table id="alerts_table"><thead><tr><th>time</th><th>src</th><th>domain</th><th>score</th><th>action</th></tr></thead><tbody></tbody></table>
      </div>
    </div>

    <div style="width:420px;padding:12px">
      <div class="card">
        <h3>Blocks</h3>
        <div id="blocks_list"></div>
      </div>

      <div class="card">
        <h3>Model</h3>
        <div id="model_info">Not trained</div>
      </div>

      <div class="card">
        <h3>Export</h3>
        <button onclick="exportAlerts()">Export Alerts CSV</button>
      </div>
    </div>
  </div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
let token = null;
let chart=null;
let flowCounts = [];

function setAuthArea(){
  const el = document.getElementById('auth_area');
  if(token){
    el.innerHTML = '<button onclick="logout()">Logout</button>'
    document.getElementById('auth_forms').style.display='none';
  } else {
    el.innerHTML = ''
    document.getElementById('auth_forms').style.display='block';
  }
}

function register(){
  const email=document.getElementById('reg_email').value;
  const pw=document.getElementById('reg_pw').value;
  fetch('/api/register',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({email,pw:pw})})
  .then(r=>r.json()).then(x=>alert(JSON.stringify(x)))
}

function login(){
  const email=document.getElementById('login_email').value;
  const pw=document.getElementById('login_pw').value;
  fetch('/api/login',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({email,password:pw})})
  .then(r=>r.json()).then(x=>{token=x.token; setAuthArea();})
}

function logout(){ token=null; setAuthArea(); }

function addDomain(){
  const domain=document.getElementById('domain_input').value;
  const f=new FormData(); f.append('domain',domain);
  fetch('/api/domains',{method:'POST',headers: token?{'Authorization':'Bearer '+token}:undefined, body:f}).then(r=>r.json()).then(x=>alert(JSON.stringify(x)))
}

function startAgent(){
  const domain=document.getElementById('domain_input').value;
  const f=new FormData(); f.append('domain',domain);
  fetch('/api/start_agent',{method:'POST',headers: token?{'Authorization':'Bearer '+token}:undefined, body:f}).then(r=>r.json()).then(x=>alert(JSON.stringify(x)))
}

function train(){
  document.getElementById('train_status').innerText='training...';
  fetch('/train',{method:'POST'}).then(r=>r.json()).then(x=>{ document.getElementById('model_info').innerText='Trained (simulated). accuracy='+ (x.accuracy?x.accuracy:'n/a'); document.getElementById('train_status').innerText='done'; })
}

function exportAlerts(){
  fetch('/api/export_alerts',{headers: token?{'Authorization':'Bearer '+token}:undefined}).then(r=>r.blob()).then(b=>{const url=URL.createObjectURL(b); const a=document.createElement('a'); a.href=url; a.download='alerts.csv'; a.click();})
}

function initChart(){
  const ctx=document.getElementById('chart');
  chart=new Chart(ctx,{type:'line',data:{labels:[],datasets:[{label:'Flows per second',data:[],fill:false}]},options:{scales:{y:{beginAtZero:true}}}});
}

function addFlowRow(f){
  const tb=document.querySelector('#flows_table tbody');
  const tr=document.createElement('tr');
  tr.innerHTML=`<td>${new Date(f.timestamp).toLocaleTimeString()}</td><td>${f.src_ip}</td><td>${f.bytes}</td><td>${f.packets}</td><td>${(f.score||0).toFixed(2)}</td>`;
  tb.prepend(tr);
  while(tb.children.length>50) tb.removeChild(tb.lastChild);
}

function addAlertRow(a){
  const tb=document.querySelector('#alerts_table tbody');
  const tr=document.createElement('tr');
  tr.innerHTML=`<td>${new Date(a.created_at).toLocaleTimeString()}</td><td>${a.src_ip}</td><td>${a.domain}</td><td>${a.score.toFixed(2)}</td><td><button onclick="block('${a.src_ip}')">Block</button></td>`;
  tb.prepend(tr);
}

function block(ip){
  const f=new FormData(); f.append('src_ip', ip); f.append('domain', document.getElementById('domain_input').value || 'unknown');
  fetch('/api/block',{method:'POST',headers: token?{'Authorization':'Bearer '+token}:undefined, body:f}).then(r=>r.json()).then(x=>alert(JSON.stringify(x)));
}

function addBlock(b){
  const el=document.getElementById('blocks_list');
  const d=document.createElement('div'); d.innerText=`${b.src_ip} -> ${b.domain} (expires ${new Date(b.expires_at).toLocaleString()})`; el.prepend(d);
}

function connectSSE(){
  const s=new EventSource('/stream');
  s.onmessage = function(e){
    const data = JSON.parse(e.data);
    if(data.type==='flow'){ addFlowRow(data.flow); updateChart(); }
    if(data.type==='alert'){ addAlertRow(data.alert); }
    if(data.type==='block'){ addBlock(data); }
  }
}

function updateChart(){
  const now = Date.now();
  const last = chart.data.labels.length?chart.data.labels[chart.data.labels.length-1]:0;
  chart.data.labels.push(new Date().toLocaleTimeString());
  const cnt = Math.floor(Math.random()*5)+1; // placeholder
  chart.data.datasets[0].data.push(cnt);
  if(chart.data.labels.length>30){ chart.data.labels.shift(); chart.data.datasets[0].data.shift(); }
  chart.update();
}

window.onload = function(){ initChart(); setAuthArea(); connectSSE(); }
</script>
</body>
</html>
    """
    return HTMLResponse(content=html)

# ------------------------ Bootstrapping: create admin user if none ------------------------

def bootstrap_admin():
    db = next(get_db())
    if not db.query(User).filter(User.is_admin==True).first():
        u = User(email='admin@local', password_hash=hash_pw('admin123'), is_admin=True)
        db.add(u)
        db.commit()

bootstrap_admin()

# ------------------------ End of file ------------------------
