import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

class ThemeManager:
    def __init__(self):
        self.themes = {
            'dark': {
                'primary_color': '#1e3c72',
                'background_color': '#0e1117',
                'secondary_background_color': '#262730',
                'text_color': '#fafafa',
                'font': 'sans serif'
            },
            'light': {
                'primary_color': '#2a5298',
                'background_color': '#ffffff',
                'secondary_background_color': '#f0f2f6',
                'text_color': '#262730',
                'font': 'sans serif'
            }
        }
    
    def apply_theme(self, theme_name):
        """Apply the selected theme"""
        if theme_name not in self.themes:
            theme_name = 'dark'
        
        theme = self.themes[theme_name]
        
        # Apply custom CSS based on theme
        if theme_name == 'dark':
            st.markdown("""
            <style>
            .stApp {
                background: linear-gradient(135deg, #0e1117 0%, #1e1e1e 100%);
            }
            .metric-card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .chat-container {
                background: rgba(30, 60, 114, 0.9);
                backdrop-filter: blur(15px);
            }
            </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <style>
            .stApp {
                background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            }
            .metric-card {
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0, 0, 0, 0.1);
            }
            .chat-container {
                background: rgba(42, 82, 152, 0.9);
                backdrop-filter: blur(15px);
            }
            </style>
            """, unsafe_allow_html=True)

class AlertSystem:
    def __init__(self):
        self.alert_channels = {
            'email': True,
            'sms': False,
            'slack': True,
            'discord': False,
            'webhook': False
        }
        self.alert_thresholds = {
            'threat_score': 0.7,
            'traffic_spike': 200,
            'failed_logins': 5,
            'blocked_ips_hour': 10
        }
    
    def get_recent_alerts(self):
        """Get recent security alerts"""
        alerts = []
        alert_types = ["DDoS Attack Detected", "Suspicious Login Activity", "High Traffic Volume", "Port Scan Detected", "Brute Force Attempt"]
        severities = ["Critical", "High", "Medium", "Low"]
        
        for i in range(15):
            timestamp = datetime.now() - timedelta(minutes=random.randint(1, 1440))
            alert = {
                "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "Type": random.choice(alert_types),
                "Severity": random.choice(severities),
                "Source": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                "Status": random.choice(["Active", "Resolved", "Investigating"]),
                "Action": random.choice(["IP Blocked", "Monitoring", "Alert Sent", "Manual Review"])
            }
            alerts.append(alert)
        
        return pd.DataFrame(alerts)
    
    def send_alert(self, alert_type, message, severity="Medium"):
        """Send alert through configured channels"""
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "message": message,
            "severity": severity,
            "channels_notified": []
        }
        
        # Simulate sending through different channels
        if self.alert_channels['email']:
            alert_data["channels_notified"].append("email")
        
        if self.alert_channels['slack']:
            alert_data["channels_notified"].append("slack")
        
        if self.alert_channels['sms'] and severity in ["Critical", "High"]:
            alert_data["channels_notified"].append("sms")
        
        return alert_data
    
    def check_thresholds(self, metrics):
        """Check if any alert thresholds are exceeded"""
        alerts_triggered = []
        
        if metrics.get('threat_score', 0) > self.alert_thresholds['threat_score']:
            alerts_triggered.append({
                "type": "High Threat Score",
                "message": f"Threat score {metrics['threat_score']:.2%} exceeds threshold {self.alert_thresholds['threat_score']:.2%}",
                "severity": "High"
            })
        
        if metrics.get('traffic_increase', 0) > self.alert_thresholds['traffic_spike']:
            alerts_triggered.append({
                "type": "Traffic Spike",
                "message": f"Traffic increased by {metrics['traffic_increase']}% (threshold: {self.alert_thresholds['traffic_spike']}%)",
                "severity": "Medium"
            })
        
        return alerts_triggered

