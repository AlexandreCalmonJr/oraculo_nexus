"""
Utilitários para sistema de gamificação
"""
from datetime import datetime, date, timedelta
from flask import flash
import random
from sqlalchemy import func
from app.models import (
    User, Level, Achievement, UserAchievement, Challenge, UserChallenge,
    DailyChallenge, Team, BossFight, BossFightStep, BossFightStage,
    TeamBossProgress, TeamBossCompletion, LearningPath, PathChallenge,
    UserPathProgress, TeamBattle, TeamBattleChallenge
)
from app.extensions import db


def update_user_level(user):
    """
    Atualiza o nível do usuário baseado em seus pontos
    
    Args:
        user: Objeto User
    """
    current_level_id = user.level_id
    new_level = Level.query.filter(Level.min_points <= user.points).order_by(Level.min_points.desc()).first()
    if new_level and new_level.id != current_level_id:
        user.level_id = new_level.id
        flash(f'Subiu de nível! Você agora é {new_level.name}!', 'success')


def check_and_award_achievements(user):
    """
    Verifica e concede conquistas ao usuário
    
    Args:
        user: Objeto User
    """
    user_achievements_ids = {ua.achievement_id for ua in user.achievements}
    potential_achievements = Achievement.query.filter(Achievement.id.notin_(user_achievements_ids)).all()
    if not potential_achievements:
        return
    
    challenges_completed_count = len(user.completed_challenges)
    paths_completed_count = UserPathProgress.query.filter_by(user_id=user.id).count()
    
    for achievement in potential_achievements:
        unlocked = False
        if achievement.trigger_type == 'challenges_completed':
            if challenges_completed_count >= achievement.trigger_value:
                unlocked = True
        elif achievement.trigger_type == 'points_earned':
            if user.points >= achievement.trigger_value:
                unlocked = True
        elif achievement.trigger_type == 'paths_completed':
            if paths_completed_count >= achievement.trigger_value:
                unlocked = True
        elif achievement.trigger_type == 'first_team_join':
            if user.team_id is not None and achievement.trigger_value == 1:
                unlocked = True
        
        if unlocked:
            user_achievement = UserAchievement(user_id=user.id, achievement_id=achievement.id)
            db.session.add(user_achievement)
            flash(f'Nova conquista desbloqueada: {achievement.name}!', 'success')


def check_boss_fight_completion(team_id, boss_id):
    """
    Verifica se uma equipe completou um Boss Fight
    
    Args:
        team_id: ID da equipe
        boss_id: ID do boss fight
    """
    boss = BossFight.query.get(boss_id)
    team = Team.query.get(team_id)
    
    if TeamBossCompletion.query.filter_by(team_id=team_id, boss_fight_id=boss_id).first():
        return
    
    total_steps_required = db.session.query(func.count(BossFightStep.id))\
        .join(BossFightStage).filter(BossFightStage.boss_fight_id == boss_id).scalar()
    
    steps_completed_by_team = TeamBossProgress.query.filter_by(team_id=team_id)\
        .join(BossFightStep).join(BossFightStage)\
        .filter(BossFightStage.boss_fight_id == boss_id).count()
    
    if total_steps_required > 0 and steps_completed_by_team >= total_steps_required:
        for member in team.members:
            member.points += boss.reward_points
            update_user_level(member)
        completion_record = TeamBossCompletion(team_id=team_id, boss_fight_id=boss_id)
        db.session.add(completion_record)
        db.session.commit()
        flash(f'Parabéns Equipe "{team.name}"! Vocês derrotaram o Boss "{boss.name}" e cada membro ganhou {boss.reward_points} pontos!', 'success')


def check_and_complete_paths(user, completed_challenge_id):
    """
    Verifica se o usuário completou alguma trilha de aprendizagem
    
    Args:
        user: Objeto User
        completed_challenge_id: ID do desafio completado
    """
    paths_containing_challenge = PathChallenge.query.filter_by(challenge_id=completed_challenge_id).all()
    if not paths_containing_challenge:
        return
    
    user_completed_challenges = {uc.challenge_id for uc in user.completed_challenges}
    
    for pc in paths_containing_challenge:
        path = pc.path
        if UserPathProgress.query.filter_by(user_id=user.id, path_id=path.id).first():
            continue
        
        all_challenges_in_path = {c.challenge_id for c in path.challenges}
        if all_challenges_in_path.issubset(user_completed_challenges):
            user.points += path.reward_points
            progress = UserPathProgress(user_id=user.id, path_id=path.id)
            db.session.add(progress)
            db.session.commit()
            check_and_award_achievements(user)
            flash(f'Trilha "{path.name}" concluída! Você ganhou {path.reward_points} pontos de bônus!', 'success')


def get_or_create_daily_challenge():
    """
    Obtém ou cria o desafio diário
    
    Returns:
        Objeto DailyChallenge ou None
    """
    today = date.today()
    daily_challenge_entry = DailyChallenge.query.filter_by(day=today).first()
    if daily_challenge_entry:
        return daily_challenge_entry
    
    thirty_days_ago = today - timedelta(days=30)
    recent_daily_ids = [dc.challenge_id for dc in DailyChallenge.query.filter(DailyChallenge.day > thirty_days_ago).all()]
    available_challenges = Challenge.query.filter(Challenge.id.notin_(recent_daily_ids)).all()
    
    if not available_challenges:
        available_challenges = Challenge.query.all()
    
    if available_challenges:
        selected_challenge = random.choice(available_challenges)
        new_daily = DailyChallenge(challenge_id=selected_challenge.id)
        db.session.add(new_daily)
        db.session.commit()
        return new_daily
    return None


def finalize_ended_battles():
    """
    Finaliza batalhas que já terminaram e distribui prêmios
    
    Returns:
        Número de batalhas finalizadas
    """
    ended_battles = TeamBattle.query.filter(
        TeamBattle.status == 'active',
        TeamBattle.end_time <= datetime.utcnow()
    ).all()

    battles_finalized_count = 0
    for battle in ended_battles:
        # Contar quantos desafios cada equipa completou
        challenger_score = TeamBattleChallenge.query.filter(
            TeamBattleChallenge.battle_id == battle.id,
            TeamBattleChallenge.completed_by_team_id == battle.challenging_team_id
        ).count()
        
        challenged_score = TeamBattleChallenge.query.filter(
            TeamBattleChallenge.battle_id == battle.id,
            TeamBattleChallenge.completed_by_team_id == battle.challenged_team_id
        ).count()

        # Determinar o vencedor
        winner = None
        if challenger_score > challenged_score:
            winner = battle.challenging_team
        elif challenged_score > challenger_score:
            winner = battle.challenged_team

        if winner:
            battle.winner_team_id = winner.id
            # Distribuir os pontos para cada membro da equipa vencedora
            for member in winner.members:
                member.points += battle.reward_points
                update_user_level(member)
            flash(f'A equipa "{winner.name}" venceu a batalha contra "{battle.challenged_team.name if winner.id == battle.challenging_team_id else battle.challenging_team.name}"!', 'success')
        
        battle.status = 'completed'
        battles_finalized_count += 1
    
    if battles_finalized_count > 0:
        db.session.commit()
    
    return battles_finalized_count
