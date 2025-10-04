import streamlit as st
import hashlib
import json
import os
from datetime import datetime, timedelta
import random
import string

class AuthManager:
    def __init__(self):
        self.users_file = "users.json"
        self.load_users()
    
    def load_users(self):
        """Load users from JSON file or create default users"""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        else:
            # Create default users
            self.users = {
                "admin": {
                    "password": self.hash_password("admin123"),
                    "role": "admin",
                    "email": "admin@shieldai.com",
                    "organization": "Shield-AI Corp",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                    "permissions": ["all"]
                },
                "analyst": {
                    "password": self.hash_password("analyst123"),
                    "role": "analyst",
                    "email": "analyst@shieldai.com",
                    "organization": "Shield-AI Corp",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                    "permissions": ["view_dashboard", "manage_threats", "view_reports"]
                },
                "employee": {
                    "password": self.hash_password("employee123"),
                    "role": "employee",
                    "email": "employee@company.com",
                    "organization": "Demo Company",
                    "created_at": datetime.now().isoformat(),
                    "last_login": None,
                    "permissions": ["view_dashboard", "view_reports"]
                }
            }
            self.save_users()
    
    def save_users(self):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username, password):
        """Authenticate user credentials"""
        if username in self.users:
            hashed_password = self.hash_password(password)
            if self.users[username]["password"] == hashed_password:
                # Update last login
                self.users[username]["last_login"] = datetime.now().isoformat()
                self.save_users()
                return True
        return False
    
    def register_user(self, username, email, password, reg_type):
        """Register a new user"""
        if username in self.users:
            return False
        
        # Determine role based on registration type
        role_mapping = {
            "Personal Use": "personal",
            "Register Organization": "admin",
            "Employee Registration": "employee"
        }
        
        role = role_mapping.get(reg_type, "employee")
        
        # Set permissions based on role
        permissions = {
            "admin": ["all"],
            "analyst": ["view_dashboard", "manage_threats", "view_reports", "manage_ips"],
            "employee": ["view_dashboard", "view_reports"],
            "personal": ["view_dashboard", "manage_personal_domains"]
        }
        
        self.users[username] = {
            "password": self.hash_password(password),
            "role": role,
            "email": email,
            "organization": f"{username}'s Organization" if reg_type == "Register Organization" else "Personal",
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "permissions": permissions.get(role, ["view_dashboard"]),
            "registration_type": reg_type
        }
        
        self.save_users()
        return True
    
    def get_user_role(self, username):
        """Get user role"""
        return self.users.get(username, {}).get("role", "employee")
    
    def get_user_org(self, username):
        """Get user organization"""
        return self.users.get(username, {}).get("organization", "Unknown")
    
    def get_user_permissions(self, username):
        """Get user permissions"""
        return self.users.get(username, {}).get("permissions", [])
    
    def has_permission(self, username, permission):
        """Check if user has specific permission"""
        user_permissions = self.get_user_permissions(username)
        return "all" in user_permissions or permission in user_permissions
    
    def get_all_users(self):
        """Get all users (admin only)"""
        users_list = []
        for username, data in self.users.items():
            users_list.append({
                "username": username,
                "email": data["email"],
                "role": data["role"],
                "organization": data["organization"],
                "created_at": data["created_at"],
                "last_login": data.get("last_login", "Never")
            })
        return users_list
    
    def update_user_role(self, username, new_role):
        """Update user role (admin only)"""
        if username in self.users:
            self.users[username]["role"] = new_role
            
            # Update permissions based on new role
            permissions = {
                "admin": ["all"],
                "analyst": ["view_dashboard", "manage_threats", "view_reports", "manage_ips"],
                "employee": ["view_dashboard", "view_reports"],
                "personal": ["view_dashboard", "manage_personal_domains"]
            }
            
            self.users[username]["permissions"] = permissions.get(new_role, ["view_dashboard"])
            self.save_users()
            return True
        return False
    
    def delete_user(self, username):
        """Delete user (admin only)"""
        if username in self.users and username != "admin":  # Protect admin account
            del self.users[username]
            self.save_users()
            return True
        return False
    
    def generate_org_code(self):
        """Generate organization code for employee registration"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def simulate_oauth_providers(self):
        """Simulate OAuth provider options"""
        return {
            "Google": "🔴",
            "GitHub": "⚫",
            "Microsoft": "🔵",
            "LinkedIn": "🔷"
        }