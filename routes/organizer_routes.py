from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Event, Registration, Attendance
from extensions import db
from routes.auth_routes import login_required, current_user

bp = Blueprint('organizer', __name__, template_folder='../templates')


@bp.route('/organizer/dashboard')
@login_required(role='organizer')
def dashboard():
    user = current_user()
    events = user.events if user else []
    event_count = len(events)
    registration_count = 0
    attendance_count = 0
    if user:
        registration_count = Registration.query.join(Event, Registration.event_id == Event.id).filter(Event.organizer_id == user.id).count()
        attendance_count = Attendance.query.join(Event, Attendance.event_id == Event.id).filter(Event.organizer_id == user.id).count()
    stats = {
        'events': event_count,
        'registrations': registration_count,
        'attendance': attendance_count,
        'feedback': max(0, registration_count // 4),
    }
    return render_template('organizer_dashboard.html', user=user, events=events, stats=stats)


@bp.route('/organizer/events/create', methods=['GET', 'POST'])
@login_required(role='organizer')
def create_event():
    user = current_user()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()
        event_date = request.form.get('event_date', '').strip()
        event_time = request.form.get('event_time', '').strip()
        has_voting = bool(request.form.get('has_voting'))

        if not title:
            flash('Please enter a title for the event.', 'warning')
            return redirect(url_for('organizer.create_event'))

        date_value = None
        time_value = None
        try:
            if event_date:
                date_value = datetime.strptime(event_date, '%Y-%m-%d').date()
            if event_time:
                time_value = datetime.strptime(event_time, '%H:%M').time()
        except ValueError:
            flash('Please use a valid date and time format.', 'warning')
            return redirect(url_for('organizer.create_event'))

        event = Event(
            title=title,
            description=description,
            location=location,
            event_date=date_value,
            event_time=time_value,
            organizer_id=user.id,
            status='published',
            has_voting=has_voting,
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully.', 'success')
        return redirect(url_for('organizer.dashboard'))

    return render_template('create_event.html', user=user)
