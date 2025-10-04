import streamlit as st
import google.generativeai as genai
import json
import random
from datetime import datetime
import time

class ShieldAIChatbot:
    def __init__(self):
        # For demo purposes, we'll simulate the Gemini Pro API
        # In production, you would use: genai.configure(api_key="your-api-key")
        self.model_name = "gemini-pro"
        self.conversation_history = []
        self.security_context = self.load_security_context()
        
    def load_security_context(self):
        """Load security context for the chatbot"""
        return {
            "current_threats": ["DDoS attacks from 192.168.1.100", "Port scanning detected", "Unusual traffic patterns"],
            "blocked_ips": ["192.168.1.100", "10.0.0.50", "172.16.0.25"],
            "recent_alerts": ["High volume traffic detected", "Suspicious login attempts", "Potential data exfiltration"],
            "system_status": "All systems operational",
            "active_domains": ["example.com", "testsite.org", "myapp.net"],
            "ml_models": {
                "random_forest": {"status": "active", "accuracy": "94.2%"},
                "xgboost": {"status": "active", "accuracy": "96.1%"},
                "isolation_forest": {"status": "active", "accuracy": "89.7%"}
            }
        }
    
    def simulate_gemini_response(self, user_message):
        """Simulate Gemini Pro responses for security-related queries"""
        user_message_lower = user_message.lower()
        
        # Security-specific responses
        if any(word in user_message_lower for word in ['threat', 'attack', 'ddos', 'security']):
            responses = [
                f"Based on current threat analysis, I've detected {len(self.security_context['current_threats'])} active threats. The most critical is: {self.security_context['current_threats'][0]}. I recommend immediate IP blocking and traffic analysis.",
                
                f"Current security status shows {len(self.security_context['blocked_ips'])} IPs are blocked. Our ML models are operating at high accuracy: Random Forest (94.2%), XGBoost (96.1%). Would you like me to analyze specific traffic patterns?",
                
                "I'm monitoring your network perimeter. Recent patterns suggest potential reconnaissance activity. I recommend increasing monitoring sensitivity and reviewing firewall rules for the affected domains.",
                
                f"Shield-AI has successfully mitigated {random.randint(15, 45)} threats in the last 24 hours. Current threat level is {'HIGH' if random.random() > 0.7 else 'MEDIUM'}. All {len(self.security_context['active_domains'])} monitored domains are secure."
            ]
            return random.choice(responses)
        
        elif any(word in user_message_lower for word in ['block', 'ip', 'unblock']):
            return f"I can help you manage IP blocking. Currently, {len(self.security_context['blocked_ips'])} IPs are blocked. To block a new IP, provide the IP address and reason. To unblock, specify the IP and I'll verify it's safe to remove from the blocklist."
        
        elif any(word in user_message_lower for word in ['alert', 'notification', 'report']):
            return f"Recent alerts include: {', '.join(self.security_context['recent_alerts'][:2])}. I can generate detailed reports, set up custom alert thresholds, or configure notification channels (email, SMS, Slack, Discord). What would you like to configure?"
        
        elif any(word in user_message_lower for word in ['domain', 'website', 'monitor']):
            return f"You're currently monitoring {len(self.security_context['active_domains'])} domains: {', '.join(self.security_context['active_domains'])}. I can help add new domains, validate DNS settings, deploy monitoring agents, or analyze domain-specific traffic patterns."
        
        elif any(word in user_message_lower for word in ['model', 'ml', 'machine learning', 'ai']):
            model_status = []
            for model, info in self.security_context['ml_models'].items():
                model_status.append(f"{model.replace('_', ' ').title()}: {info['accuracy']} accuracy")
            
            return f"ML Models Status: {', '.join(model_status)}. All models are actively analyzing traffic patterns. I can explain model decisions, adjust sensitivity thresholds, or retrain models with new threat data."
        
        elif any(word in user_message_lower for word in ['help', 'what can you do', 'commands']):
            return """I'm your Shield-AI security assistant! I can help with:

🛡️ **Threat Analysis**: Real-time threat assessment and recommendations
🚫 **IP Management**: Block/unblock IPs, manage allowlists
📊 **Reports**: Generate security reports and analytics
🔔 **Alerts**: Configure notifications and alert thresholds  
🌐 **Domain Management**: Add domains, deploy agents, DNS validation
🤖 **ML Models**: Explain AI decisions, adjust model parameters
📈 **Traffic Analysis**: Deep dive into traffic patterns and anomalies
⚙️ **System Config**: Help with platform settings and integrations

Just ask me anything about your network security!"""
        
        elif any(word in user_message_lower for word in ['status', 'health', 'system']):
            return f"🟢 System Status: {self.security_context['system_status']}\n\n📊 Current Metrics:\n• Active Threats: {len(self.security_context['current_threats'])}\n• Blocked IPs: {len(self.security_context['blocked_ips'])}\n• Monitored Domains: {len(self.security_context['active_domains'])}\n• ML Models: All operational\n• Last Update: {datetime.now().strftime('%H:%M:%S')}"
        
        else:
            # General AI assistant responses
            general_responses = [
                "I'm here to help with your cybersecurity needs. Could you be more specific about what you'd like assistance with?",
                "As your Shield-AI assistant, I can help analyze threats, manage IP blocks, configure alerts, and much more. What would you like to explore?",
                "I'm analyzing your security posture continuously. Is there a specific security concern or task you'd like me to help with?",
                "I have access to real-time threat intelligence and your system data. How can I assist you in strengthening your security defenses?"
            ]
            return random.choice(general_responses)
    
    def get_response(self, user_message):
        """Get response from the AI assistant"""
        try:
            # In production, you would use:
            # model = genai.GenerativeModel(self.model_name)
            # response = model.generate_content(user_message)
            # return response.text
            
            # For demo, simulate the response
            response = self.simulate_gemini_response(user_message)
            
            # Add to conversation history
            self.conversation_history.append({
                "user": user_message,
                "assistant": response,
                "timestamp": datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties. Error: {str(e)}. Please try again or contact support."
    
    def show_chat_interface(self):
        """Display the chat interface"""
        st.markdown("### 🤖 Shield-AI Security Assistant")
        st.markdown("*Powered by Google Gemini Pro*")
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display conversation history
            if st.session_state.chat_messages:
                for i, message in enumerate(st.session_state.chat_messages):
                    if message["role"] == "user":
                        st.markdown(f"""
                        <div style="background: #e3f2fd; padding: 10px; border-radius: 10px; margin: 5px 0; margin-left: 20%;">
                            <strong>You:</strong> {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: #f3e5f5; padding: 10px; border-radius: 10px; margin: 5px 0; margin-right: 20%;">
                            <strong>🤖 Shield-AI:</strong> {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                # Welcome message
                st.markdown("""
                <div style="background: #f3e5f5; padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <strong>🤖 Shield-AI Assistant:</strong> Hello! I'm your AI-powered security assistant. I can help you with threat analysis, IP management, security reports, and much more. How can I assist you today?
                </div>
                """, unsafe_allow_html=True)
        
        # Chat input
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Ask me anything about your security...",
                key="chat_input",
                placeholder="e.g., 'What threats are currently detected?' or 'Block IP 192.168.1.100'"
            )
        
        with col2:
            send_button = st.button("Send", key="send_chat")
        
        # Process user input
        if send_button and user_input:
            # Add user message
            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Get AI response
            with st.spinner("🤖 Thinking..."):
                ai_response = self.get_response(user_input)
            
            # Add AI response
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": ai_response
            })
            
            # Clear input and refresh
            st.rerun()
        
        # Quick action buttons
        st.markdown("#### Quick Actions:")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔍 Threat Status", key="quick_threat"):
                st.session_state.chat_messages.append({"role": "user", "content": "What's the current threat status?"})
                ai_response = self.get_response("What's the current threat status?")
                st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
        
        with col2:
            if st.button("🚫 Blocked IPs", key="quick_blocked"):
                st.session_state.chat_messages.append({"role": "user", "content": "Show me blocked IPs"})
                ai_response = self.get_response("Show me blocked IPs")
                st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
        
        with col3:
            if st.button("📊 Generate Report", key="quick_report"):
                st.session_state.chat_messages.append({"role": "user", "content": "Generate a security report"})
                ai_response = self.get_response("Generate a security report")
                st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
        
        with col4:
            if st.button("❓ Help", key="quick_help"):
                st.session_state.chat_messages.append({"role": "user", "content": "What can you help me with?"})
                ai_response = self.get_response("What can you help me with?")
                st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chat_messages = []
            st.rerun()
    
    def get_contextual_suggestions(self, current_page):
        """Get contextual suggestions based on current page"""
        suggestions = {
            "dashboard": [
                "What's my current threat level?",
                "Show me today's security summary",
                "Are there any critical alerts?"
            ],
            "threats": [
                "Explain the latest threat detection",
                "How accurate are the ML models?",
                "What should I do about high-risk IPs?"
            ],
            "ip_management": [
                "Block IP 192.168.1.100 for suspicious activity",
                "Show me recently blocked IPs",
                "Unblock IP if it's safe"
            ],
            "reports": [
                "Generate a weekly security report",
                "Show me threat trends",
                "Export blocked IP statistics"
            ]
        }
        
        return suggestions.get(current_page, suggestions["dashboard"])