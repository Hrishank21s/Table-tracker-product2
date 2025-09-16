from flask import Blueprint, render_template
from flask_login import login_required

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/billing')
@login_required
def billing():
    return render_template('billing.html')
