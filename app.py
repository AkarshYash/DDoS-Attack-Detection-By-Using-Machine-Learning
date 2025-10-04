import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
import json
from streamlit_option_menu import option_menu
from streamlit_chat import message
import numpy as np

# Import custom modules
from auth import AuthManager
from ml_engine import MLEngine
from database import DatabaseManager
from chatbot import ShieldAIChatbot
from dashboard_components import DashboardComponents
from admin_panel import AdminPanel
from utils import ThemeManager, AlertSystem

# Page configuration
st.set_page_config(
    page_title="Shield-AI | DDoS Protection Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'organization' not in st.session_state:
    st.session_state.organization = None
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'show_chat' not in st.session_state:
    st.session_state.show_chat = False

# Initialize components
auth_manager = AuthManager()
ml_engine = MLEngine()
db_manager = DatabaseManager()
chatbot = ShieldAIChatbot()
dashboard = DashboardComponents()
admin_panel = AdminPanel()
theme_manager = ThemeManager()
alert_system = AlertSystem()

def main():
    # Apply theme
    theme_manager.apply_theme(st.session_state.theme)
    
    # Custom CSS for better UI
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #00ff88;
        margin: 0.5rem 0;
    }
    .threat-high { border-left-color: #ff4444; }
    .threat-medium { border-left-color: #ffaa00; }
    .threat-low { border-left-color: #00ff88; }
    .chat-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 350px;
        height: 500px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 1000;
        display: flex;
        flex-direction: column;
    }
    .chat-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 15px;
        border-radius: 15px 15px 0 0;
        font-weight: bold;
    }
    .chat-toggle {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        z-index: 999;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ Shield-AI | Enterprise DDoS Protection Platform</h1>
        <p>AI-Powered Network Security & Threat Detection</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication check
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_application()
    
    # Chat toggle button and container
    show_chat_interface()

def show_login_page():
    st.markdown("## 🔐 Authentication")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.markdown("### Sign In to Shield-AI")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("Username/Email", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔑 Sign In", use_container_width=True):
                    if auth_manager.authenticate(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_role = auth_manager.get_user_role(username)
                        st.session_state.organization = auth_manager.get_user_org(username)
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            
            with col_b:
                if st.button("🌐 OAuth Login", use_container_width=True):
                    # Simulate OAuth login
                    st.session_state.authenticated = True
                    st.session_state.username = "demo_user"
                    st.session_state.user_role = "admin"
                    st.session_state.organization = "Demo Corp"
                    st.success("OAuth login successful!")
                    time.sleep(1)
                    st.rerun()
    
    with tab2:
        st.markdown("### Register New Account")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            reg_type = st.selectbox(
                "Registration Type",
                ["Personal Use", "Register Organization", "Employee Registration"]
            )
            
            reg_username = st.text_input("Username", key="reg_username")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            
            if reg_type == "Register Organization":
                org_name = st.text_input("Organization Name")
                org_domain = st.text_input("Primary Domain")
            elif reg_type == "Employee Registration":
                org_code = st.text_input("Organization Code")
                employee_id = st.text_input("Employee ID")
            
            if st.button("📝 Register", use_container_width=True):
                if auth_manager.register_user(reg_username, reg_email, reg_password, reg_type):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Registration failed. Username may already exist.")

def show_main_application():
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.username}")
        st.markdown(f"**Role:** {st.session_state.user_role.title()}")
        st.markdown(f"**Organization:** {st.session_state.organization}")
        
        # Theme toggle
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌙" if st.session_state.theme == 'light' else "☀️"):
                st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
                st.rerun()
        with col2:
            if st.button("🚪 Logout"):
                st.session_state.authenticated = False
                st.session_state.user_role = None
                st.session_state.username = None
                st.rerun()
        
        st.markdown("---")
        
        # Navigation menu based on role
        if st.session_state.user_role == "admin":
            selected = option_menu(
                "Navigation",
                ["Dashboard", "Traffic Analysis", "Threat Detection", "IP Management", "Admin Panel", "Reports", "Settings"],
                icons=['speedometer2', 'graph-up', 'shield-exclamation', 'ban', 'gear', 'file-text', 'sliders'],
                menu_icon="list",
                default_index=0,
            )
        else:
            selected = option_menu(
                "Navigation",
                ["Dashboard", "Traffic Analysis", "Threat Detection", "IP Management", "Reports", "Settings"],
                icons=['speedometer2', 'graph-up', 'shield-exclamation', 'ban', 'file-text', 'sliders'],
                menu_icon="list",
                default_index=0,
            )
    
    # Main content area
    if selected == "Dashboard":
        show_dashboard()
    elif selected == "Traffic Analysis":
        show_traffic_analysis()
    elif selected == "Threat Detection":
        show_threat_detection()
    elif selected == "IP Management":
        show_ip_management()
    elif selected == "Admin Panel" and st.session_state.user_role == "admin":
        show_admin_panel()
    elif selected == "Reports":
        show_reports()
    elif selected == "Settings":
        show_settings()

def show_dashboard():
    st.markdown("## 📊 Real-Time Security Dashboard")
    
    # Real-time metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Generate real-time data
    current_time = datetime.now()
    traffic_data = dashboard.generate_traffic_data()
    threat_score = ml_engine.calculate_threat_score(traffic_data)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🚦 Traffic Status</h3>
            <h2 style="color: #00ff88;">NORMAL</h2>
            <p>1,247 req/sec</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        threat_class = "threat-high" if threat_score > 0.7 else "threat-medium" if threat_score > 0.4 else "threat-low"
        st.markdown(f"""
        <div class="metric-card {threat_class}">
            <h3>⚠️ Threat Level</h3>
            <h2>{threat_score:.1%}</h2>
            <p>ML Confidence</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🚫 Blocked IPs</h3>
            <h2 style="color: #ff4444;">23</h2>
            <p>Last 24h</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🌍 Countries</h3>
            <h2 style="color: #ffaa00;">45</h2>
            <p>Traffic Sources</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Real-time charts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 Traffic Flow (Real-Time)")
        chart_data = dashboard.generate_realtime_chart()
        fig = px.line(chart_data, x='time', y='requests', 
                     title="Requests per Second",
                     color_discrete_sequence=['#00ff88'])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white' if st.session_state.theme == 'dark' else 'black'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🌍 Traffic by Country")
        geo_data = dashboard.generate_geo_data()
        fig = px.pie(geo_data, values='requests', names='country',
                    color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white' if st.session_state.theme == 'dark' else 'black'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent alerts
    st.markdown("### 🚨 Recent Security Alerts")
    alerts_data = alert_system.get_recent_alerts()
    st.dataframe(alerts_data, use_container_width=True)

def show_traffic_analysis():
    st.markdown("## 🔍 Advanced Traffic Analysis")
    
    # Traffic analysis components will be implemented here
    dashboard.show_traffic_analysis()

def show_threat_detection():
    st.markdown("## 🛡️ ML-Powered Threat Detection")
    
    # ML threat detection interface
    ml_engine.show_detection_interface()

def show_ip_management():
    st.markdown("## 🚫 IP Address Management")
    
    # IP management interface
    dashboard.show_ip_management()

def show_admin_panel():
    st.markdown("## ⚙️ Administrative Panel")
    
    # Admin panel interface
    admin_panel.show_admin_interface()

def show_reports():
    st.markdown("## 📊 Reports & Analytics")
    
    # Reports interface
    dashboard.show_reports()

def show_settings():
    st.markdown("## ⚙️ Settings & Configuration")
    
    # Settings interface
    dashboard.show_settings()

def show_chat_interface():
    # Chat toggle button
    if not st.session_state.show_chat:
        if st.markdown("""
        <div class="chat-toggle" onclick="document.querySelector('[data-testid=\"stButton\"] button').click()">
            💬
        </div>
        """, unsafe_allow_html=True):
            pass
        
        # Hidden button to trigger chat
        if st.button("", key="chat_toggle", help="Open AI Assistant"):
            st.session_state.show_chat = True
            st.rerun()
    else:
        # Chat container
        with st.container():
            st.markdown("""
            <div class="chat-container">
                <div class="chat-header">
                    🤖 Shield-AI Assistant
                    <span style="float: right; cursor: pointer;" onclick="document.querySelector('[data-testid=\"stButton\"][title=\"Close Chat\"] button').click()">✕</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Chat interface
            chatbot.show_chat_interface()
            
            if st.button("✕", key="close_chat", help="Close Chat"):
                st.session_state.show_chat = False
                st.rerun()

if __name__ == "__main__":
    main()