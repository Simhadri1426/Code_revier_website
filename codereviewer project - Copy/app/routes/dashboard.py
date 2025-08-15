from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models import CodeSubmission

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    recent_submissions = CodeSubmission.query.filter_by(user_id=current_user.id).order_by(CodeSubmission.timestamp.desc()).limit(5).all()
    return render_template('dashboard.html', submissions=recent_submissions)

@bp.route('/')
def home():
    return render_template('home.html') 