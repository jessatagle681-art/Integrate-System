from flask import Blueprint, render_template
from routes.auth_routes import login_required, current_user
from models import Election, Candidate, Vote

bp = Blueprint('results', __name__, template_folder='../templates')


@bp.route('/elections/results')
@login_required()
def elections_results():
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