class DataProcessor:
    @staticmethod
    def process_traffic_data(raw_data):
        """Process raw traffic data for analysis"""
        processed_data = {
            'total_requests': sum(raw_data.get('requests', [])),
            'unique_ips': len(set(raw_data.get('source_ips', []))),
            'avg_response_time': sum(raw_data.get('response_times', [])) / max(len(raw_data.get('response_times', [])), 1),
            'error_rate': len([r for r in raw_data.get('status_codes', []) if r >= 400]) / max(len(raw_data.get('status_codes', [])), 1)
        }
        return processed_data
    
    @staticmethod
    def generate_threat_features(traffic_data):
        """Generate features for ML threat detection"""
        features = {
            'packet_rate': traffic_data.get('packets_per_second', random.uniform(50, 200)),
            'byte_rate': traffic_data.get('bytes_per_second', random.uniform(30000, 70000)),
            'flow_duration': traffic_data.get('avg_flow_duration', random.uniform(1, 10)),
            'packet_size_avg': traffic_data.get('avg_packet_size', random.uniform(600, 1000)),
            'packet_size_std': traffic_data.get('packet_size_std', random.uniform(80, 120)),
            'inter_arrival_time': traffic_data.get('inter_arrival_time', random.uniform(0.005, 0.02)),
            'protocol_tcp': traffic_data.get('tcp_ratio', random.uniform(0.6, 0.8)),
            'protocol_udp': traffic_data.get('udp_ratio', random.uniform(0.15, 0.3)),
            'protocol_icmp': traffic_data.get('icmp_ratio', random.uniform(0.01, 0.1)),
            'src_port_entropy': traffic_data.get('src_port_entropy', random.uniform(2.5, 4.0)),
            'dst_port_entropy': traffic_data.get('dst_port_entropy', random.uniform(1.5, 2.5)),
            'flag_syn': traffic_data.get('syn_ratio', random.uniform(0.2, 0.4)),
            'flag_ack': traffic_data.get('ack_ratio', random.uniform(0.7, 0.9)),
            'flag_fin': traffic_data.get('fin_ratio', random.uniform(0.1, 0.3)),
            'flag_rst': traffic_data.get('rst_ratio', random.uniform(0.05, 0.15)),
            'payload_entropy': traffic_data.get('payload_entropy', random.uniform(3.0, 5.0))
        }
        return features

