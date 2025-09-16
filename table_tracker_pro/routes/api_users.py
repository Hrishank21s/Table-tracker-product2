from flask import Blueprint, jsonify, request
from flask_login import current_user
from utils.decorators import admin_only, json_required
import json
import os

api_users_bp = Blueprint('api_users', __name__)
ABSOLUTE_FILE = '/home/h21s/table_tracker_pro/data/users.json'

@api_users_bp.route('/api/users', methods=['GET'])
@admin_only
def get_users():
    try:
        with open(ABSOLUTE_FILE, 'r') as f:
            users = json.load(f)
        
        user_list = []
        for username, user_data in users.items():
            user_list.append({
                'username': username,
                'role': user_data['role'],
                'can_remove': username not in ['admin', 'staff1']
            })
        
        return jsonify({"success": True, "users": user_list})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_users_bp.route('/api/users/add', methods=['POST'])
@admin_only
@json_required
def add_user():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', 'staff')
        
        print(f"🚀 NO-CACHE ADD: Adding {username}")
        
        if not username or not password:
            return jsonify({"success": False, "error": "Username and password required"}), 400
        
        # Read current users
        with open(ABSOLUTE_FILE, 'r') as f:
            users = json.load(f)
        print(f"   Before: {list(users.keys())}")
        
        # Add new user
        users[username] = {'password': password, 'role': role}
        print(f"   After: {list(users.keys())}")
        
        # Write to file
        with open(ABSOLUTE_FILE, 'w') as f:
            json.dump(users, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        print("   File written and synced")
        
        # Verify
        with open(ABSOLUTE_FILE, 'r') as f:
            verify = json.load(f)
        print(f"   Verified: {list(verify.keys())}")
        
        if username in verify:
            print(f"✅ NO-CACHE SUCCESS: {username} saved!")
            return jsonify({"success": True, "message": f"User '{username}' added successfully"})
        else:
            print(f"❌ NO-CACHE FAILED: {username} not found")
            return jsonify({"success": False, "error": "User not saved"}), 500
        
    except Exception as e:
        print(f"❌ NO-CACHE ERROR: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@api_users_bp.route('/api/users/remove', methods=['POST'])
@admin_only
@json_required
def remove_user():
    return jsonify({"success": False, "error": "Remove disabled for safety"}), 400
