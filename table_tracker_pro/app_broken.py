#!/usr/bin/env python3
"""
TABLE TRACKER PRO - MAIN APPLICATION - SIMPLE USER SYSTEM
Enhanced Professional Table Management System
"""

import os
import sys
from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS

# Ensure we're in the right directory
if not os.path.basename(os.getcwd()) == 'table_tracker_pro':
    os.chdir('/home/h21s/table_tracker_pro')

# Import configuration
from config import Config

# Import models
from models.user import User
from models.customer import CustomerModel
from models.table import TableManager

# Import routes
from routes.auth import auth_bp
from routes.main import main_bp
from routes.tables import tables_bp
from routes.billing import billing_bp
from routes.api import api_bp
from routes.api_users import api_users_bp

# Import utilities
from utils.helpers import get_local_ip
from database.init_db import init_database

# ============================================================================
# GLOBAL INSTANCES - Initialize early
# ============================================================================

# Initialize Table Manager FIRST
print("🎯 Initializing Table Manager...")
table_manager = TableManager()
print(f"✅ Table Manager ready - Snooker: {len(table_manager.snooker_tables)}, Pool: {len(table_manager.pool_tables)}")

# ============================================================================
# APPLICATION FACTORY
# ============================================================================

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Ensure directories exist
    Config.ensure_directories()
    
    # Initialize database
    print("🗄️ Initializing database...")
    init_database()
    
    # Show user system status
    print("👥 User system status:")
    all_users = User.get_all_users()
    print(f"   Total users: {len(all_users)} - {list(all_users.keys())}")
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        print(f"🔐 Flask-Login requesting user: {user_id}")
        user = User.get(user_id)
        if user:
            print(f"✅ Flask-Login loaded user: {user_id} ({user.role})")
        else:
            print(f"❌ Flask-Login failed to load user: {user_id}")
        return user
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tables_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(api_users_bp)
    
    print("✅ Flask app configured successfully")
    return app

# ============================================================================
# CREATE APP INSTANCE
# ============================================================================

# Create Flask app
app = create_app()

# ============================================================================
# DEBUG ROUTES
# ============================================================================

@app.route('/debug/users')
def debug_users():
    """Debug endpoint to check user status"""
    users = User.get_all_users()
    users_file_path = User.get_users_file()
    
    file_exists = os.path.exists(users_file_path)
    file_content = {}
    
    if file_exists:
        try:
            with open(users_file_path, 'r') as f:
                import json
                file_content = json.load(f)
        except:
            file_content = {"error": "Could not read file"}
    
    return {
        'total_users': len(users),
        'users': {k: {'role': v['role']} for k, v in users.items()},
        'users_file_path': users_file_path,
        'users_file_exists': file_exists,
        'users_file_content': file_content,
        'default_users': list(["admin", "staff1"].keys()),
        'custom_users': list(User.load_custom_users().keys())
    }

@app.route('/debug/test-auth/<username>/<password>')
def debug_auth(username, password):
    """Debug authentication"""
    all_users = User.get_all_users()
    user_exists = username in all_users
    
    if user_exists:
        stored_data = all_users[username]
        password_match = password == stored_data['password']
    else:
        stored_data = None
        password_match = False
    
    # Test authentication methods
    auth_result = User.authenticate(username, password)
    get_result = User.get(username)
    
    return {
        'username': username,
        'password': password,
        'user_exists': user_exists,
        'stored_data': stored_data,
        'password_match': password_match,
        'authenticate_result': auth_result is not None,
        'get_result': get_result is not None,
        'all_users': list(all_users.keys()),
        'users_file': User.get_users_file(),
        'file_exists': os.path.exists(User.get_users_file())
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    return """
    <h1>404 - Page Not Found</h1>
    <p><a href="/">← Back to Home</a></p>
    """, 404

@app.errorhandler(500)
def internal_error(error):
    return """
    <h1>500 - Internal Server Error</h1>
    <p>Please try refreshing the page.</p>
    <p><a href="/">← Back to Home</a></p>
    """, 500

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_application():
    """Run the Table Tracker Pro application"""
    
    try:
        # Get network information
        local_ip = get_local_ip()
        port = Config.PORT
        
        # Final user check
        print("\n" + "="*70)
        print("🎯 TABLE TRACKER PRO - SIMPLE USER SYSTEM")
        print("="*70)
        
        final_users = User.get_all_users()
        print(f"👥 AVAILABLE USERS ({len(final_users)}):")
        for username, data in final_users.items():
            user_type = "DEFAULT" if username in ["admin", "staff1"] else "CUSTOM"
            print(f"   {username:<12} | {data['password']:<12} | {data['role']:<6} | {user_type}")
        
        print("="*70)
        print("🌐 ACCESS INFORMATION:")
        print(f"   Local:   http://localhost:{port}")
        print(f"   Network: http://{local_ip}:{port}")
        print("="*70)
        print("🔍 Debug URLs:")
        print(f"   Users:  http://localhost:{port}/debug/users")
        print(f"   Auth:   http://localhost:{port}/debug/test-auth/h21s/h21s")
        print("="*70)
        print("🔥 SYSTEM STATUS: READY")
        print("="*70)
        
        # Start the application
        app.run(
            host=Config.HOST,
            port=port,
            debug=Config.DEBUG,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Table Tracker Pro...")
        table_manager.stop()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_application()
