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
        
        # Try to authenticate user
        user = User.authenticate(username, password)
        
        if user:
            login_user(user)
            print(f"✅ Login successful: {username} ({user.role})")
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('main.home'))
        else:
            print(f"❌ Login failed: {username}")
            flash('Invalid username or password. Please try again.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    print(f"🚪 Logout: {request.remote_addr}")
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
