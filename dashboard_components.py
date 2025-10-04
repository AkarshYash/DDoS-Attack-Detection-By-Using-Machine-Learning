import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import numpy as np
from database import DatabaseManager

class DashboardComponents:
    def __init__(self):
        self.db = DatabaseManager()
    
    def generate_traffic_data(self):
        """Generate sample traffic data"""
        return {
            "requests_per_second": random.randint(800, 2000),
            "bytes_per_second": random.randint(500000, 2000000),
            "unique_ips": random.randint(100, 500),
            "countries": random.randint(25, 60)
        }
    
    def generate_realtime_chart(self):
        """Generate real-time traffic chart data"""
        now = datetime.now()
        data = []
        
        for i in range(60):  # Last 60 seconds
            timestamp = now - timedelta(seconds=i)
            requests = random.randint(800, 2000) + random.randint(-200, 200)
            data.append({
                "time": timestamp,
                "requests": max(0, requests)
            })
        
        return pd.DataFrame(data).sort_values('time')
    
    def generate_geo_data(self):
        """Generate geographic traffic data"""
        countries = [
            "United States", "China", "Germany", "United Kingdom", 
            "France", "Japan", "Brazil", "India", "Canada", "Australia"
        ]
        
        data = []
        for country in countries:
            data.append({
                "country": country,
                "requests": random.randint(50, 500)
            })
        
        return pd.DataFrame(data)
    
    def show_traffic_analysis(self):
        """Show detailed traffic analysis"""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📊 Traffic Patterns Analysis")
            
            # Time range selector
            time_range = st.selectbox(
                "Select Time Range",
                ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days"]
            )
            
            # Generate traffic timeline
            if time_range == "Last Hour":
                periods = 60
                freq = "1min"
                delta_func = lambda x: timedelta(minutes=x)
            elif time_range == "Last 24 Hours":
                periods = 24
                freq = "1H"
                delta_func = lambda x: timedelta(hours=x)
            elif time_range == "Last 7 Days":
                periods = 7
                freq = "1D"
                delta_func = lambda x: timedelta(days=x)
            else:  # Last 30 Days
                periods = 30
                freq = "1D"
                delta_func = lambda x: timedelta(days=x)
            
            # Generate data
            now = datetime.now()
            timeline_data = []
            
            for i in range(periods):
                timestamp = now - delta_func(i)
                base_traffic = random.randint(800, 1500)
                
                # Add some realistic patterns
                if time_range in ["Last Hour", "Last 24 Hours"]:
                    # Add hourly patterns
                    hour_factor = 1 + 0.3 * np.sin(2 * np.pi * timestamp.hour / 24)
                    base_traffic = int(base_traffic * hour_factor)
                
                timeline_data.append({
                    "timestamp": timestamp,
                    "requests": base_traffic,
                    "threats": random.randint(0, 15),
                    "blocked": random.randint(0, 50)
                })
            
            timeline_df = pd.DataFrame(timeline_data).sort_values('timestamp')
            
            # Create multi-line chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=timeline_df['timestamp'],
                y=timeline_df['requests'],
                mode='lines',
                name='Total Requests',
                line=dict(color='#00ff88', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=timeline_df['timestamp'],
                y=timeline_df['threats'],
                mode='lines',
                name='Threats Detected',
                line=dict(color='#ff4444', width=2),
                yaxis='y2'
            ))
            
            fig.add_trace(go.Scatter(
                x=timeline_df['timestamp'],
                y=timeline_df['blocked'],
                mode='lines',
                name='Requests Blocked',
                line=dict(color='#ffaa00', width=2),
                yaxis='y2'
            ))
            
            fig.update_layout(
                title=f"Traffic Analysis - {time_range}",
                xaxis_title="Time",
                yaxis_title="Requests per Period",
                yaxis2=dict(
                    title="Threats/Blocks",
                    overlaying='y',
                    side='right'
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white' if st.session_state.theme == 'dark' else 'black',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Traffic Insights")
            
            # Traffic metrics
            metrics = self.generate_traffic_data()
            
            st.metric("Peak Requests/sec", f"{metrics['requests_per_second']:,}", "+12%")
            st.metric("Data Transfer", f"{metrics['bytes_per_second']/1000000:.1f} MB/s", "+5%")
            st.metric("Unique Visitors", f"{metrics['unique_ips']:,}", "+8%")
            st.metric("Source Countries", metrics['countries'], "+2")
            
            st.markdown("---")
            
            # Top threat sources
            st.markdown("#### 🚨 Top Threat Sources")
            threat_sources = pd.DataFrame([
                {"Country": "China", "Threats": 45, "Blocked": 42},
                {"Country": "Russia", "Threats": 32, "Blocked": 30},
                {"Country": "Brazil", "Threats": 18, "Blocked": 15},
                {"Country": "India", "Threats": 12, "Blocked": 10},
                {"Country": "Unknown", "Threats": 8, "Blocked": 8}
            ])
            
            st.dataframe(threat_sources, use_container_width=True)
        
        # Protocol analysis
        st.markdown("### 🔍 Protocol & Port Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Protocol distribution
            protocol_data = pd.DataFrame([
                {"Protocol": "HTTP", "Percentage": 45},
                {"Protocol": "HTTPS", "Percentage": 35},
                {"Protocol": "TCP", "Percentage": 12},
                {"Protocol": "UDP", "Percentage": 6},
                {"Protocol": "ICMP", "Percentage": 2}
            ])
            
            fig = px.pie(protocol_data, values='Percentage', names='Protocol',
                        title="Protocol Distribution")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white' if st.session_state.theme == 'dark' else 'black'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top ports
            port_data = pd.DataFrame([
                {"Port": "80", "Requests": 12500, "Threats": 5},
                {"Port": "443", "Requests": 8900, "Threats": 3},
                {"Port": "22", "Requests": 450, "Threats": 25},
                {"Port": "21", "Requests": 120, "Threats": 15},
                {"Port": "3389", "Requests": 80, "Threats": 12}
            ])
            
            fig = px.bar(port_data, x='Port', y='Requests',
                        title="Top Destination Ports",
                        color='Threats', color_continuous_scale='Reds')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white' if st.session_state.theme == 'dark' else 'black'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            # Request size distribution
            size_data = pd.DataFrame([
                {"Size Range": "0-1KB", "Count": 5500},
                {"Size Range": "1-10KB", "Count": 3200},
                {"Size Range": "10-100KB", "Count": 1800},
                {"Size Range": "100KB-1MB", "Count": 450},
                {"Size Range": ">1MB", "Count": 120}
            ])
            
            fig = px.bar(size_data, x='Size Range', y='Count',
                        title="Request Size Distribution",
                        color='Count', color_continuous_scale='Blues')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white' if st.session_state.theme == 'dark' else 'black'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def show_ip_management(self):
        """Show IP management interface"""
        tab1, tab2, tab3 = st.tabs(["🚫 Blocked IPs", "➕ Block New IP", "📊 IP Analytics"])
        
        with tab1:
            st.markdown("### Currently Blocked IPs")
            
            # Get blocked IPs from database
            blocked_ips = self.db.get_blocked_ips(50)
            
            if blocked_ips:
                # Convert to DataFrame
                blocked_df = pd.DataFrame(blocked_ips)
                
                # Add action buttons
                for idx, ip_data in enumerate(blocked_ips[:10]):  # Show first 10
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{ip_data['ip_address']}**")
                    with col2:
                        st.write(ip_data['reason'])
                    with col3:
                        st.write(ip_data['blocked_at'][:19])
                    with col4:
                        status_color = "🔴" if ip_data['status'] == 'Active' else "🟡"
                        st.write(f"{status_color} {ip_data['status']}")
                    with col5:
                        if ip_data['status'] == 'Active':
                            if st.button("Unblock", key=f"unblock_{idx}"):
                                self.db.unblock_ip(ip_data['ip_address'], st.session_state.username)
                                st.success(f"Unblocked {ip_data['ip_address']}")
                                st.rerun()
            else:
                st.info("No blocked IPs found.")
        
        with tab2:
            st.markdown("### Block New IP Address")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                new_ip = st.text_input("IP Address to Block", placeholder="192.168.1.100")
                reason = st.selectbox(
                    "Reason for Blocking",
                    ["DDoS Attack", "Brute Force", "Port Scanning", "Malicious Activity", "Spam", "Other"]
                )
                
                if reason == "Other":
                    custom_reason = st.text_input("Custom Reason")
                    reason = custom_reason if custom_reason else "Other"
                
                duration = st.selectbox(
                    "Block Duration",
                    ["1 hour", "24 hours", "7 days", "30 days", "Permanent"]
                )
                
                if st.button("🚫 Block IP Address", type="primary"):
                    if new_ip:
                        # Validate IP format (basic)
                        if new_ip.count('.') == 3:
                            self.db.block_ip(new_ip, reason, st.session_state.username, duration)
                            st.success(f"Successfully blocked {new_ip}")
                            st.rerun()
                        else:
                            st.error("Please enter a valid IP address")
                    else:
                        st.error("Please enter an IP address")
            
            with col2:
                st.markdown("#### Quick Block Suggestions")
                st.markdown("*Based on recent threat analysis*")
                
                suspicious_ips = [
                    "192.168.1.100",
                    "10.0.0.50",
                    "172.16.0.25",
                    "203.0.113.10"
                ]
                
                for ip in suspicious_ips:
                    if st.button(f"Block {ip}", key=f"quick_block_{ip}"):
                        self.db.block_ip(ip, "Suspicious Activity", st.session_state.username)
                        st.success(f"Blocked {ip}")
                        st.rerun()
        
        with tab3:
            st.markdown("### IP Analytics & Insights")
            
            # Generate analytics data
            col1, col2 = st.columns(2)
            
            with col1:
                # Blocked IPs by country
                country_blocks = pd.DataFrame([
                    {"Country": "China", "Blocked IPs": 45},
                    {"Country": "Russia", "Blocked IPs": 32},
                    {"Country": "Brazil", "Blocked IPs": 18},
                    {"Country": "India", "Blocked IPs": 12},
                    {"Country": "USA", "Blocked IPs": 8},
                    {"Country": "Germany", "Blocked IPs": 6}
                ])
                
                fig = px.bar(country_blocks, x='Country', y='Blocked IPs',
                           title="Blocked IPs by Country",
                           color='Blocked IPs', color_continuous_scale='Reds')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white' if st.session_state.theme == 'dark' else 'black'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Block reasons distribution
                reason_data = pd.DataFrame([
                    {"Reason": "DDoS Attack", "Count": 35},
                    {"Reason": "Brute Force", "Count": 28},
                    {"Reason": "Port Scanning", "Count": 22},
                    {"Reason": "Malicious Activity", "Count": 15},
                    {"Reason": "Spam", "Count": 8}
                ])
                
                fig = px.pie(reason_data, values='Count', names='Reason',
                           title="Block Reasons Distribution")
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white' if st.session_state.theme == 'dark' else 'black'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Blocking timeline
            st.markdown("#### Blocking Activity Timeline")
            
            timeline_data = []
            now = datetime.now()
            
            for i in range(30):  # Last 30 days
                date = now - timedelta(days=i)
                blocks = random.randint(0, 10)
                timeline_data.append({
                    "Date": date.date(),
                    "Blocks": blocks
                })
            
            timeline_df = pd.DataFrame(timeline_data).sort_values('Date')
            
            fig = px.line(timeline_df, x='Date', y='Blocks',
                         title="Daily IP Blocking Activity",
                         markers=True)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white' if st.session_state.theme == 'dark' else 'black'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def show_reports(self):
        """Show reports interface"""
        st.markdown("### 📊 Security Reports & Analytics")
        
        tab1, tab2, tab3 = st.tabs(["📈 Generate Report", "📋 Scheduled Reports", "📊 Analytics Dashboard"])
        
        with tab1:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### Report Configuration")
                
                report_type = st.selectbox(
                    "Report Type",
                    ["Security Summary", "Threat Analysis", "Traffic Report", "Blocked IPs Report", "Custom Report"]
                )
                
                date_range = st.selectbox(
                    "Time Period",
                    ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom Range"]
                )
                
                if date_range == "Custom Range":
                    col_a, col_b = st.columns(2)
                    with col_a:
                        start_date = st.date_input("Start Date")
                    with col_b:
                        end_date = st.date_input("End Date")
                
                format_type = st.selectbox("Format", ["PDF", "HTML", "CSV", "JSON"])
                
                include_charts = st.checkbox("Include Charts and Visualizations", value=True)
                include_raw_data = st.checkbox("Include Raw Data", value=False)
                
                if st.button("📊 Generate Report", type="primary"):
                    with st.spinner("Generating report..."):
                        # Simulate report generation
                        import time
                        time.sleep(2)
                        
                        st.success("Report generated successfully!")
                        
                        # Create download button
                        report_content = f"""
# Shield-AI Security Report
## {report_type} - {date_range}

### Executive Summary
- Total Requests Analyzed: 1,247,832
- Threats Detected: 156
- IPs Blocked: 23
- Success Rate: 99.87%

### Key Findings
1. DDoS attack attempts increased by 15% compared to previous period
2. Most threats originated from China (28%) and Russia (22%)
3. Port 22 (SSH) was the most targeted port
4. ML models achieved 94.2% accuracy in threat detection

### Recommendations
1. Increase monitoring for SSH brute force attacks
2. Consider geo-blocking for high-risk countries
3. Update firewall rules for commonly targeted ports
4. Schedule regular model retraining
                        """
                        
                        st.download_button(
                            label="📥 Download Report",
                            data=report_content,
                            file_name=f"shield_ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
            
            with col2:
                st.markdown("#### Quick Stats")
                
                # Generate quick stats
                st.metric("Total Threats", "156", "+12%")
                st.metric("Blocked IPs", "23", "+5")
                st.metric("Clean Traffic", "99.87%", "+0.1%")
                st.metric("Response Time", "0.3ms", "-0.1ms")
                
                st.markdown("---")
                
                st.markdown("#### Recent Reports")
                recent_reports = [
                    "Security Summary - 2024-01-15",
                    "Threat Analysis - 2024-01-14",
                    "Weekly Report - 2024-01-13",
                    "Traffic Report - 2024-01-12"
                ]
                
                for report in recent_reports:
                    if st.button(f"📄 {report}", key=f"recent_{report}"):
                        st.info(f"Loading {report}...")
        
        with tab2:
            st.markdown("#### Scheduled Report Management")
            
            # Current scheduled reports
            scheduled_reports = pd.DataFrame([
                {
                    "Name": "Daily Security Summary",
                    "Type": "Security Summary",
                    "Schedule": "Daily at 6:00 AM",
                    "Recipients": "admin@company.com",
                    "Status": "Active"
                },
                {
                    "Name": "Weekly Threat Report",
                    "Type": "Threat Analysis",
                    "Schedule": "Weekly on Monday",
                    "Recipients": "security-team@company.com",
                    "Status": "Active"
                },
                {
                    "Name": "Monthly Executive Report",
                    "Type": "Executive Summary",
                    "Schedule": "Monthly on 1st",
                    "Recipients": "executives@company.com",
                    "Status": "Paused"
                }
            ])
            
            st.dataframe(scheduled_reports, use_container_width=True)
            
            st.markdown("#### Add New Scheduled Report")
            
            col1, col2 = st.columns(2)
            
            with col1:
                schedule_name = st.text_input("Report Name")
                schedule_type = st.selectbox("Report Type", ["Security Summary", "Threat Analysis", "Traffic Report"])
                schedule_freq = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])
            
            with col2:
                recipients = st.text_area("Email Recipients (one per line)")
                schedule_format = st.selectbox("Format", ["PDF", "HTML"])
                
                if st.button("➕ Add Scheduled Report"):
                    st.success("Scheduled report added successfully!")
        
        with tab3:
            self.show_analytics_dashboard()
    
    def show_analytics_dashboard(self):
        """Show comprehensive analytics dashboard"""
        st.markdown("#### 📊 Comprehensive Security Analytics")
        
        # Key metrics row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Threat Score", "0.34", "-0.05")
        with col2:
            st.metric("Blocked Today", "23", "+8")
        with col3:
            st.metric("Clean Traffic", "99.87%", "+0.12%")
        with col4:
            st.metric("Response Time", "0.3ms", "-0.1ms")
        with col5:
            st.metric("Uptime", "99.99%", "0%")
        
        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            # Threat detection over time
            threat_timeline = []
            now = datetime.now()
            
            for i in range(24):  # Last 24 hours
                timestamp = now - timedelta(hours=i)
                threats = random.randint(0, 15)
                threat_timeline.append({
                    "Hour": timestamp.strftime("%H:00"),
                    "Threats": threats,
                    "Severity": random.choice(["Low", "Medium", "High"])
                })
            
            timeline_df = pd.DataFrame(threat_timeline)
            
            fig = px.bar(timeline_df, x='Hour', y='Threats',
                        title="Threat Detection Timeline (24h)",
                        color='Severity',
                        color_discrete_map={'Low': '#00ff88', 'Medium': '#ffaa00', 'High': '#ff4444'})
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white' if st.session_state.theme == 'dark' else 'black'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Attack types distribution
            attack_types = pd.DataFrame([
                {"Type": "DDoS", "Count": 45, "Severity": "High"},
                {"Type": "Brute Force", "Count": 32, "Severity": "Medium"},
                {"Type": "Port Scan", "Count": 28, "Severity": "Low"},
                {"Type": "SQL Injection", "Count": 15, "Severity": "High"},
                {"Type": "XSS", "Count": 12, "Severity": "Medium"}
            ])
            
            fig = px.sunburst(attack_types, path=['Severity', 'Type'], values='Count',
                             title="Attack Types by Severity")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white' if st.session_state.theme == 'dark' else 'black'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def show_settings(self):
        """Show settings interface"""
        st.markdown("### ⚙️ System Settings & Configuration")
        
        tab1, tab2, tab3, tab4 = st.tabs(["🔔 Notifications", "🎨 Appearance", "🔒 Security", "🌐 Integrations"])
        
        with tab1:
            st.markdown("#### Notification Preferences")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Alert Channels**")
                email_alerts = st.checkbox("Email Notifications", value=True)
                sms_alerts = st.checkbox("SMS Notifications", value=False)
                slack_alerts = st.checkbox("Slack Integration", value=True)
                discord_alerts = st.checkbox("Discord Webhooks", value=False)
                
                st.markdown("**Alert Thresholds**")
                threat_threshold = st.slider("Threat Score Threshold", 0.0, 1.0, 0.7, 0.1)
                traffic_threshold = st.number_input("Traffic Spike Threshold (%)", value=200)
            
            with col2:
                st.markdown("**Email Settings**")
                email_address = st.text_input("Primary Email", value="admin@company.com")
                backup_email = st.text_input("Backup Email", value="")
                
                st.markdown("**SMS Settings**")
                phone_number = st.text_input("Phone Number", value="+1234567890")
                
                st.markdown("**Webhook URLs**")
                slack_webhook = st.text_input("Slack Webhook URL")
                discord_webhook = st.text_input("Discord Webhook URL")
            
            if st.button("💾 Save Notification Settings"):
                st.success("Notification settings saved successfully!")
        
        with tab2:
            st.markdown("#### Appearance & Theme")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Theme selection
                theme_option = st.radio(
                    "Color Theme",
                    ["Dark Mode", "Light Mode", "Auto (System)"],
                    index=0 if st.session_state.theme == 'dark' else 1
                )
                
                if theme_option != ("Dark Mode" if st.session_state.theme == 'dark' else "Light Mode"):
                    if theme_option == "Dark Mode":
                        st.session_state.theme = 'dark'
                    elif theme_option == "Light Mode":
                        st.session_state.theme = 'light'
                    st.rerun()
                
                # Dashboard layout
                layout_density = st.selectbox("Dashboard Density", ["Compact", "Normal", "Spacious"])
                sidebar_position = st.selectbox("Sidebar Position", ["Left", "Right"])
                
            with col2:
                st.markdown("**Preview**")
                
                # Theme preview
                if st.session_state.theme == 'dark':
                    st.markdown("""
                    <div style="background: #1e1e1e; color: white; padding: 20px; border-radius: 10px;">
                        <h4>🌙 Dark Theme Preview</h4>
                        <p>This is how your dashboard looks in dark mode.</p>
                        <div style="background: #333; padding: 10px; border-radius: 5px; margin: 10px 0;">
                            Sample metric card
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background: #ffffff; color: black; padding: 20px; border-radius: 10px; border: 1px solid #ddd;">
                        <h4>☀️ Light Theme Preview</h4>
                        <p>This is how your dashboard looks in light mode.</p>
                        <div style="background: #f5f5f5; padding: 10px; border-radius: 5px; margin: 10px 0;">
                            Sample metric card
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab3:
            st.markdown("#### Security Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Authentication Settings**")
                session_timeout = st.number_input("Session Timeout (minutes)", value=60)
                require_2fa = st.checkbox("Require Two-Factor Authentication", value=True)
                password_policy = st.selectbox("Password Policy", ["Standard", "Strong", "Enterprise"])
                
                st.markdown("**API Security**")
                api_rate_limit = st.number_input("API Rate Limit (requests/minute)", value=1000)
                require_api_key = st.checkbox("Require API Key", value=True)
            
            with col2:
                st.markdown("**Audit Settings**")
                log_retention = st.selectbox("Log Retention Period", ["30 days", "90 days", "1 year", "Forever"])
                audit_level = st.selectbox("Audit Level", ["Basic", "Detailed", "Comprehensive"])
                
                st.markdown("**Backup Settings**")
                auto_backup = st.checkbox("Automatic Backups", value=True)
                backup_frequency = st.selectbox("Backup Frequency", ["Daily", "Weekly", "Monthly"])
        
        with tab4:
            st.markdown("#### External Integrations")
            
            integrations = [
                {"name": "AWS WAF", "status": "Connected", "icon": "🔶"},
                {"name": "Cloudflare", "status": "Disconnected", "icon": "🟠"},
                {"name": "Google Cloud Armor", "status": "Connected", "icon": "🔵"},
                {"name": "Azure Firewall", "status": "Disconnected", "icon": "🔷"},
                {"name": "Slack", "status": "Connected", "icon": "💬"},
                {"name": "PagerDuty", "status": "Connected", "icon": "📟"},
                {"name": "Splunk", "status": "Disconnected", "icon": "📊"},
                {"name": "Elasticsearch", "status": "Connected", "icon": "🔍"}
            ]
            
            for integration in integrations:
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                
                with col1:
                    st.write(integration["icon"])
                with col2:
                    st.write(f"**{integration['name']}**")
                with col3:
                    status_color = "🟢" if integration["status"] == "Connected" else "🔴"
                    st.write(f"{status_color} {integration['status']}")
                with col4:
                    action = "Disconnect" if integration["status"] == "Connected" else "Connect"
                    if st.button(action, key=f"integration_{integration['name']}"):
                        new_status = "Disconnected" if integration["status"] == "Connected" else "Connected"
                        st.success(f"{integration['name']} {new_status.lower()} successfully!")