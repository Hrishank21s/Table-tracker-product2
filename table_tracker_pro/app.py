#!/usr/bin/env python3
"""
TABLE TRACKER PRO - CLEAN START
"""

import os
import sys
from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS

# Change to project directory
os.chdir('/home/h21s/table_tracker_pro')

# Import everything
from config import Config
from models.user import User, USERS_FILE
from models.customer import CustomerModel
from models.table import TableManager
from routes.auth import auth_bp
from routes.main import main_bp
from routes.tables import tables_bp
from routes.billing import billing_bp
from routes.api import api_bp
from routes.api_users import api_users_bp
from utils.helpers import get_local_ip
from database.init_db import init_database

# Initialize Table Manager
print("🎯 Initializing Table Manager...")
table_manager = TableManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    
    # Ensure directories
    Config.ensure_directories()
    
    # Initialize database
    init_database()
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tables_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(api_users_bp)
    
    return app

# Create app
app = create_app()

# Debug routes
@app.route('/debug/users')
def debug_users():
    users = User.get_all_users()
    return {
        'users': users,
        'file': USERS_FILE,
        'total': len(users)
    }

@app.route('/debug/test-auth/<username>/<password>')
def debug_auth(username, password):
    auth_result = User.authenticate(username, password)
    return {
        'username': username,
        'success': auth_result is not None,
        'available_users': list(User.get_all_users().keys())
    }

def run_application():
    try:
        local_ip = get_local_ip()
        port = Config.PORT
        
        users = User.get_all_users()
        
        print("\n" + "="*50)
        print("🎯 TABLE TRACKER PRO - CLEAN START")
        print("="*50)
        print(f"👥 USERS ({len(users)}):")
        for username, data in users.items():
            print(f"   {username} / {data['password']} ({data['role']})")
        print("="*50)
        print(f"🌐 URL: http://{local_ip}:{port}")
        print("="*50)
        
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except KeyboardInterrupt:
        table_manager.stop()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_application()
