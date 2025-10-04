# 🛡️ Shield-AI — Intelligent DDoS Detection & Defense Platform

**Built by:** [Akarsh — Cybersecurity & AI Developer](https://akarshyash.github.io/My_Digital-Card/)
**Tech Stack:** Python | FastAPI | Streamlit | LangChain | Gemini Pro | ML | JS | HTML | CSS | PostgreSQL | Redis | MinIO | Plotly | AG Grid

---

## ⚡ Overview

**Shield-AI** is an advanced, enterprise-grade **DDoS detection and defense platform** that leverages **Machine Learning, real-time data processing, and AI assistance** to monitor, detect, and mitigate distributed denial-of-service (DDoS) attacks — all within a powerful, interactive web dashboard.

It’s not just a security tool — it’s a **complete ecosystem for network protection**, combining automation, explainable AI, and intelligent chat-based security operations.

---

## 🎯 Key Highlights

✅ **AI-Powered Detection:** Uses Random Forest, XGBoost, and Isolation Forest models trained on the **CICDDoS2019** dataset for real-time classification.
✅ **Interactive Chatbot:** Built with **Google Gemini Pro + LangChain**, the chatbot acts as your security copilot — answering questions, explaining threats, and recommending defense actions.
✅ **Multi-Role Access:** Admins, Analysts, IT Teams, and Auditors get dedicated panels with RBAC (Role-Based Access Control).
✅ **Live Dashboard:** Monitor real-time traffic, requests/second, threat scores, and blocked IPs with Streamlit’s multipage interface.
✅ **Automated IP Blocking:** Auto-blocks malicious IPs using local agent or cloud firewall APIs (AWS WAF / Azure Defender).
✅ **Alert System:** WebSocket live alerts, plus Email, SMS, Slack, Discord, and PagerDuty integration.
✅ **Modern UI Themes:** Switch between **Dark** 🌑 and **Light** ☀️ modes dynamically.
✅ **Great UX:** Animated panels, responsive grids, and a **floating AI Assistant** popup (bottom-right) for quick help.
✅ **Enterprise Deployment:** Supports cloud + on-premises with containerized deployment using Docker / Kubernetes.

---

## 🧠 Machine Learning & Dataset

**Dataset Used:**

* **CICDDoS2019** — by the Canadian Institute for Cybersecurity
* Contains labeled normal and DDoS traffic samples from multiple attack types
* Used for feature extraction, training ML models, and testing real-time predictions

**ML Models Implemented:**

* **Random Forest** (Primary Classifier)
* **XGBoost** (Boosted Tree Ensemble for enhanced precision)
* **Isolation Forest** (Anomaly detection layer)

**Explainability:**

* Integrated with **SHAP** for model interpretation and transparent threat scoring.

**Pipeline:**

* Data Preprocessing → Feature Extraction → Model Training → Real-time Scoring → Threshold-based Mitigation

---

## 🧩 System Architecture

```text
                   ┌──────────────────────────┐
                   │     Shield-AI UI (Web)   │
                   │ Streamlit + HTML/CSS/JS  │
                   │ - Dashboard              │
                   │ - Reports                │
                   │ - Chat Assistant         │
                   └────────────┬─────────────┘
                                │
                ┌───────────────┴────────────────┐
                │         FastAPI Backend         │
                │ - Auth & Role Management        │
                │ - Domain Registration           │
                │ - ML Scoring API                │
                │ - Alerts & Reports              │
                └──────────────┬──────────────────┘
                               │
           ┌───────────────────┴────────────────────┐
           │              ML Engine                 │
           │ RandomForest | XGBoost | IsoForest     │
           │ - Live Traffic Scoring                 │
           │ - SHAP Explainability                  │
           └───────────────────┬────────────────────┘
                               │
         ┌─────────────────────┴────────────────────────┐
         │       Data Layer & Async Processing           │
         │ PostgreSQL / TimescaleDB  → Persistent Data   │
         │ Redis → Caching, Queues (Celery Tasks)        │
         │ S3/MinIO → PCAP & Reports Storage             │
         └───────────────────────────────────────────────┘
```

---

## 🧭 Workflow

1. **User Authentication:**

   * OAuth (Google, GitHub, Microsoft) or SMS-based login via Twilio.
   * JWT-secured sessions.

2. **Domain Setup:**

   * Register and verify your organization’s domain.
   * Deploy a lightweight agent or use the API key for flow collection.

3. **Traffic Monitoring:**

   * Packet/Flow data sent to backend via async queue.
   * Features extracted → ML model evaluates → Threat score assigned.

4. **Alert & Mitigation:**

   * If threshold exceeds danger level → Auto-block IP.
   * Alerts sent to user dashboard + email/SMS/Slack.

5. **AI Chat Assistant:**

   * Ask: “What’s the latest DDoS source country?” or “Explain this alert.”
   * Gemini Pro responds contextually using LangChain memory.

6. **Reporting:**

   * Generate/export PDF or HTML reports (daily/weekly).

---

## 💻 UI Features

| Section                 | Description                                                                    |
| ----------------------- | ------------------------------------------------------------------------------ |
| **Dashboard**           | Real-time traffic stats, charts, and live threat scores.                       |
| **Traffic Analytics**   | Country-level breakdowns, time series charts (Plotly/Altair).                  |
| **IP Management**       | Block/unblock IPs, view history, severity, and exceptions.                     |
| **Alerts Panel**        | WebSocket-powered live alerts with severity badges.                            |
| **Reports**             | Export to PDF/HTML or schedule via email/webhook.                              |
| **Settings**            | Theme switcher, alert channels, and schedule preferences.                      |
| **Admin Panel**         | Manage roles, audit logs, and organizational activity.                         |
| **Chatbot (Gemini AI)** | Floating pop-up bot (bottom-right) — “Need help?” UX with real-time responses. |

---

## ⚙️ Technologies Used

**Languages:** Python, JavaScript, HTML, CSS
**Frameworks & Libraries:**

* **Backend:** FastAPI, Celery, Redis, LangChain, Gemini API
* **Frontend:** Streamlit (Multipage), Plotly, Altair, AG Grid, JS Animations
* **Database:** PostgreSQL / TimescaleDB, Redis (cache), MinIO (storage)
* **Machine Learning:** Scikit-learn, XGBoost, SHAP
* **Authentication:** OAuthlib, Twilio Verify
* **Reports:** ReportLab / WeasyPrint
* **Containerization:** Docker, Kubernetes

---

## 🌗 UI & Theme

* Two main visual modes:

  * **Light Mode:** Professional analytics look (white + blue accent)
  * **Dark Mode:** Futuristic SOC theme (black + cyan accent)
* Responsive layout
* Animated charts & transitions
* Floating Gemini Chatbot pop with "Need Help?" trigger

---

## 🧩 Folder Structure (Final Modular Version)

```
Shield-AI/
│
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── api/
│   ├── ml_engine/
│   ├── utils/
│   └── database/
│
├── gui/
│   ├── app.py  (Streamlit main UI)
│   ├── components/
│   └── assets/  (CSS, JS, images)
│
├── models/
│   ├── rf_model.pkl
│   ├── xgb_model.pkl
│   └── iso_model.pkl
│
├── data/
│   └── CICDDoS2019/
│
└── reports/
    └── generated_reports/
```

---

## 🧠 AI Assistant (Gemini Pro + LangChain Integration)

The Shield-AI chatbot is built to be context-aware, assisting users with:

* Real-time threat summaries
* Attack explanations
* Report generation via command
* Auto-suggesting mitigations

It runs as a **floating interactive widget (bottom-right corner)** using Gemini Pro + LangChain memory stack.

---

## 🧪 Text & Tech Check

| Category         | Description                                         |
| ---------------- | --------------------------------------------------- |
| **Dataset**      | CICDDoS2019                                         |
| **ML Models**    | Random Forest, XGBoost, Isolation Forest            |
| **Frameworks**   | FastAPI, Streamlit, LangChain, Gemini               |
| **Theme System** | Dual (Dark/Light)                                   |
| **Storage**      | PostgreSQL, Redis, MinIO                            |
| **Deployment**   | Docker/Kubernetes ready                             |
| **UI Libraries** | Plotly, AG Grid, Tailwind CSS                       |
| **Chat System**  | Gemini Pro with Context Memory                      |
| **Security**     | JWT Auth, Role-Based Access, SSL, API Rate Limiting |

---

## 🎥 Demo Videos

> 💡 Hidden UI Demos (with different design styles) are attached inside `/demo_videos/` folder.
> These showcase:
>
> * Version 1: Classic SOC Dark Mode
https://github.com/user-attachments/assets/a1c63894-8ba1-4814-b704-3ffaff7d79cc

> * Version 2: Futuristic Light Mode with Gradient UI
https://github.com/user-attachments/assets/1afda0e6-ac2a-4f54-b71e-490400faae8d

> * Version 3: Minimal Flat Design

---

## 🚀 Future Enhancements

* 🧩 Deep Learning (LSTM/Transformer) for behavioral analysis
* 🧠 Real-time anomaly clustering
* ☁️ Cloud Firewall integration (AWS / GCP / Azure)
* 🔐 SOC Dashboard for multiple organizations
* 🤖 Voice-based AI Assistant using Gemini + gTTS

---

## 💬 Contribution

Want to collaborate or contribute to Shield-AI?

1. Fork the repo
2. Create a feature branch
3. Submit a pull request

---

## 🧾 License

MIT License © 2025 [ Akars Chaturvedi]

---

## 🌐 Connect with Developer

**Website:** [My Digital Card](https://akarshyash.github.io/My_Digital-Card/)
**GitHub:** [@AkarshYash](https://github.com/AkarshYash)
**LinkedIn:** [Kalki Akarsh](https://linkedin.com/in/akarshyash)

