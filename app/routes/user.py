"""
Rotas de usuário (dashboard, perfil, ranking)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
import cloudinary.uploader

from app.extensions import db
from app.models import User, Team, Challenge, UserChallenge, ScavengerHunt, UserHuntProgress, GlobalEvent
from app.utils import get_or_create_daily_challenge

user_bp = Blueprint('user', __name__)


@user_bp.route('/')
@login_required
def index():
    """Dashboard principal"""
    daily_challenge = get_or_create_daily_challenge()
    active_hunt = ScavengerHunt.query.filter_by(is_active=True).first()
    hunt_progress = None
    if active_hunt:
        hunt_progress = UserHuntProgress.query.filter_by(user_id=current_user.id, hunt_id=active_hunt.id).first()
    
    active_event = GlobalEvent.query.filter(
        GlobalEvent.is_active == True,
        GlobalEvent.end_date >= datetime.utcnow(),
        GlobalEvent.current_hp > 0
    ).first()

    event_progress = 0
    if active_event:
        event_progress = ((active_event.total_hp - active_event.current_hp) / active_event.total_hp) * 100

    return render_template('user/dashboard.html', 
                            daily_challenge=daily_challenge,
                            active_hunt=active_hunt, 
                            hunt_progress=hunt_progress,
                            active_event=active_event,      
                            event_progress=event_progress)


@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Perfil do usuário"""
    if request.method == 'POST':
        current_user.phone = request.form.get('phone')
        file = request.files.get('avatar')
        if file and file.filename:
            try:
                upload_result = cloudinary.uploader.upload(file, folder="avatars")
                current_user.avatar_url = upload_result['secure_url']
            except Exception as e:
                flash(f'Erro ao fazer upload do avatar: {e}', 'error')
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html')


@user_bp.route('/ranking')
@login_required
def ranking():
    """Ranking de usuários e equipes"""
    ranked_users = User.query.order_by(User.points.desc()).all()
    all_teams = Team.query.all()
    ranked_teams = sorted(all_teams, key=lambda t: t.total_points, reverse=True)
    
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_leaders = db.session.query(
        User, func.sum(Challenge.points_reward).label('monthly_points')
    ).join(UserChallenge, User.id == UserChallenge.user_id)\
     .join(Challenge, Challenge.id == UserChallenge.challenge_id)\
     .filter(UserChallenge.completed_at >= start_of_month)\
     .group_by(User).order_by(func.sum(Challenge.points_reward).desc()).limit(10).all()
    
    start_of_week = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    weekly_leaders = db.session.query(
        User, func.sum(Challenge.points_reward).label('weekly_points')
    ).join(UserChallenge, User.id == UserChallenge.user_id)\
     .join(Challenge, Challenge.id == UserChallenge.challenge_id)\
     .filter(UserChallenge.completed_at >= start_of_week)\
     .group_by(User).order_by(func.sum(Challenge.points_reward).desc()).limit(10).all()
    
    return render_template(
        'user/ranking.html', 
        ranked_users=ranked_users, 
        ranked_teams=ranked_teams,
        monthly_leaders=monthly_leaders,
        weekly_leaders=weekly_leaders
    )


@user_bp.route('/hunt/start/<int:hunt_id>', methods=['POST'])
@login_required
def start_hunt(hunt_id):
    """Iniciar caça ao tesouro"""
    hunt = ScavengerHunt.query.get_or_404(hunt_id)
    existing_progress = UserHuntProgress.query.filter_by(user_id=current_user.id, hunt_id=hunt.id).first()
    if not existing_progress:
        new_progress = UserHuntProgress(user_id=current_user.id, hunt_id=hunt.id, current_step=1)
        db.session.add(new_progress)
        db.session.commit()
        flash('Você começou a caça ao tesouro! Boa sorte!', 'success')
    return redirect(url_for('user.index'))
