from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        print(f"🔐 Login attempt: {username}")
        
        # Use our fresh user system
        all_users = User.get_all_users()
        print(f"📋 Available users: {list(all_users.keys())}")
        
        if username in all_users and all_users[username]['password'] == password:
            user_data = all_users[username]
            user = User(username, user_data['password'], user_data['role'])
            login_user(user)
            print(f"✅ Login successful: {username}")
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('main.home'))
        else:
            print(f"❌ Login failed: {username}")
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    print(f"🚪 Logout")
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
