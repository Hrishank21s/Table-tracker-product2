from flask import Blueprint, jsonify, request
import json
import os
from flask_login import current_user
from models.customer import CustomerModel
from utils.decorators import api_login_required, admin_only, json_required, validate_game_type
from utils.helpers import validate_customer_data
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize customer model
customer_model = CustomerModel()

@api_bp.route('/<game_type>/tables', methods=['GET'])
@api_login_required
@validate_game_type
def get_tables(game_type):
    """Get all tables for a game type"""
    try:
        print(f"🌐 API Request: GET /{game_type}/tables from user {current_user.username}")
        
        # Import here to avoid circular import
        from app import table_manager
        
        tables = table_manager.get_tables(game_type)
        available_rates = table_manager.available_rates
        
        print(f"📊 API Response: {len(tables)} {game_type} tables found")
        
        return jsonify({
            "success": True,
            "tables": tables,
            "available_rates": available_rates,
            "timestamp": datetime.now().isoformat(),
            "game_type": game_type,
            "table_count": len(tables)
        })
        
    except Exception as e:
        print(f"❌ API Error in get_tables: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False, 
            "error": str(e),
            "tables": {},
            "available_rates": [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0],
            "timestamp": datetime.now().isoformat()
        }), 500

@api_bp.route('/<game_type>/table/<int:table_id>/action', methods=['POST'])
@api_login_required
@json_required
@validate_game_type
def table_action(game_type, table_id):
    """Handle table actions (start, pause, end)"""
    try:
        from app import table_manager
        
        data = request.get_json()
        action = data.get('action')
        
        print(f"🎮 Table Action: {game_type} Table {table_id} - {action} by {current_user.username}")
        
        if action not in ['start', 'pause', 'end']:
            return jsonify({"success": False, "error": "Invalid action"}), 400
        
        result = table_manager.handle_table_action(game_type, table_id, action, current_user.username)
        
        if result["success"]:
            tables = table_manager.get_tables(game_type)
            response_data = {
                "success": True,
                "table": table_id,
                "action": action,
                "message": result["message"],
                "tables": tables,
                "show_customer_popup": result.get("show_customer_popup", False)
            }
            
            if result.get("show_customer_popup") and "session_data" in result:
                response_data["session_data"] = result["session_data"]
            
            return jsonify(response_data)
        else:
            return jsonify({"success": False, "error": result["message"]}), 400
            
    except Exception as e:
        print(f"❌ API Error in table_action: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/<game_type>/table/<int:table_id>/rate', methods=['POST'])
@api_login_required
@json_required
@validate_game_type
def update_table_rate(game_type, table_id):
    """Update table rate"""
    try:
        from app import table_manager
        
        data = request.get_json()
        new_rate = data.get('rate')
        
        if not isinstance(new_rate, (int, float)):
            return jsonify({"success": False, "error": "Invalid rate value"}), 400
        
        result = table_manager.update_table_rate(game_type, table_id, float(new_rate))
        
        if result["success"]:
            tables = table_manager.get_tables(game_type)
            return jsonify({
                "success": True,
                "table": table_id,
                "new_rate": new_rate,
                "message": result["message"],
                "tables": tables
            })
        else:
            return jsonify({"success": False, "error": result["message"]}), 400
            
    except Exception as e:
        print(f"❌ API Error in update_table_rate: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/<game_type>/table/<int:table_id>/clear-sessions', methods=['POST'])
@api_login_required
@validate_game_type
def clear_table_sessions(game_type, table_id):
    """Clear all sessions for a table"""
    try:
        from app import table_manager
        
        result = table_manager.clear_table_sessions(game_type, table_id)
        
        if result["success"]:
            return jsonify({"success": True, "message": result["message"]})
        else:
            return jsonify({"success": False, "error": result["message"]}), 400
            
    except Exception as e:
        print(f"❌ API Error in clear_table_sessions: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/customers/search')
@api_login_required
def search_customers():
    """Search customers by name or phone"""
    try:
        term = request.args.get('term', '')
        
        if len(term) < 2:
            return jsonify([])
        
        customers = customer_model.search_customers(term)
        
        return jsonify([{
            'id': c[0], 'name': c[1], 'phone': c[2], 'total_amount': c[3] or 0,
            'total_minutes': c[4] or 0, 'snooker_amount': c[5] or 0, 'pool_amount': c[7] or 0
        } for c in customers])
        
    except Exception as e:
        print(f"❌ API Error in search_customers: {e}")
        return jsonify([])

@api_bp.route('/customers/add', methods=['POST'])
@api_login_required
@json_required
def add_customer():
    """Add a new customer"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        
        errors = validate_customer_data(name, phone)
        if errors:
            return jsonify({'success': False, 'error': '; '.join(errors)}), 400
        
        customer_id = customer_model.add_customer(name, phone)
        
        if customer_id:
            customer_model.export_to_txt()
            return jsonify({
                'success': True, 
                'id': customer_id, 
                'name': name, 
                'phone': phone,
                'message': f'Customer {name} added successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Phone number already exists'}), 400
            
    except Exception as e:
        print(f"❌ API Error in add_customer: {e}")
        return jsonify({'success': False, 'error': f'Failed to add customer: {str(e)}'}), 500

@api_bp.route('/customers/assign-amount', methods=['POST'])
@api_login_required
@json_required
def assign_amount_to_customer():
    """Assign amount to customer from table session"""
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        amount = data.get('amount')
        minutes = data.get('minutes')
        game_type = data.get('game_type', 'snooker')
        description = data.get('description', f'{game_type.title()} session')
        
        if not all([customer_id, amount is not None, minutes is not None]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        if game_type not in ['snooker', 'pool']:
            return jsonify({'success': False, 'error': 'Invalid game type'}), 400
        
        customer_model.add_amount_to_customer(
            customer_id, amount, minutes, description, current_user.username, game_type
        )
        customer_model.export_to_txt()
        return jsonify({'success': True, 'message': f'₹{amount:.2f} added to customer balance'})
        
    except Exception as e:
        print(f"❌ API Error in assign_amount_to_customer: {e}")
        return jsonify({'success': False, 'error': f'Failed to assign amount: {str(e)}'}), 500

@api_bp.route('/customers/adjust-balance', methods=['POST'])
@api_login_required
@json_required
def adjust_customer_balance():
    """Manually adjust customer balance"""
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        amount = data.get('amount')
        transaction_type = data.get('transaction_type')
        
        if not all([customer_id, amount is not None, transaction_type]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        if current_user.role == 'staff' and amount < 0:
            return jsonify({'success': False, 'error': 'Staff cannot subtract money'}), 403
        
        customer_model.adjust_customer_balance(
            customer_id, amount, transaction_type, current_user.username
        )
        customer_model.export_to_txt()
        action = 'added to' if amount > 0 else 'subtracted from'
        return jsonify({
            'success': True, 
            'message': f'₹{abs(amount):.2f} {action} customer balance'
        })
        
    except Exception as e:
        print(f"❌ API Error in adjust_customer_balance: {e}")
        return jsonify({'success': False, 'error': f'Failed to adjust balance: {str(e)}'}), 500

@api_bp.route('/customers/split-assign', methods=['POST'])
@api_login_required
@json_required
def split_assign_amount():
    """Split bill among multiple customers"""
    try:
        data = request.get_json()
        players = data.get('players', [])
        per_player_amount = data.get('per_player_amount')
        per_player_minutes = data.get('per_player_minutes')
        game_type = data.get('game_type', 'snooker')
        table_id = data.get('table_id')
        
        if not players or not per_player_amount:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Process each player
        for player in players:
            customer_id = player.get('customer_id')
            name = player.get('name')
            
            description = f"Split {game_type.title()} Table {table_id} session ({len(players)} players)"
            
            customer_model.add_amount_to_customer(
                customer_id, per_player_amount, per_player_minutes, 
                description, current_user.username, game_type
            )
        
        customer_model.export_to_txt()
        
        return jsonify({
            'success': True, 
            'message': f'Split bill assigned to {len(players)} players'
        })
        
    except Exception as e:
        print(f"❌ API Error in split_assign_amount: {e}")
        return jsonify({'success': False, 'error': f'Failed to assign split bill: {str(e)}'}), 500

@api_bp.route('/customers/all')
@api_login_required
def get_all_customers():
    """Get all customers with statistics"""
    try:
        customers = customer_model.get_all_customers()
        today_stats = customer_model.get_today_stats()
        top_customers = customer_model.get_top_customers(5)
        
        return jsonify({
            'success': True,
            'customers': [{
                'id': c[0], 'name': c[1], 'phone': c[2], 
                'total_amount': c[3] or 0, 'total_minutes': c[4] or 0,
                'snooker_amount': c[5] or 0, 'snooker_minutes': c[6] or 0,
                'pool_amount': c[7] or 0, 'pool_minutes': c[8] or 0,
                'today_amount': c[9] or 0, 'today_minutes': c[10] or 0,
                'last_session_time': c[13]
            } for c in customers],
            'today_stats': today_stats,
            'top_customers': top_customers
        })
        
    except Exception as e:
        print(f"❌ API Error in get_all_customers: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch customers: {str(e)}',
            'customers': [],
            'today_stats': {'total_customers': 0, 'today_total_amount': 0, 'today_total_minutes': 0, 'today_snooker_amount': 0, 'today_pool_amount': 0},
            'top_customers': []
        }), 500

@api_bp.route('/system/status')
@api_login_required
def system_status():
    """Get system status"""
    try:
        from app import table_manager
        
        snooker_running = sum(1 for table in table_manager.snooker_tables.values() if table['status'] == 'running')
        pool_running = sum(1 for table in table_manager.pool_tables.values() if table['status'] == 'running')
        
        return jsonify({
            'success': True,
            'system_status': 'online',
            'timestamp': datetime.now().isoformat(),
            'tables': {
                'snooker': {
                    'total': len(table_manager.snooker_tables),
                    'running': snooker_running,
                    'idle': len(table_manager.snooker_tables) - snooker_running
                },
                'pool': {
                    'total': len(table_manager.pool_tables),
                    'running': pool_running,
                    'idle': len(table_manager.pool_tables) - pool_running
                }
            }
        })
        
    except Exception as e:
        print(f"❌ API Error in system_status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/system/export', methods=['POST'])
@api_login_required
def export_data():
    """Export customer data"""
    try:
        success = customer_model.export_to_txt()
        if success:
            return jsonify({
                'success': True, 
                'message': 'Data exported successfully',
                'file_path': customer_model.export_path
            })
        else:
            return jsonify({'success': False, 'error': 'Export failed'}), 500
            
    except Exception as e:
        print(f"❌ API Error in export_data: {e}")
        return jsonify({'success': False, 'error': f'Export failed: {str(e)}'}), 500

# ============================================================================
# USER MANAGEMENT API ENDPOINTS - FIXED
# ============================================================================

@api_bp.route('/users', methods=['GET'])
@admin_only
def get_users():
    """Get all users (Admin only) - FIXED TO READ FROM JSON FILE"""
    try:
        print(f"🔍 FIXED GET: Loading users for admin: {current_user.username}")
        
        USERS_FILE = "/home/h21s/table_tracker_pro/data/users.json"
        
        # Read from JSON file instead of Config.DEFAULT_USERS
        with open(USERS_FILE, "r") as f:
            all_users = json.load(f)
        
        print(f"📁 FIXED GET: Found {len(all_users)} users in JSON file: {list(all_users.keys())}")
        
        user_list = []
        for username, user_data in all_users.items():
            user_list.append({
                "username": username,
                "role": user_data["role"],
                "can_remove": username != current_user.username and username not in ["admin", "staff1"]
            })
        
        print(f"✅ FIXED GET: Returning {len(user_list)} users to UI")
        return jsonify({"success": True, "users": user_list})
        
    except Exception as e:
        print(f"❌ FIXED GET ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Failed to fetch users: {str(e)}"}), 500

@api_bp.route('/users/add', methods=['POST'])
@admin_only
@json_required
def add_user():
    """Add a new user (Admin only) - FIXED TO SAVE TO JSON FILE"""
    try:
        print(f"🚀 REAL API FIX: Adding user by {current_user.username}")
        
        USERS_FILE = "/home/h21s/table_tracker_pro/data/users.json"
        
        data = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        role = data.get("role", "staff")
        
        print(f"📝 REAL API: User data: {username}, role: {role}")
        
        # Validation
        if not username or not password:
            return jsonify({"success": False, "error": "Username and password are required"}), 400
        
        if role not in ["admin", "staff"]:
            return jsonify({"success": False, "error": "Role must be admin or staff"}), 400
        
        # Read from JSON file (not Config.DEFAULT_USERS)
        print("   📖 Reading JSON file...")
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
        print(f"   📖 Current users: {list(users.keys())}")
        
        if username in users:
            return jsonify({"success": False, "error": "Username already exists"}), 400
        
        # Add user to JSON file
        print("   ➕ Adding to JSON file...")
        users[username] = {"password": password, "role": role}
        
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        print("   💾 Saved to JSON file")
        
        # Verify
        with open(USERS_FILE, "r") as f:
            verify = json.load(f)
        
        if username in verify:
            print(f"✅ REAL API SUCCESS: {username} saved to JSON file!")
            print(f"   📁 File now has: {list(verify.keys())}")
            return jsonify({
                "success": True,
                "message": f"{role.title()} user {username} created successfully"
            })
        else:
            print(f"❌ REAL API FAILED: {username} not in file after save")
            return jsonify({"success": False, "error": "Failed to save user"}), 500
        
    except Exception as e:
        print(f"❌ REAL API ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route("/users/remove", methods=["POST"])
@admin_only
@json_required
def remove_user():
    """Remove a user (Admin only) - FIXED TO REMOVE FROM JSON FILE"""
    try:
        print(f"🗑️ FIXED REMOVE: Request by admin: {current_user.username}")
        
        USERS_FILE = "/home/h21s/table_tracker_pro/data/users.json"
        
        data = request.get_json()
        username = data.get('username')
        
        print(f"🗑️ FIXED REMOVE: Removing user: {username}")
        
        if not username:
            return jsonify({"success": False, "error": "Username is required"}), 400
        
        if username == current_user.username:
            return jsonify({"success": False, "error": "Cannot remove yourself"}), 400
            
        if username in ['admin']:
            return jsonify({"success": False, "error": "Cannot remove admin user"}), 400
        
        # Read from JSON file
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
        
        print(f"   📖 Before removal: {list(users.keys())}")
        
        if username not in users:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Remove user from JSON file
        del users[username]
        
        # Save back to JSON file
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        # Verify removal
        with open(USERS_FILE, "r") as f:
            verify_users = json.load(f)
        
        if username not in verify_users:
            print(f"   📁 File now has: {list(verify_users.keys())}")
            return jsonify({"success": True, "message": f"User '{username}' removed successfully"})
        else:
            print(f"❌ FIXED REMOVE FAILED: {username} still in file")
            return jsonify({"success": False, "error": "Failed to remove user"}), 500
        
    except Exception as e:
        print(f"❌ FIXED REMOVE ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/customers/<int:customer_id>/edit', methods=['POST'])
@api_login_required
@json_required
def edit_customer(customer_id):
    """Edit customer information"""
    try:
        data = request.get_json()
        new_name = data.get('name', '').strip()
        new_phone = data.get('phone', '').strip()
        
        if not new_name or not new_phone:
            return jsonify({'success': False, 'error': 'Name and phone are required'}), 400
        
        # Validate phone format
        phone_pattern = r'^[\d\s\-\+\(\)]+$'
        import re
        if not re.match(phone_pattern, new_phone):
            return jsonify({'success': False, 'error': 'Invalid phone number format'}), 400
        
        # Update customer in database
        conn = customer_model.get_connection()
        c = conn.cursor()
        
        # Check if phone already exists for another customer
        c.execute("SELECT id FROM customers WHERE phone = ? AND id != ?", (new_phone, customer_id))
        if c.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Phone number already exists for another customer'}), 400
        
        # Update customer
        c.execute("UPDATE customers SET name = ?, phone = ? WHERE id = ?", (new_name, new_phone, customer_id))
        
        if c.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
        
        conn.commit()
        conn.close()
        
        customer_model.export_to_txt()
        
        return jsonify({
            'success': True,
            'message': f'Customer information updated successfully'
        })
        
    except Exception as e:
        print(f"❌ API Error in edit_customer: {e}")
        return jsonify({'success': False, 'error': f'Failed to edit customer: {str(e)}'}), 500

@api_bp.route('/customers/<int:customer_id>/delete', methods=['POST'])
@api_login_required
def delete_customer(customer_id):
    """Delete customer (Admin only)"""
    try:
        if current_user.role != 'admin':
            return jsonify({'success': False, 'error': 'Only admin can delete customers'}), 403
        
        conn = customer_model.get_connection()
        c = conn.cursor()
        
        # Get customer name for confirmation
        c.execute("SELECT name FROM customers WHERE id = ?", (customer_id,))
        customer = c.fetchone()
        
        if not customer:
            conn.close()
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
        
        customer_name = customer[0]
        
        # Delete customer and related transactions
        c.execute("DELETE FROM transactions WHERE customer_id = ?", (customer_id,))
        c.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        
        conn.commit()
        conn.close()
        
        customer_model.export_to_txt()
        
        return jsonify({
            'success': True,
            'message': f'Customer "{customer_name}" deleted successfully'
        })
        
    except Exception as e:
        print(f"❌ API Error in delete_customer: {e}")
        return jsonify({'success': False, 'error': f'Failed to delete customer: {str(e)}'}), 500
