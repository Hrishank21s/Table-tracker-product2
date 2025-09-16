from flask import Blueprint, render_template
from flask_login import login_required

tables_bp = Blueprint('tables', __name__)

@tables_bp.route('/snooker')
@login_required
def snooker():
    return render_template('snooker.html', game_type='snooker')

@tables_bp.route('/pool')
@login_required
def pool():
    return render_template('pool.html', game_type='pool')
