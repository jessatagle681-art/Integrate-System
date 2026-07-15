from flask import Blueprint, render_template, redirect, request, session, url_for, flash
from werkzeug.security import check_password_hash
from models import User
from extensions import db

bp = Blueprint('auth', __name__, template_folder='../templates')


def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return db.session.get(User, user_id)


def login_required(role=None):
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = current_user()
            if not user or not user.is_active:
                return redirect(url_for('auth.login'))
            if role and user.role != role:
                flash('You are not authorized to access that page.', 'danger')
                return redirect(url_for('auth.dashboard'))
            return func(*args, **kwargs)

        return wrapper

    return decorator


@bp.route('/login', methods=['GET', 'POST'])
def login():
    user = current_user()
    if user:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['user_name'] = user.name
            flash('Welcome back!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            if user.role == 'organizer':
                return redirect(url_for('organizer.dashboard'))
            return redirect(url_for('auth.dashboard'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return redirect(url_for('auth.register'))
        # restrict creating admin accounts via register; only allow student/organizer
        if role not in ('student', 'organizer'):
            role = 'student'
        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Account created. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')


@bp.route('/profile')
@login_required()
def profile():
    user = current_user()
    return render_template('profile.html', user=user)


@bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/dashboard')
@login_required()
def dashboard():
    user = current_user()
    if user.role == 'organizer':
        return redirect(url_for('organizer.dashboard'))

    # compute student dashboard statistics
    from datetime import date
    from models import Registration, Event, Election, Certificate

    stats = {
        'registered_events': Registration.query.filter_by(user_id=user.id).count(),
        'upcoming_events': Event.query.join(Registration, Registration.event_id == Event.id)
            .filter(Registration.user_id == user.id)
            .filter(Event.event_date >= date.today())
            .count(),
        'active_elections': Election.query.filter_by(status='active').count(),
        'certificates_earned': Certificate.query.filter_by(user_id=user.id).count(),
    }

    return render_template('student_dashboard.html', user=user, stats=stats)


@bp.route('/')
def index():
    return redirect(url_for('auth.login'))
