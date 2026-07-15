import os
import sys
from pathlib import Path
from flask import Flask, redirect, session, url_for
from extensions import db

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / 'instance'
INSTANCE_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(BASE_DIR))

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'integrated-portal-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(INSTANCE_DIR / 'integrated_portal.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

db.init_app(app)

from models import User, Event, Registration, Attendance, Certificate, Election, Vote

with app.app_context():
    db.create_all()
    # Ensure new columns exist for lightweight schema updates (SQLite)
    try:
        cols = [r[1] for r in db.engine.execute("PRAGMA table_info('events')").fetchall()]
        if 'image_url' not in cols:
            db.engine.execute("ALTER TABLE events ADD COLUMN image_url VARCHAR(255)")
        if 'event_time' not in cols:
            db.engine.execute("ALTER TABLE events ADD COLUMN event_time TIME")
    except Exception:
        # ignore if DB doesn't support pragma or already updated
        pass
    if not User.query.filter_by(email='admin@school.local').first():
        admin = User(name='Admin User', email='admin@school.local', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
    if not User.query.filter_by(email='organizer@school.local').first():
        organizer = User(name='Organizer User', email='organizer@school.local', role='organizer')
        organizer.set_password('organizer123')
        db.session.add(organizer)
    if not User.query.filter_by(email='student@school.local').first():
        student = User(name='Student User', email='student@school.local', role='student')
        student.set_password('student123')
        db.session.add(student)
    db.session.commit()

from routes.auth_routes import bp as auth_bp
from routes.event_routes import bp as event_bp
from routes.voting_routes import bp as voting_bp
from routes.organizer_routes import bp as organizer_bp
from routes.results_routes import bp as results_bp

app.register_blueprint(auth_bp)
app.register_blueprint(event_bp)
app.register_blueprint(voting_bp)
app.register_blueprint(organizer_bp)
app.register_blueprint(results_bp)


@app.route('/')
def index():
    if session.get('user_id'):
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))


@app.route('/voting/login')
def voting_login_redirect():
    return redirect(url_for('auth.login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