class ReportGenerator:
    def __init__(self):
        self.templates = {
            'security_summary': self.generate_security_summary,
            'threat_analysis': self.generate_threat_analysis,
            'traffic_report': self.generate_traffic_report,
            'executive_summary': self.generate_executive_summary
        }
    
    def generate_security_summary(self, data):
        """Generate security summary report"""
        report = f"""
# Security Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
- **Total Requests Analyzed**: {data.get('total_requests', 'N/A'):,}
- **Threats Detected**: {data.get('threats_detected', 'N/A')}
- **IPs Blocked**: {data.get('ips_blocked', 'N/A')}
- **Success Rate**: {data.get('success_rate', 'N/A')}%

## Key Metrics
- **Average Threat Score**: {data.get('avg_threat_score', 'N/A')}
- **Peak Traffic**: {data.get('peak_traffic', 'N/A')} req/sec
- **Response Time**: {data.get('avg_response_time', 'N/A')}ms
- **Uptime**: {data.get('uptime', 'N/A')}%

## Top Threats
{self._format_threat_list(data.get('top_threats', []))}

## Recommendations
{self._format_recommendations(data.get('recommendations', []))}
        """
        return report.strip()
    
    def generate_threat_analysis(self, data):
        """Generate detailed threat analysis report"""
        report = f"""
# Threat Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Threat Landscape Overview
- **Total Threat Events**: {data.get('total_threats', 'N/A')}
- **Critical Threats**: {data.get('critical_threats', 'N/A')}
- **Active Investigations**: {data.get('active_investigations', 'N/A')}

## Attack Vector Analysis
{self._format_attack_vectors(data.get('attack_vectors', {}))}

## Geographic Distribution
{self._format_geographic_data(data.get('geographic_data', {}))}

## ML Model Performance
{self._format_ml_performance(data.get('ml_performance', {}))}

## Mitigation Actions
{self._format_mitigation_actions(data.get('mitigation_actions', []))}
        """
        return report.strip()
    
    def generate_traffic_report(self, data):
        """Generate traffic analysis report"""
        report = f"""
# Traffic Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Traffic Overview
- **Total Requests**: {data.get('total_requests', 'N/A'):,}
- **Unique Visitors**: {data.get('unique_visitors', 'N/A'):,}
- **Peak Hour**: {data.get('peak_hour', 'N/A')}
- **Average Load**: {data.get('avg_load', 'N/A')} req/sec

## Protocol Distribution
{self._format_protocol_distribution(data.get('protocols', {}))}

## Top Source Countries
{self._format_country_data(data.get('countries', {}))}

## Performance Metrics
- **Average Response Time**: {data.get('avg_response_time', 'N/A')}ms
- **Error Rate**: {data.get('error_rate', 'N/A')}%
- **Bandwidth Usage**: {data.get('bandwidth', 'N/A')} GB
        """
        return report.strip()
    
    def generate_executive_summary(self, data):
        """Generate executive summary report"""
        report = f"""
# Executive Security Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Security Posture
Shield-AI has successfully protected your infrastructure with **{data.get('success_rate', 99.9)}%** effectiveness.

## Key Achievements
- Blocked **{data.get('total_blocks', 'N/A')}** malicious IP addresses
- Prevented **{data.get('prevented_attacks', 'N/A')}** potential attacks
- Maintained **{data.get('uptime', 99.99)}%** system uptime

## Risk Assessment
Current risk level: **{data.get('risk_level', 'LOW')}**

## Investment ROI
- Estimated damage prevented: **${data.get('damage_prevented', 'N/A'):,}**
- Cost savings: **${data.get('cost_savings', 'N/A'):,}**
- ROI: **{data.get('roi', 'N/A')}%**

## Strategic Recommendations
{self._format_strategic_recommendations(data.get('strategic_recommendations', []))}
        """
        return report.strip()
    
    def _format_threat_list(self, threats):
        if not threats:
            return "- No significant threats detected"
        return "\n".join([f"- {threat}" for threat in threats[:5]])
    
    def _format_recommendations(self, recommendations):
        if not recommendations:
            return "- Continue current security posture"
        return "\n".join([f"- {rec}" for rec in recommendations[:5]])
    
    def _format_attack_vectors(self, vectors):
        if not vectors:
            return "- No attack vectors identified"
        return "\n".join([f"- **{k}**: {v}" for k, v in vectors.items()])
    
    def _format_geographic_data(self, geo_data):
        if not geo_data:
            return "- Geographic data not available"
        return "\n".join([f"- **{k}**: {v} threats" for k, v in geo_data.items()])
    
    def _format_ml_performance(self, performance):
        if not performance:
            return "- ML performance data not available"
        return "\n".join([f"- **{k}**: {v}" for k, v in performance.items()])
    
    def _format_mitigation_actions(self, actions):
        if not actions:
            return "- No mitigation actions required"
        return "\n".join([f"- {action}" for action in actions])
    
    def _format_protocol_distribution(self, protocols):
        if not protocols:
            return "- Protocol data not available"
        return "\n".join([f"- **{k}**: {v}%" for k, v in protocols.items()])
    
    def _format_country_data(self, countries):
        if not countries:
            return "- Country data not available"
        return "\n".join([f"- **{k}**: {v} requests" for k, v in countries.items()])
    
    def _format_strategic_recommendations(self, recommendations):
        if not recommendations:
            return "- Continue current security strategy"
        return "\n".join([f"- {rec}" for rec in recommendations])
    
    def generate_report(self, report_type, data):
        """Generate report of specified type"""
        if report_type in self.templates:
            return self.templates[report_type](data)
        else:
            return f"Report type '{report_type}' not supported"

class ConfigManager:
    def __init__(self):
        self.config_file = "shield_ai_config.json"
        self.default_config = {
            "system": {
                "name": "Shield-AI",
                "version": "1.0.0",
                "environment": "production",
                "timezone": "UTC"
            },
            "security": {
                "session_timeout": 3600,
                "max_login_attempts": 5,
                "password_policy": "strong",
                "require_2fa": True
            },
            "ml": {
                "threat_threshold": 0.7,
                "model_retrain_interval": 24,
                "feature_importance_threshold": 0.05
            },
            "alerts": {
                "email_enabled": True,
                "sms_enabled": False,
                "slack_enabled": True,
                "webhook_enabled": False
            },
            "performance": {
                "max_concurrent_requests": 10000,
                "cache_ttl": 300,
                "log_retention_days": 90
            }
        }
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.config = self.default_config.copy()
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, section, key, default=None):
        """Get configuration value"""
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section, key, value):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()
    
    def get_section(self, section):
        """Get entire configuration section"""
        return self.config.get(section, {})
    
    def update_section(self, section, updates):
        """Update entire configuration section"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section].update(updates)
        self.save_config()