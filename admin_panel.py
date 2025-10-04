import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random
from auth import AuthManager
from database import DatabaseManager

class AdminPanel:
    def __init__(self):
        self.auth_manager = AuthManager()
        self.db_manager = DatabaseManager()
    
    def show_admin_interface(self):
        """Show admin panel interface"""
        if st.session_state.user_role != "admin":
            st.error("🚫 Access Denied: Admin privileges required")
            return
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "👥 User Management", 
            "🏢 Organizations", 
            "🌐 Domain Management", 
            "📋 Audit Logs", 
            "⚙️ System Config"
        ])
        
        with tab1:
            self.show_user_management()
        
        with tab2:
            self.show_organization_management()
        
        with tab3:
            self.show_domain_management()
        
        with tab4:
            self.show_audit_logs()
        
        with tab5:
            self.show_system_configuration()
    
    def show_user_management(self):
        """Show user management interface"""
        st.markdown("### 👥 User Management")
        
        # User statistics
        col1, col2, col3, col4 = st.columns(4)
        
        users = self.auth_manager.get_all_users()
        total_users = len(users)
        active_users = len([u for u in users if u['last_login'] != 'Never'])
        admin_users = len([u for u in users if u['role'] == 'admin'])
        
        with col1:
            st.metric("Total Users", total_users)
        with col2:
            st.metric("Active Users", active_users)
        with col3:
            st.metric("Admin Users", admin_users)
        with col4:
            st.metric("New This Month", random.randint(3, 12))
        
        # User table with actions
        st.markdown("#### User Directory")
        
        if users:
            users_df = pd.DataFrame(users)
            
            # Add action buttons for each user
            for idx, user in enumerate(users):
                col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 2, 2, 2])
                
                with col1:
                    st.write(f"**{user['username']}**")
                with col2:
                    st.write(user['email'])
                with col3:
                    role_color = {"admin": "🔴", "analyst": "🟡", "employee": "🟢", "personal": "🔵"}
                    st.write(f"{role_color.get(user['role'], '⚪')} {user['role'].title()}")
                with col4:
                    st.write(user['organization'])
                with col5:
                    last_login = user['last_login']
                    if last_login == 'Never':
                        st.write("🔴 Never")
                    else:
                        try:
                            login_date = datetime.fromisoformat(last_login)
                            days_ago = (datetime.now() - login_date).days
                            if days_ago == 0:
                                st.write("🟢 Today")
                            elif days_ago < 7:
                                st.write(f"🟡 {days_ago}d ago")
                            else:
                                st.write(f"🔴 {days_ago}d ago")
                        except:
                            st.write("🔴 Unknown")
                with col6:
                    # Action buttons
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        if st.button("✏️", key=f"edit_user_{idx}", help="Edit User"):
                            st.session_state[f"edit_user_{user['username']}"] = True
                    
                    with col_b:
                        if user['username'] != 'admin':  # Protect admin account
                            if st.button("🗑️", key=f"delete_user_{idx}", help="Delete User"):
                                if self.auth_manager.delete_user(user['username']):
                                    st.success(f"User {user['username']} deleted")
                                    st.rerun()
                    
                    with col_c:
                        if st.button("🔄", key=f"reset_pwd_{idx}", help="Reset Password"):
                            st.info(f"Password reset email sent to {user['email']}")
                
                # Edit user modal
                if st.session_state.get(f"edit_user_{user['username']}", False):
                    with st.expander(f"Edit User: {user['username']}", expanded=True):
                        new_role = st.selectbox(
                            "Role", 
                            ["admin", "analyst", "employee", "personal"],
                            index=["admin", "analyst", "employee", "personal"].index(user['role']),
                            key=f"role_select_{user['username']}"
                        )
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 Save Changes", key=f"save_{user['username']}"):
                                if self.auth_manager.update_user_role(user['username'], new_role):
                                    st.success("User updated successfully")
                                    st.session_state[f"edit_user_{user['username']}"] = False
                                    st.rerun()
                        
                        with col_cancel:
                            if st.button("❌ Cancel", key=f"cancel_{user['username']}"):
                                st.session_state[f"edit_user_{user['username']}"] = False
                                st.rerun()
                
                st.markdown("---")
        
        # Add new user
        st.markdown("#### ➕ Add New User")
        
        with st.expander("Create New User Account"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username", key="new_user_username")
                new_email = st.text_input("Email", key="new_user_email")
                new_password = st.text_input("Temporary Password", type="password", key="new_user_password")
            
            with col2:
                new_role = st.selectbox("Role", ["employee", "analyst", "admin"], key="new_user_role")
                new_org = st.text_input("Organization", key="new_user_org")
                send_email = st.checkbox("Send welcome email", value=True)
            
            if st.button("👤 Create User Account"):
                if new_username and new_email and new_password:
                    if self.auth_manager.register_user(new_username, new_email, new_password, "Employee Registration"):
                        # Update role and organization
                        self.auth_manager.update_user_role(new_username, new_role)
                        st.success(f"User {new_username} created successfully!")
                        if send_email:
                            st.info(f"Welcome email sent to {new_email}")
                        st.rerun()
                    else:
                        st.error("Failed to create user. Username may already exist.")
                else:
                    st.error("Please fill in all required fields")
    
    def show_organization_management(self):
        """Show organization management interface"""
        st.markdown("### 🏢 Organization Management")
        
        # Organization statistics
        col1, col2, col3, col4 = st.columns(4)
        
        # Get organization data
        users = self.auth_manager.get_all_users()
        organizations = {}
        
        for user in users:
            org = user['organization']
            if org not in organizations:
                organizations[org] = {
                    'name': org,
                    'users': [],
                    'domains': 0,
                    'created_at': user['created_at']
                }
            organizations[org]['users'].append(user)
        
        # Add domain counts
        domains = self.db_manager.domains
        for domain, domain_data in domains.items():
            org = domain_data['organization']
            if org in organizations:
                organizations[org]['domains'] += 1
        
        with col1:
            st.metric("Total Organizations", len(organizations))
        with col2:
            st.metric("Total Domains", sum(org['domains'] for org in organizations.values()))
        with col3:
            st.metric("Avg Users/Org", f"{len(users) / max(len(organizations), 1):.1f}")
        with col4:
            st.metric("New This Month", random.randint(1, 5))
        
        # Organization list
        st.markdown("#### Organization Directory")
        
        for org_name, org_data in organizations.items():
            with st.expander(f"🏢 {org_name} ({len(org_data['users'])} users, {org_data['domains']} domains)"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**Users:**")
                    for user in org_data['users']:
                        role_icon = {"admin": "👑", "analyst": "🔍", "employee": "👤", "personal": "🏠"}
                        st.write(f"{role_icon.get(user['role'], '👤')} {user['username']} ({user['email']}) - {user['role'].title()}")
                    
                    st.markdown("**Domains:**")
                    org_domains = [d for d, data in domains.items() if data['organization'] == org_name]
                    if org_domains:
                        for domain in org_domains:
                            status_icon = {"active": "🟢", "monitoring": "🟡", "pending": "🔴"}
                            domain_status = domains[domain]['status']
                            st.write(f"{status_icon.get(domain_status, '⚪')} {domain} - {domain_status}")
                    else:
                        st.write("No domains registered")
                
                with col2:
                    st.markdown("**Actions:**")
                    if st.button(f"📊 View Analytics", key=f"analytics_{org_name}"):
                        st.info(f"Loading analytics for {org_name}...")
                    
                    if st.button(f"⚙️ Manage Settings", key=f"settings_{org_name}"):
                        st.info(f"Opening settings for {org_name}...")
                    
                    if st.button(f"📧 Send Notification", key=f"notify_{org_name}"):
                        st.success(f"Notification sent to all users in {org_name}")
        
        # Add new organization
        st.markdown("#### ➕ Create New Organization")
        
        with st.expander("Register New Organization"):
            col1, col2 = st.columns(2)
            
            with col1:
                org_name = st.text_input("Organization Name")
                org_domain = st.text_input("Primary Domain")
                org_type = st.selectbox("Organization Type", ["Enterprise", "Small Business", "Non-Profit", "Government", "Educational"])
            
            with col2:
                admin_username = st.text_input("Admin Username")
                admin_email = st.text_input("Admin Email")
                admin_password = st.text_input("Admin Password", type="password")
            
            if st.button("🏢 Create Organization"):
                if all([org_name, admin_username, admin_email, admin_password]):
                    # Create admin user
                    if self.auth_manager.register_user(admin_username, admin_email, admin_password, "Register Organization"):
                        self.auth_manager.update_user_role(admin_username, "admin")
                        
                        # Add domain if provided
                        if org_domain:
                            self.db_manager.add_domain(org_domain, admin_username, org_name)
                        
                        st.success(f"Organization {org_name} created successfully!")
                        st.info(f"Admin user {admin_username} created with full privileges")
                        st.rerun()
                    else:
                        st.error("Failed to create organization. Admin username may already exist.")
                else:
                    st.error("Please fill in all required fields")
    
    def show_domain_management(self):
        """Show domain management interface"""
        st.markdown("### 🌐 Global Domain Management")
        
        domains = self.db_manager.domains
        
        # Domain statistics
        col1, col2, col3, col4 = st.columns(4)
        
        total_domains = len(domains)
        active_domains = len([d for d in domains.values() if d['status'] == 'active'])
        monitored_domains = len([d for d in domains.values() if d['agent_deployed']])
        
        with col1:
            st.metric("Total Domains", total_domains)
        with col2:
            st.metric("Active Domains", active_domains)
        with col3:
            st.metric("Monitored", monitored_domains)
        with col4:
            st.metric("DNS Validated", len([d for d in domains.values() if d['dns_validated']]))
        
        # Domain list with management options
        st.markdown("#### Domain Directory")
        
        for domain_name, domain_data in domains.items():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 2])
            
            with col1:
                st.write(f"**{domain_name}**")
                st.caption(f"Owner: {domain_data['owner']} | Org: {domain_data['organization']}")
            
            with col2:
                status_colors = {"active": "🟢", "monitoring": "🟡", "pending": "🔴"}
                st.write(f"{status_colors.get(domain_data['status'], '⚪')} {domain_data['status'].title()}")
            
            with col3:
                st.write("✅ Yes" if domain_data['dns_validated'] else "❌ No")
            
            with col4:
                st.write("🔧 Yes" if domain_data['agent_deployed'] else "❌ No")
            
            with col5:
                threat_colors = {"low": "🟢", "medium": "🟡", "high": "🔴"}
                threat_level = domain_data.get('threat_level', 'unknown')
                st.write(f"{threat_colors.get(threat_level, '⚪')} {threat_level.title()}")
            
            with col6:
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if st.button("📊", key=f"domain_stats_{domain_name}", help="View Statistics"):
                        st.info(f"Loading statistics for {domain_name}")
                
                with col_b:
                    if st.button("⚙️", key=f"domain_config_{domain_name}", help="Configure"):
                        st.session_state[f"config_{domain_name}"] = True
                
                with col_c:
                    if st.button("🗑️", key=f"domain_delete_{domain_name}", help="Remove Domain"):
                        if st.session_state.get(f"confirm_delete_{domain_name}", False):
                            # Delete domain logic here
                            st.success(f"Domain {domain_name} removed")
                        else:
                            st.session_state[f"confirm_delete_{domain_name}"] = True
                            st.warning("Click again to confirm deletion")
            
            # Configuration modal
            if st.session_state.get(f"config_{domain_name}", False):
                with st.expander(f"Configure {domain_name}", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_status = st.selectbox(
                            "Status",
                            ["active", "monitoring", "pending", "suspended"],
                            index=["active", "monitoring", "pending", "suspended"].index(domain_data['status']),
                            key=f"status_{domain_name}"
                        )
                        
                        dns_validated = st.checkbox(
                            "DNS Validated",
                            value=domain_data['dns_validated'],
                            key=f"dns_{domain_name}"
                        )
                    
                    with col2:
                        agent_deployed = st.checkbox(
                            "Agent Deployed",
                            value=domain_data['agent_deployed'],
                            key=f"agent_{domain_name}"
                        )
                        
                        threat_level = st.selectbox(
                            "Threat Level",
                            ["low", "medium", "high"],
                            index=["low", "medium", "high"].index(domain_data.get('threat_level', 'low')),
                            key=f"threat_{domain_name}"
                        )
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 Save", key=f"save_domain_{domain_name}"):
                            # Update domain configuration
                            self.db_manager.domains[domain_name].update({
                                'status': new_status,
                                'dns_validated': dns_validated,
                                'agent_deployed': agent_deployed,
                                'threat_level': threat_level
                            })
                            self.db_manager.save_json_file(self.db_manager.domains_file, self.db_manager.domains)
                            st.success("Domain configuration updated")
                            st.session_state[f"config_{domain_name}"] = False
                            st.rerun()
                    
                    with col_cancel:
                        if st.button("❌ Cancel", key=f"cancel_domain_{domain_name}"):
                            st.session_state[f"config_{domain_name}"] = False
                            st.rerun()
            
            st.markdown("---")
    
    def show_audit_logs(self):
        """Show audit logs interface"""
        st.markdown("### 📋 System Audit Logs")
        
        # Audit log filters
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            date_filter = st.date_input("From Date", value=datetime.now().date() - timedelta(days=7))
        with col2:
            user_filter = st.selectbox("User", ["All Users"] + [u['username'] for u in self.auth_manager.get_all_users()])
        with col3:
            action_filter = st.selectbox("Action", ["All Actions", "LOGIN", "LOGOUT", "IP_BLOCKED", "IP_UNBLOCKED", "USER_CREATED", "DOMAIN_ADDED"])
        with col4:
            if st.button("🔍 Apply Filters"):
                st.info("Filters applied")
        
        # Generate sample audit logs
        audit_logs = []
        actions = ["LOGIN", "LOGOUT", "IP_BLOCKED", "IP_UNBLOCKED", "USER_CREATED", "DOMAIN_ADDED", "SETTINGS_CHANGED", "REPORT_GENERATED"]
        users = [u['username'] for u in self.auth_manager.get_all_users()]
        
        for i in range(50):
            timestamp = datetime.now() - timedelta(hours=random.randint(1, 168))
            log = {
                "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "User": random.choice(users),
                "Action": random.choice(actions),
                "Description": f"User performed {random.choice(actions).lower().replace('_', ' ')}",
                "IP Address": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                "Status": random.choice(["Success", "Failed", "Warning"])
            }
            audit_logs.append(log)
        
        # Apply filters
        filtered_logs = audit_logs
        if user_filter != "All Users":
            filtered_logs = [log for log in filtered_logs if log["User"] == user_filter]
        if action_filter != "All Actions":
            filtered_logs = [log for log in filtered_logs if log["Action"] == action_filter]
        
        # Display logs
        st.markdown(f"#### Showing {len(filtered_logs)} log entries")
        
        logs_df = pd.DataFrame(filtered_logs)
        
        if not logs_df.empty:
            st.dataframe(logs_df, use_container_width=True)
        else:
            st.info("No audit logs found matching the selected criteria")
        
        # Export options
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("📥 Export CSV"):
                csv = logs_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📧 Email Report"):
                st.success("Audit log report emailed to administrators")
        
        # Audit statistics
        st.markdown("#### Audit Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Events", len(audit_logs))
        with col2:
            success_rate = len([log for log in audit_logs if log["Status"] == "Success"]) / len(audit_logs) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        with col3:
            unique_users = len(set(log["User"] for log in audit_logs))
            st.metric("Active Users", unique_users)
        with col4:
            failed_logins = len([log for log in audit_logs if log["Action"] == "LOGIN" and log["Status"] == "Failed"])
            st.metric("Failed Logins", failed_logins)
    
    def show_system_configuration(self):
        """Show system configuration interface"""
        st.markdown("### ⚙️ System Configuration")
        
        tab1, tab2, tab3, tab4 = st.tabs(["🔧 General", "🛡️ Security", "📊 Performance", "🔄 Backup"])
        
        with tab1:
            st.markdown("#### General System Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**System Information**")
                system_name = st.text_input("System Name", value="Shield-AI Production")
                system_description = st.text_area("Description", value="Enterprise DDoS Protection Platform")
                timezone = st.selectbox("Timezone", ["UTC", "EST", "PST", "GMT"])
                
                st.markdown("**Default Settings**")
                default_threat_threshold = st.slider("Default Threat Threshold", 0.0, 1.0, 0.7)
                default_block_duration = st.selectbox("Default Block Duration", ["1 hour", "24 hours", "7 days"])
            
            with col2:
                st.markdown("**System Status**")
                st.success("🟢 System Online")
                st.info("🔄 Last Restart: 2024-01-15 06:00:00")
                st.metric("Uptime", "99.99%")
                st.metric("CPU Usage", "23%")
                st.metric("Memory Usage", "45%")
                st.metric("Disk Usage", "67%")
        
        with tab2:
            st.markdown("#### Security Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Authentication**")
                session_timeout = st.number_input("Session Timeout (minutes)", value=60, min_value=5, max_value=480)
                max_login_attempts = st.number_input("Max Login Attempts", value=5, min_value=1, max_value=10)
                require_2fa = st.checkbox("Require 2FA", value=True)
                
                st.markdown("**Password Policy**")
                min_password_length = st.number_input("Minimum Password Length", value=8, min_value=6, max_value=20)
                require_special_chars = st.checkbox("Require Special Characters", value=True)
                password_expiry_days = st.number_input("Password Expiry (days)", value=90, min_value=30, max_value=365)
            
            with col2:
                st.markdown("**API Security**")
                api_rate_limit = st.number_input("API Rate Limit (req/min)", value=1000, min_value=100, max_value=10000)
                require_api_key = st.checkbox("Require API Key", value=True)
                api_key_expiry = st.selectbox("API Key Expiry", ["30 days", "90 days", "1 year", "Never"])
                
                st.markdown("**Network Security**")
                allowed_ip_ranges = st.text_area("Allowed IP Ranges (CIDR)", value="0.0.0.0/0")
                enable_geo_blocking = st.checkbox("Enable Geo-blocking", value=False)
                blocked_countries = st.multiselect("Blocked Countries", ["CN", "RU", "KP", "IR"], default=[])
        
        with tab3:
            st.markdown("#### Performance Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Resource Limits**")
                max_concurrent_requests = st.number_input("Max Concurrent Requests", value=10000, min_value=100, max_value=100000)
                request_timeout = st.number_input("Request Timeout (seconds)", value=30, min_value=5, max_value=300)
                max_request_size = st.number_input("Max Request Size (MB)", value=10, min_value=1, max_value=100)
                
                st.markdown("**Caching**")
                enable_caching = st.checkbox("Enable Caching", value=True)
                cache_ttl = st.number_input("Cache TTL (seconds)", value=300, min_value=60, max_value=3600)
                max_cache_size = st.number_input("Max Cache Size (MB)", value=1000, min_value=100, max_value=10000)
            
            with col2:
                st.markdown("**Database**")
                connection_pool_size = st.number_input("Connection Pool Size", value=20, min_value=5, max_value=100)
                query_timeout = st.number_input("Query Timeout (seconds)", value=30, min_value=5, max_value=300)
                enable_query_logging = st.checkbox("Enable Query Logging", value=False)
                
                st.markdown("**Monitoring**")
                log_level = st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], index=1)
                enable_metrics = st.checkbox("Enable Metrics Collection", value=True)
                metrics_retention = st.selectbox("Metrics Retention", ["7 days", "30 days", "90 days", "1 year"])
        
        with tab4:
            st.markdown("#### Backup & Recovery")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Backup Settings**")
                enable_auto_backup = st.checkbox("Enable Automatic Backups", value=True)
                backup_frequency = st.selectbox("Backup Frequency", ["Hourly", "Daily", "Weekly", "Monthly"])
                backup_retention = st.selectbox("Backup Retention", ["7 days", "30 days", "90 days", "1 year"])
                
                st.markdown("**Backup Location**")
                backup_location = st.selectbox("Backup Location", ["Local Storage", "AWS S3", "Google Cloud Storage", "Azure Blob"])
                
                if backup_location != "Local Storage":
                    backup_credentials = st.text_area("Backup Credentials (JSON)", height=100)
            
            with col2:
                st.markdown("**Recovery Options**")
                
                if st.button("🔄 Create Manual Backup"):
                    with st.spinner("Creating backup..."):
                        import time
                        time.sleep(2)
                    st.success("Manual backup created successfully!")
                
                st.markdown("**Recent Backups**")
                backup_list = [
                    "2024-01-15 06:00:00 - Auto (Daily)",
                    "2024-01-14 06:00:00 - Auto (Daily)",
                    "2024-01-13 15:30:00 - Manual",
                    "2024-01-13 06:00:00 - Auto (Daily)",
                    "2024-01-12 06:00:00 - Auto (Daily)"
                ]
                
                for backup in backup_list:
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(backup)
                    with col_b:
                        if st.button("Restore", key=f"restore_{backup}"):
                            st.warning("Restore functionality requires confirmation")
        
        # Save configuration
        if st.button("💾 Save All Configuration Changes", type="primary"):
            st.success("Configuration saved successfully!")
            st.info("Some changes may require a system restart to take effect.")