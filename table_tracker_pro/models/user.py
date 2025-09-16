import json
import os
from flask_login import UserMixin

USERS_FILE = '/home/h21s/table_tracker_pro/data/users.json'
ABSOLUTE_FILE = '/home/h21s/table_tracker_pro/data/users.json'

class User(UserMixin):
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role
    
    def get_id(self):
        return self.username
    
    def check_password(self, password):
        return self.password == password
    
    @staticmethod
    def get_all_users():
        with open(ABSOLUTE_FILE, 'r') as f:
            users = json.load(f)
        print(f"📂 CACHE-FREE LOAD: {len(users)} users: {list(users.keys())}")
        return users
    
    @staticmethod
    def add_user(username, password, role):
        users = User.get_all_users()
        users[username] = {'password': password, 'role': role}
        
        with open(ABSOLUTE_FILE, 'w') as f:
            json.dump(users, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        return True
    
    @staticmethod
    def get(username):
        users = User.get_all_users()
        if username in users:
            data = users[username]
            return User(username, data['password'], data['role'])
        return None
    
    @staticmethod
    def authenticate(username, password):
        users = User.get_all_users()
        if username in users and users[username]['password'] == password:
            data = users[username]
            return User(username, data['password'], data['role'])
        return None

print("🔧 CACHE-FREE User System Ready")
