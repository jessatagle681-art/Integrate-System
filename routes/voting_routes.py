from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Election, Vote, Candidate, Position
from extensions import db
from routes.auth_routes import login_required, current_user

bp = Blueprint('voting', __name__, template_folder='../templates')


@bp.route('/voting')
@login_required()
def index():
    user = current_user()
    elections = Election.query.order_by(Election.created_at.desc()).all()
    active = [e for e in elections if e.status == 'active']
    closed = [e for e in elections if e.status != 'active']
    return render_template('voting.html', active_elections=active, closed_elections=closed, user=user)


# aliases to match required URL structure
@bp.route('/elections')
@login_required()
def elections_alias():
    return index()


@bp.route('/elections/vote/<int:election_id>')
@login_required()
def elections_vote(election_id):
    return ballot(election_id)


@bp.route('/elections/results')
@login_required()
def elections_results_alias():
    return redirect(url_for('results.elections_results'))


@bp.route('/voting/elections')
@login_required()
def elections():
    user = current_user()
    elections = Election.query.order_by(Election.created_at.desc()).all()
    return render_template('elections.html', elections=elections, user=user)


@bp.route('/voting/ballot/<int:election_id>', methods=['GET', 'POST'])
@login_required()
def ballot(election_id):
    user = current_user()
    election = Election.query.get_or_404(election_id)
    existing_vote = Vote.query.filter_by(user_id=user.id, election_id=election.id).first()
    candidates = Candidate.query.filter_by(election_id=election.id).order_by(Candidate.created_at.asc()).all()
    positions = Position.query.filter_by(election_id=election.id).order_by(Position.created_at.asc()).all()
    if request.method == 'POST':
        choice = request.form.get('choice', '').strip()
        if existing_vote:
            flash('You have already voted in this election.', 'info')
            return redirect(url_for('voting.ballot', election_id=election.id))
        if not choice:
            flash('Please choose a candidate.', 'warning')
            return redirect(url_for('voting.ballot', election_id=election.id))
        db.session.add(Vote(election_id=election.id, user_id=user.id, choice=choice))
        db.session.commit()
        flash('Your vote has been recorded.', 'success')
        return redirect(url_for('voting.results'))

    return render_template('ballot.html', election=election, candidates=candidates, positions=positions, existing_vote=existing_vote, user=user)


@bp.route('/voting/results')
@login_required()
def results():
    user = current_user()
    elections = Election.query.order_by(Election.created_at.desc()).all()
    # compute simple results per election
    election_results = {}
    for e in elections:
        cands = Candidate.query.filter_by(election_id=e.id).all()
        counts = []
        for c in cands:
            cnt = Vote.query.filter_by(election_id=e.id, choice=str(c.id)).count()
            counts.append({'candidate': c, 'votes': cnt})
        election_results[e.id] = counts
    return render_template('results.html', elections=elections, user=user, election_results=election_results)


@bp.route('/voting/history')
@login_required()
def history():
    user = current_user()
    votes = Vote.query.filter_by(user_id=user.id).order_by(Vote.created_at.desc()).all()
    # attach candidate info when possible
    enriched = []
    for v in votes:
        cand = None
        try:
            cand = Candidate.query.get(int(v.choice)) if v.choice and v.choice.isdigit() else None
        except Exception:
            cand = None
        enriched.append({'vote': v, 'candidate': cand})
    return render_template('voting_history.html', votes=enriched, user=user)
