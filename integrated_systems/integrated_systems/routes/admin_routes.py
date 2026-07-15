from flask import Blueprint, render_template
from models import User, Event, Election, Registration, Vote, Candidate, Certificate
from routes.auth_routes import login_required, current_user

bp = Blueprint('admin', __name__, template_folder='../templates')


@bp.route('/admin')
@login_required(role='admin')
def dashboard():
    user = current_user()
    counts = {
        'students': User.query.filter_by(role='student').count(),
        'events': Event.query.count(),
        'active_elections': Election.query.filter_by(status='active').count(),
        'votes_cast': Vote.query.count(),
        'certificates': Certificate.query.count(),
    }
    return render_template('admin_dashboard.html', user=user, counts=counts)


# Management panels (placeholders)
@bp.route('/admin/manage_users')
@login_required(role='admin')
def manage_users():
    user = current_user()
    users = User.query.order_by(User.created_at.desc()).limit(200).all()
    return render_template('admin_manage_users.html', user=user, users=users)


@bp.route('/admin/manage_organizers')
@login_required(role='admin')
def manage_organizers():
    user = current_user()
    organizers = User.query.filter_by(role='organizer').all()
    return render_template('admin_manage_organizers.html', user=user, organizers=organizers)


@bp.route('/admin/manage_events')
@login_required(role='admin')
def manage_events():
    user = current_user()
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template('admin_manage_events.html', user=user, events=events)


@bp.route('/admin/manage_elections')
@login_required(role='admin')
def manage_elections():
    user = current_user()
    elections = Election.query.order_by(Election.created_at.desc()).all()
    return render_template('admin_manage_elections.html', user=user, elections=elections)


@bp.route('/admin/manage_candidates')
@login_required(role='admin')
def manage_candidates():
    user = current_user()
    candidates = Candidate.query.order_by(Candidate.created_at.desc()).all()
    return render_template('admin_manage_candidates.html', user=user, candidates=candidates)


@bp.route('/admin/reports')
@login_required(role='admin')
def reports():
    user = current_user()
    # placeholder: implement real report generation later
    return render_template('admin_reports.html', user=user)


@bp.route('/admin/audit_logs')
@login_required(role='admin')
def audit_logs():
    user = current_user()
    # placeholder: integrate with audit log model/system later
    logs = []
    return render_template('admin_audit_logs.html', user=user, logs=logs)


@bp.route('/admin/settings')
@login_required(role='admin')
def settings():
    user = current_user()
    return render_template('admin_settings.html', user=user)
