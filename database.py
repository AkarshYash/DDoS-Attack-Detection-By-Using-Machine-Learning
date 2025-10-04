import json
import os
from datetime import datetime, timedelta
import random
import pandas as pd
import numpy as np

class DatabaseManager:
    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_directory()
        self.domains_file = os.path.join(self.data_dir, "domains.json")
        self.traffic_file = os.path.join(self.data_dir, "traffic.json")
        self.alerts_file = os.path.join(self.data_dir, "alerts.json")
        self.blocked_ips_file = os.path.join(self.data_dir, "blocked_ips.json")
        self.audit_logs_file = os.path.join(self.data_dir, "audit_logs.json")
        
        self.load_or_create_data()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_or_create_data(self):
        """Load existing data or create sample data"""
        self.domains = self.load_json_file(self.domains_file, self.create_sample_domains())
        self.traffic_data = self.load_json_file(self.traffic_file, [])
        self.alerts = self.load_json_file(self.alerts_file, self.create_sample_alerts())
        self.blocked_ips = self.load_json_file(self.blocked_ips_file, self.create_sample_blocked_ips())
        self.audit_logs = self.load_json_file(self.audit_logs_file, [])
    
    def load_json_file(self, filepath, default_data):
        """Load JSON file or return default data"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default_data
    
    def save_json_file(self, filepath, data):
        """Save data to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def create_sample_domains(self):
        """Create sample domain data"""
        return {
            "example.com": {
                "domain_id": "dom_001",
                "owner": "admin",
                "organization": "Shield-AI Corp",
                "status": "active",
                "dns_validated": True,
                "monitoring_token": "tok_abc123xyz",
                "agent_deployed": True,
                "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
                "last_traffic": datetime.now().isoformat(),
                "total_requests": 1250000,
                "blocked_requests": 1250,
                "threat_level": "low"
            },
            "testsite.org": {
                "domain_id": "dom_002",
                "owner": "analyst",
                "organization": "Demo Company",
                "status": "active",
                "dns_validated": True,
                "monitoring_token": "tok_def456uvw",
                "agent_deployed": False,
                "created_at": (datetime.now() - timedelta(days=15)).isoformat(),
                "last_traffic": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "total_requests": 85000,
                "blocked_requests": 45,
                "threat_level": "medium"
            },
            "myapp.net": {
                "domain_id": "dom_003",
                "owner": "employee",
                "organization": "Personal",
                "status": "monitoring",
                "dns_validated": False,
                "monitoring_token": "tok_ghi789rst",
                "agent_deployed": True,
                "created_at": (datetime.now() - timedelta(days=7)).isoformat(),
                "last_traffic": (datetime.now() - timedelta(hours=2)).isoformat(),
                "total_requests": 25000,
                "blocked_requests": 5,
                "threat_level": "low"
            }
        }
    
    def create_sample_alerts(self):
        """Create sample alert data"""
        alerts = []
        alert_types = ["DDoS Attack", "Port Scan", "Brute Force", "Suspicious Traffic", "High Volume"]
        severities = ["Critical", "High", "Medium", "Low"]
        
        for i in range(20):
            timestamp = datetime.now() - timedelta(minutes=random.randint(1, 1440))
            alert = {
                "alert_id": f"alert_{i+1:03d}",
                "timestamp": timestamp.isoformat(),
                "type": random.choice(alert_types),
                "severity": random.choice(severities),
                "source_ip": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                "target_domain": random.choice(list(self.create_sample_domains().keys())),
                "description": f"Detected {random.choice(alert_types).lower()} from suspicious source",
                "status": random.choice(["Active", "Resolved", "Investigating"]),
                "confidence": random.uniform(0.7, 0.99),
                "actions_taken": ["IP Blocked"] if random.choice([True, False]) else ["Monitoring"],
                "analyst_notes": ""
            }
            alerts.append(alert)
        
        return sorted(alerts, key=lambda x: x['timestamp'], reverse=True)
    
    def create_sample_blocked_ips(self):
        """Create sample blocked IP data"""
        blocked_ips = []
        
        for i in range(50):
            timestamp = datetime.now() - timedelta(hours=random.randint(1, 168))
            ip = {
                "ip_address": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                "blocked_at": timestamp.isoformat(),
                "blocked_by": random.choice(["admin", "analyst", "auto-system"]),
                "reason": random.choice(["DDoS Attack", "Brute Force", "Port Scan", "Malicious Activity"]),
                "severity": random.choice(["Critical", "High", "Medium"]),
                "duration": random.choice(["1 hour", "24 hours", "7 days", "30 days", "Permanent"]),
                "expires_at": (timestamp + timedelta(hours=random.randint(1, 720))).isoformat(),
                "status": random.choice(["Active", "Expired", "Manual Override"]),
                "country": random.choice(["US", "CN", "RU", "BR", "IN", "DE", "FR", "UK", "JP", "KR"]),
                "organization": random.choice(["Unknown", "Hosting Provider", "VPN Service", "ISP", "Cloud Provider"]),
                "threat_score": random.uniform(0.7, 1.0),
                "packet_count": random.randint(1000, 100000),
                "bytes_transferred": random.randint(50000, 10000000)
            }
            blocked_ips.append(ip)
        
        return sorted(blocked_ips, key=lambda x: x['blocked_at'], reverse=True)
    
    def get_domains_for_user(self, username):
        """Get domains owned by a specific user"""
        user_domains = {}
        for domain, data in self.domains.items():
            if data['owner'] == username:
                user_domains[domain] = data
        return user_domains
    
    def add_domain(self, domain_name, owner, organization):
        """Add a new domain"""
        domain_id = f"dom_{len(self.domains)+1:03d}"
        monitoring_token = f"tok_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=12))}"
        
        self.domains[domain_name] = {
            "domain_id": domain_id,
            "owner": owner,
            "organization": organization,
            "status": "pending",
            "dns_validated": False,
            "monitoring_token": monitoring_token,
            "agent_deployed": False,
            "created_at": datetime.now().isoformat(),
            "last_traffic": None,
            "total_requests": 0,
            "blocked_requests": 0,
            "threat_level": "unknown"
        }
        
        self.save_json_file(self.domains_file, self.domains)
        return domain_id, monitoring_token
    
    def update_domain_status(self, domain_name, status):
        """Update domain status"""
        if domain_name in self.domains:
            self.domains[domain_name]['status'] = status
            self.save_json_file(self.domains_file, self.domains)
            return True
        return False
    
    def get_recent_alerts(self, limit=10):
        """Get recent alerts"""
        return self.alerts[:limit]
    
    def add_alert(self, alert_data):
        """Add a new alert"""
        alert_data['alert_id'] = f"alert_{len(self.alerts)+1:03d}"
        alert_data['timestamp'] = datetime.now().isoformat()
        self.alerts.insert(0, alert_data)
        self.save_json_file(self.alerts_file, self.alerts)
    
    def get_blocked_ips(self, limit=None):
        """Get blocked IPs"""
        if limit:
            return self.blocked_ips[:limit]
        return self.blocked_ips
    
    def block_ip(self, ip_address, reason, blocked_by, duration="24 hours"):
        """Block an IP address"""
        blocked_ip = {
            "ip_address": ip_address,
            "blocked_at": datetime.now().isoformat(),
            "blocked_by": blocked_by,
            "reason": reason,
            "severity": "High",
            "duration": duration,
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "status": "Active",
            "country": "Unknown",
            "organization": "Unknown",
            "threat_score": 0.8,
            "packet_count": 0,
            "bytes_transferred": 0
        }
        
        self.blocked_ips.insert(0, blocked_ip)
        self.save_json_file(self.blocked_ips_file, self.blocked_ips)
        
        # Add audit log
        self.add_audit_log(blocked_by, "IP_BLOCKED", f"Blocked IP {ip_address} for {reason}")
    
    def unblock_ip(self, ip_address, unblocked_by):
        """Unblock an IP address"""
        for ip_data in self.blocked_ips:
            if ip_data['ip_address'] == ip_address and ip_data['status'] == 'Active':
                ip_data['status'] = 'Manual Override'
                ip_data['unblocked_at'] = datetime.now().isoformat()
                ip_data['unblocked_by'] = unblocked_by
                break
        
        self.save_json_file(self.blocked_ips_file, self.blocked_ips)
        self.add_audit_log(unblocked_by, "IP_UNBLOCKED", f"Unblocked IP {ip_address}")
    
    def add_audit_log(self, user, action, description):
        """Add audit log entry"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "action": action,
            "description": description,
            "ip_address": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "user_agent": "Shield-AI Dashboard"
        }
        
        self.audit_logs.insert(0, log_entry)
        # Keep only last 1000 logs
        self.audit_logs = self.audit_logs[:1000]
        self.save_json_file(self.audit_logs_file, self.audit_logs)
    
    def get_audit_logs(self, limit=50):
        """Get audit logs"""
        return self.audit_logs[:limit]
    
    def generate_traffic_stats(self):
        """Generate traffic statistics"""
        now = datetime.now()
        
        # Generate hourly stats for last 24 hours
        stats = []
        for i in range(24):
            timestamp = now - timedelta(hours=i)
            stat = {
                "timestamp": timestamp.isoformat(),
                "requests": random.randint(800, 2000),
                "bytes": random.randint(500000, 2000000),
                "unique_ips": random.randint(100, 500),
                "blocked_requests": random.randint(0, 50),
                "threat_score": random.uniform(0.1, 0.8)
            }
            stats.append(stat)
        
        return sorted(stats, key=lambda x: x['timestamp'])
    
    def get_geographic_data(self):
        """Get geographic traffic distribution"""
        countries = {
            "United States": random.randint(1000, 5000),
            "China": random.randint(500, 2000),
            "Germany": random.randint(300, 1500),
            "United Kingdom": random.randint(200, 1000),
            "France": random.randint(200, 1000),
            "Japan": random.randint(150, 800),
            "Brazil": random.randint(100, 600),
            "India": random.randint(100, 600),
            "Russia": random.randint(50, 300),
            "Canada": random.randint(50, 300)
        }
        
        return [{"country": k, "requests": v} for k, v in countries.items()]
    
    def get_threat_timeline(self):
        """Get threat detection timeline"""
        timeline = []
        now = datetime.now()
        
        for i in range(48):  # Last 48 hours
            timestamp = now - timedelta(hours=i)
            threats = random.randint(0, 10)
            timeline.append({
                "timestamp": timestamp.isoformat(),
                "threats_detected": threats,
                "severity_high": random.randint(0, max(1, threats//3)),
                "severity_medium": random.randint(0, max(1, threats//2)),
                "severity_low": threats - random.randint(0, max(1, threats//3)) - random.randint(0, max(1, threats//2))
            })
        
        return sorted(timeline, key=lambda x: x['timestamp'])