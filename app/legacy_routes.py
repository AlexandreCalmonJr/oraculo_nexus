"""
Rotas legadas do app.py original
Este arquivo contém temporariamente todas as rotas que ainda não foram modularizadas
Gradualmente, essas rotas serão movidas para blueprints apropriados
"""
from flask import render_template, request, jsonify, flash, redirect, url_for, session, send_file
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta
from sqlalchemy.orm import aliased
from sqlalchemy import func
import os
import csv
import json
import re
import random
import io
import cloudinary.uploader
from datetime import datetime, timedelta

from app.extensions import db
from app.models import *
from app.forms import BaseForm
from app.utils import *


def register_routes(app):
    """Registra todas as rotas legadas na aplicação"""

    # --- ROTAS FALTANTES (Portadas de app_original.py) ---
    @app.route('/')
    @login_required
    def index():
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

        return render_template('dashboard.html', 
                                daily_challenge=daily_challenge,
                                active_hunt=active_hunt, 
                                hunt_progress=hunt_progress,
                                active_event=active_event,      
                                event_progress=event_progress)

    @app.route('/hunt/start/<int:hunt_id>', methods=['POST'])
    @login_required
    def start_hunt(hunt_id):
        hunt = ScavengerHunt.query.get_or_404(hunt_id)
        existing_progress = UserHuntProgress.query.filter_by(user_id=current_user.id, hunt_id=hunt.id).first()
        if not existing_progress:
            new_progress = UserHuntProgress(user_id=current_user.id, hunt_id=hunt.id, current_step=1)
            db.session.add(new_progress)
            db.session.commit()
            flash('Você começou a caça ao tesouro! Boa sorte!', 'success')
        return redirect(url_for('index'))

    @app.route('/ranking')
    @login_required
    def ranking():
        ranked_users = User.query.order_by(User.points.desc()).all()
        all_teams = Team.query.all()
        ranked_teams = sorted(all_teams, key=lambda t: t.total_points, reverse=True)
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_leaders = db.session.query(
            User, func.sum(Challenge.points_reward).label('monthly_points')
        ).join(UserChallenge, User.id == UserChallenge.user_id).join(Challenge, Challenge.id == UserChallenge.challenge_id).filter(UserChallenge.completed_at >= start_of_month).group_by(User).order_by(func.sum(Challenge.points_reward).desc()).limit(10).all()
        start_of_week = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        weekly_leaders = db.session.query(
            User, func.sum(Challenge.points_reward).label('weekly_points')
        ).join(UserChallenge, User.id == UserChallenge.user_id).join(Challenge, Challenge.id == UserChallenge.challenge_id).filter(UserChallenge.completed_at >= start_of_week).group_by(User).order_by(func.sum(Challenge.points_reward).desc()).limit(10).all()
        return render_template(
            'ranking.html', 
            ranked_users=ranked_users, 
            ranked_teams=ranked_teams,
            monthly_leaders=monthly_leaders,
            weekly_leaders=weekly_leaders
        )
    
    # --- ROTAS DE CHAT ---
    @app.route('/chat-page')
    @login_required
    def chat_page():
        session.pop('faq_selection', None)
        return render_template('chat/chat.html')
    
    @app.route('/chat', methods=['POST'])
    @login_required
    def chat():
        data = request.get_json()
        mensagem = data.get('mensagem', '').strip()
        
        active_hunt = ScavengerHunt.query.filter_by(is_active=True).first()
        if active_hunt:
            progress = UserHuntProgress.query.filter_by(user_id=current_user.id, hunt_id=active_hunt.id).first()
            if progress and not progress.completed_at:
                current_step_info = ScavengerHuntStep.query.filter_by(hunt_id=active_hunt.id, step_number=progress.current_step).first()
                
                if current_step_info and current_step_info.target_identifier.lower() in mensagem.lower():
                    next_step_info = ScavengerHuntStep.query.filter_by(hunt_id=active_hunt.id, step_number=progress.current_step + 1).first()
                    
                    if next_step_info:
                        progress.current_step += 1
                        db.session.commit()
                        resposta_caca = f"🎉 **Pista Encontrada!**<br><br>{current_step_info.hidden_clue}<br><br><strong>Próxima Pista:</strong> {next_step_info.clue_text}"
                        return jsonify({'text': resposta_caca, 'html': True, 'state': 'normal', 'options': []})
                    else:
                        progress.completed_at = datetime.utcnow()
                        current_user.points += active_hunt.reward_points
                        update_user_level(current_user)
                        check_and_award_achievements(current_user)
                        db.session.commit()
                        resposta_final = f"🏆 **Parabéns!** Você completou a caça ao tesouro '{active_hunt.name}' e ganhou {active_hunt.reward_points} pontos! A última pista era: {current_step_info.hidden_clue}"
                        return jsonify({'text': resposta_final, 'html': True, 'state': 'normal', 'options': []})
                    
        resposta = {
            'text': "Desculpe, não entendi. Tente reformular a pergunta.",
            'html': False,
            'state': 'normal',
            'options': [],
            'suggestion': None
        }
        
        ticket_response = process_ticket_command(mensagem)
        if ticket_response:
            resposta['text'] = ticket_response
            return jsonify(resposta)
        
        solution_response = suggest_solution(mensagem)
        if solution_response:
            resposta['text'] = solution_response
            return jsonify(resposta)
        
        faq_matches = find_faq_by_nlp(mensagem)
        if faq_matches:
            if len(faq_matches) == 1:
                faq = faq_matches[0]
                resposta['text'] = format_faq_response(faq.id, faq.question, faq.answer, faq.image_url, faq.video_url, faq.file_name)
                resposta['html'] = True
                
                from app.utils.faq_utils import nlp
                if nlp:
                    doc = nlp(faq.question.lower())
                    keywords = {token.lemma_ for token in doc if not token.is_stop and not token.is_punct and token.pos_ == 'NOUN'}
                    if keywords:
                        relevant_challenge = Challenge.query.filter(Challenge.title.ilike(f'%{next(iter(keywords))}%')).first()
                        if relevant_challenge:
                            is_completed = UserChallenge.query.filter_by(user_id=current_user.id, challenge_id=relevant_challenge.id).first()
                            if not is_completed:
                                resposta['suggestion'] = {
                                    'text': f"Parece que você está interessado neste tópico! Que tal tentar o desafio '{relevant_challenge.title}' e ganhar {relevant_challenge.points_reward} pontos?",
                                    'challenge_id': relevant_challenge.id
                                }
            else:
                faq_ids = [faq.id for faq in faq_matches]
                session['faq_selection'] = faq_ids
                resposta['state'] = 'faq_selection'
                resposta['text'] = "Encontrei várias FAQs relacionadas. Clique na que você deseja:"
                resposta['html'] = True
                resposta['options'] = [{'id': faq.id, 'question': faq.question} for faq in faq_matches][:5]
        else:
            resposta['text'] = "Nenhuma FAQ encontrada para a sua busca. Tente reformular a pergunta."
        
        return jsonify(resposta)
    
    @app.route('/chat/faq_select', methods=['POST'])
    @login_required
    def chat_faq_select():
        data = request.get_json()
        faq_id = data.get('faq_id')
        if not faq_id:
            return jsonify({'text': 'ID da FAQ não fornecido.', 'html': True}), 400
        faq = FAQ.query.get(faq_id)
        if not faq:
            return jsonify({'text': 'FAQ não encontrada.', 'html': True}), 404
        response_text = format_faq_response(
            faq.id, faq.question, faq.answer,
            faq.image_url, faq.video_url, faq.file_name
        )
        return jsonify({
            'text': response_text,
            'html': True,
            'state': 'normal',
            'options': []
        })
    
    @app.route('/chat/feedback', methods=['POST'])
    @login_required
    def chat_feedback():
        data = request.get_json()
        message_id = data.get('message_id')
        feedback_type = data.get('feedback')
        message = ChatMessage.query.get(message_id)
        if message and message.user_id == current_user.id:
            message.feedback = feedback_type
            db.session.commit()
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': 'Mensagem não encontrada ou não autorizada'}), 404
    
    # --- ROTAS DE FAQ ---
    @app.route('/faqs', methods=['GET'])
    @login_required
    def faqs():
        categories = Category.query.all()
        faqs = FAQ.query.all()
        faq_to_edit = None
        if request.args.get('edit'):
            faq_id = request.args.get('edit')
            faq_to_edit = FAQ.query.get_or_404(faq_id)
        return render_template('faq/faqs.html', faqs=faqs, categories=categories, faq_to_edit=faq_to_edit)

    @app.route('/admin/faqs', methods=['GET', 'POST'])
    @login_required
    def admin_faq():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        
        form = BaseForm()
        categories = Category.query.all()
        
        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Erro de validação CSRF.', 'error')
                return redirect(url_for('admin_faq'))
            
            action = request.form.get('action')
            
            if action == 'create_faq':
                category_id = request.form['category']
                question = request.form['question']
                answer = request.form['answer']
                image_url = request.form.get('image_url') or None
                video_url = request.form.get('video_url') or None
                
                file = request.files.get('file')
                file_name = None
                file_data = None
                if file and file.filename:
                    file_name = file.filename
                    file_data = file.read()
                
                new_faq = FAQ(
                    category_id=category_id,
                    question=question,
                    answer=answer,
                    image_url=image_url,
                    video_url=video_url,
                    file_name=file_name,
                    file_data=file_data
                )
                db.session.add(new_faq)
                db.session.commit()
                flash('FAQ criada com sucesso!', 'success')
                return redirect(url_for('admin_faq'))
            
            elif action == 'create_category':
                category_name = request.form['category_name']
                if not Category.query.filter_by(name=category_name).first():
                    new_category = Category(name=category_name)
                    db.session.add(new_category)
                    db.session.commit()
                    flash('Categoria criada com sucesso!', 'success')
                else:
                    flash('Categoria já existe.', 'warning')
                return redirect(url_for('admin_faq'))
        
        all_faqs = FAQ.query.all()
        return render_template('admin/admin_faq.html', faqs=all_faqs, categories=categories, form=form)

    @app.route('/faqs/edit/<int:faq_id>', methods=['GET', 'POST'])
    @login_required
    def edit_faq(faq_id):
        if not current_user.is_admin:
            flash('Acesso negado. Apenas administradores podem gerenciar FAQs.', 'error')
            return redirect(url_for('faqs'))
        faq = FAQ.query.get_or_404(faq_id)
        if request.method == 'POST':
            faq.category_id = request.form['edit_category']
            faq.question = request.form['edit_question']
            faq.answer = request.form['edit_answer']
            faq.image_url = request.form.get('edit_image_url') or None
            faq.video_url = request.form.get('edit_video_url') or None
            file = request.files.get('edit_file')
            if file and file.filename:
                faq.file_name = file.filename
                faq.file_data = file.read()
            db.session.commit()
            flash('FAQ atualizada com sucesso!', 'success')
            return redirect(url_for('faqs'))
        return redirect(url_for('faqs', edit=faq_id))

    @app.route('/faqs/delete/<int:faq_id>', methods=['POST'])
    @login_required
    def delete_faq(faq_id):
        if not current_user.is_admin:
            flash('Acesso negado. Apenas administradores podem gerenciar FAQs.', 'error')
            return redirect(url_for('faqs'))
        faq = FAQ.query.get_or_404(faq_id)
        db.session.delete(faq)
        db.session.commit()
        flash('FAQ excluída com sucesso!', 'success')
        return redirect(url_for('faqs'))

    @app.route('/faqs/delete-multiple', methods=['POST'])
    @login_required
    def delete_multiple_faqs():
        if not current_user.is_admin:
            flash('Acesso negado. Apenas administradores podem gerenciar FAQs.', 'error')
            return redirect(url_for('faqs'))
        faq_ids = request.form.getlist('faq_ids')
        if faq_ids:
            FAQs_to_delete = FAQ.query.filter(FAQ.id.in_(faq_ids)).all()
            for faq in FAQs_to_delete:
                db.session.delete(faq)
            db.session.commit()
            flash(f'{len(faq_ids)} FAQs excluídas com sucesso!', 'success')
        else:
            flash('Nenhuma FAQ selecionada para exclusão.', 'error')
        return redirect(url_for('faqs'))

    @app.route('/download/<int:faq_id>')
    @login_required
    def download(faq_id):
        faq = FAQ.query.get_or_404(faq_id)
        if faq.file_data:
            return send_file(io.BytesIO(faq.file_data), download_name=faq.file_name, as_attachment=True)
        flash('Nenhum arquivo encontrado.', 'error')
        return redirect(url_for('faqs'))

    # --- ROTAS DE CONVITE ---
    @app.route('/generate_invitation', methods=['POST'])
    @login_required
    def generate_invitation():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_users'))
        code = generate_invitation_code()
        return jsonify({'code': code})

    # --- ROTAS DE DESAFIOS ---
    @app.route('/challenges')
    @login_required
    def list_challenges():
        if not current_user.level:
            flash('Não foi possível determinar o seu nível. Contate o suporte.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        completed_challenges_ids = [uc.challenge_id for uc in current_user.completed_challenges]
        user_min_points = current_user.level.min_points
        RequiredLevel = aliased(Level)
        all_challenges_query = db.session.query(Challenge).filter(Challenge.id.notin_(completed_challenges_ids))
        all_challenges_query = all_challenges_query.join(RequiredLevel, Challenge.level_required == RequiredLevel.name)
        unlocked_challenges = all_challenges_query.filter(RequiredLevel.min_points <= user_min_points).all()
        locked_challenges = all_challenges_query.filter(RequiredLevel.min_points > user_min_points).all()
        return render_template('challenges/challenges.html', unlocked_challenges=unlocked_challenges, locked_challenges=locked_challenges, form=form)

    @app.route('/challenges/hint/<int:challenge_id>', methods=['POST'])
    @login_required
    def get_challenge_hint(challenge_id):
        challenge = Challenge.query.get_or_404(challenge_id)
        if not challenge.hint:
            return jsonify({'error': 'Este desafio não possui dica.'}), 404
        
        if current_user.points < challenge.hint_cost:
            return jsonify({'error': 'Você não tem pontos suficientes para comprar esta dica.'}), 400
        
        current_user.points -= challenge.hint_cost
        db.session.commit()
        
        return jsonify({'hint': challenge.hint, 'new_points': current_user.points})

    @app.route('/challenges/submit/<int:challenge_id>', methods=['POST'])
    @login_required
    def submit_challenge(challenge_id):
        challenge = Challenge.query.get_or_404(challenge_id)
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('list_challenges'))
            
        submitted_answer = request.form.get('answer').strip()
        
        is_correct = False
        if challenge.challenge_type == 'code':
            is_correct = submitted_answer == challenge.expected_answer
        else:
            is_correct = submitted_answer.lower() == challenge.expected_answer.lower()

        if is_correct:
            existing_completion = UserChallenge.query.filter_by(user_id=current_user.id, challenge_id=challenge_id).first()
            if not existing_completion:
                current_user.points += challenge.points_reward
                flash_message = f'Parabéns! Completou o desafio "{challenge.title}" e ganhou {challenge.points_reward} pontos!'
                
                today_challenge_entry = DailyChallenge.query.filter_by(day=date.today()).first()
                if today_challenge_entry and today_challenge_entry.challenge_id == challenge.id:
                    current_user.points += today_challenge_entry.bonus_points
                    flash_message += f' Você ganhou {today_challenge_entry.bonus_points} pontos de bônus por completar o desafio do dia!'
                
                completion = UserChallenge(user_id=current_user.id, challenge_id=challenge_id)
                db.session.add(completion)

                # Lógica do Evento Global (World Boss)
                active_event = GlobalEvent.query.filter(
                    GlobalEvent.is_active == True,
                    GlobalEvent.start_date <= datetime.utcnow(),
                    GlobalEvent.end_date >= datetime.utcnow(),
                    GlobalEvent.current_hp > 0
                ).first()

                if active_event:
                    damage = challenge.points_reward
                    active_event.current_hp = max(0, active_event.current_hp - damage)
                    contribution = GlobalEventContribution.query.filter_by(event_id=active_event.id, user_id=current_user.id).first()
                    if contribution:
                        contribution.contribution_points += damage
                    else:
                        contribution = GlobalEventContribution(event_id=active_event.id, user_id=current_user.id, contribution_points=damage)
                        db.session.add(contribution)
                    flash(f'Você causou {damage} de dano ao Boss Global!', 'success')
                    if active_event.current_hp == 0:
                        flash(f'O Boss Global "{active_event.name}" foi derrotado!', 'success')

                # Lógica da Batalha de Equipas
                if current_user.team:
                    active_battles = TeamBattle.query.filter(
                        (TeamBattle.challenging_team_id == current_user.team_id) | (TeamBattle.challenged_team_id == current_user.team_id),
                        TeamBattle.status == 'active'
                    ).all()

                    for battle in active_battles:
                        battle_challenge = TeamBattleChallenge.query.filter_by(battle_id=battle.id, challenge_id=challenge_id).first()
                        if battle_challenge and not battle_challenge.completed_by_team_id:
                            battle_challenge.completed_by_team_id = current_user.team_id
                            battle_challenge.completed_at = datetime.utcnow()
                            flash(f'A sua equipa marcou pontos na batalha contra "{battle.challenged_team.name if battle.challenging_team_id == current_user.team_id else battle.challenging_team.name}"!', 'info')

                check_and_complete_paths(current_user, challenge_id)
                update_user_level(current_user)
                db.session.commit()
                check_and_award_achievements(current_user)
                db.session.commit()
                flash(flash_message, 'success')
            else:
                flash('Você já completou este desafio.', 'info')
        else:
            flash('Resposta incorreta. Tente novamente!', 'error')
            
        return redirect(url_for('list_challenges'))

    # --- ROTAS DE TIMES ---
    @app.route('/teams', methods=['GET', 'POST'])
    @login_required
    def teams_list():
        form = BaseForm()
        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Erro de validação.', 'error')
                return redirect(url_for('teams_list'))
                
            if current_user.team_id:
                flash('Você já pertence a uma equipe. Saia da sua equipe atual para criar uma nova.', 'error')
                return redirect(url_for('teams_list'))
            team_name = request.form.get('team_name')
            if Team.query.filter_by(name=team_name).first():
                flash('Já existe uma equipe com este nome.', 'error')
            else:
                new_team = Team(name=team_name, owner_id=current_user.id)
                db.session.add(new_team)
                db.session.commit()
                current_user.team = new_team
                db.session.commit()
                flash(f'Equipe "{team_name}" criada com sucesso!', 'success')
            return redirect(url_for('teams_list'))
                
        all_teams = Team.query.all()
        active_battles = []
        if current_user.team:
            active_battles = TeamBattle.query.filter(
                (TeamBattle.challenging_team_id == current_user.team_id) | (TeamBattle.challenged_team_id == current_user.team_id),
                TeamBattle.status == 'active'
            ).all()

        return render_template('teams/teams.html', teams=all_teams, form=form, active_battles=active_battles)

    @app.route('/team/<int:team_id>')
    @login_required
    def view_team(team_id):
        team = Team.query.get_or_404(team_id)
        team_challenges = Challenge.query.filter_by(is_team_challenge=True).all()
        return render_template('teams/view_team.html', team=team, team_challenges=team_challenges)

    @app.route('/teams/join/<int:team_id>', methods=['POST'])
    @login_required
    def join_team(team_id):
        if current_user.team_id:
            flash('Você já pertence a uma equipe.', 'error')
            return redirect(url_for('teams_list'))
        team_to_join = Team.query.get_or_404(team_id)
        current_user.team = team_to_join
        db.session.commit()
        check_and_award_achievements(current_user)
        db.session.commit()
        flash(f'Você entrou na equipe "{team_to_join.name}"!', 'success')
        return redirect(url_for('teams_list'))

    @app.route('/teams/leave', methods=['POST'])
    @login_required
    def leave_team():
        if not current_user.team_id:
            flash('Você não pertence a nenhuma equipe.', 'error')
            return redirect(url_for('teams_list'))
        team = current_user.team
        if team.owner_id == current_user.id:
            flash('Você é o dono da equipe e não pode sair. Considere transferir a posse ou dissolver a equipe.', 'warning')
            return redirect(url_for('teams_list'))
        current_user.team_id = None
        db.session.commit()
        flash(f'Você saiu da equipe "{team.name}".', 'success')
        return redirect(url_for('teams_list'))

    @app.route('/teams/manage')
    @login_required
    def manage_team():
        if not current_user.team or current_user.id != current_user.team.owner_id:
            flash('Você não é o dono de uma equipe para gerenciá-la.', 'error')
            return redirect(url_for('teams_list'))
        team = current_user.team
        return render_template('teams/manage_team.html', team=team)

    @app.route('/teams/kick/<int:user_id>', methods=['POST'])
    @login_required
    def kick_from_team(user_id):
        team = current_user.team
        if not team or current_user.id != team.owner_id:
            flash('Acesso negado.', 'error')
            return redirect(url_for('teams_list'))
        user_to_kick = User.query.get_or_404(user_id)
        if user_to_kick in team.members:
            user_to_kick.team_id = None
            db.session.commit()
            flash(f'{user_to_kick.name} foi expulso da equipe.', 'success')
        else:
            flash('Este usuário não faz parte da sua equipe.', 'error')
        return redirect(url_for('manage_team'))

    # --- ROTAS DE ADMIN ---
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        stats = {
            'total_users': User.query.count(),
            'total_faqs': FAQ.query.count(),
            'total_teams': Team.query.count(),
            'total_challenges_completed': UserChallenge.query.count(),
        }
        return render_template('admin/admin_dashboard.html', stats=stats)

    @app.route('/admin/users')
    @login_required
    def admin_users():
        if not current_user.is_admin:
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        all_users = User.query.order_by(User.name).all()
        return render_template('admin/admin_users.html', users=all_users, form=form)

    @app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
    @login_required
    def toggle_admin(user_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_users'))
        
        user = User.query.get_or_404(user_id)
        
        # Não permitir remover admin do próprio usuário
        if user.id == current_user.id:
            flash('Você não pode alterar seu próprio status de administrador.', 'error')
            return redirect(url_for('admin_users'))
        
        # Alternar status de admin
        user.is_admin = not user.is_admin
        db.session.commit()
        
        status = 'administrador' if user.is_admin else 'usuário normal'
        flash(f'Usuário {user.name} agora é {status}.', 'success')
        return redirect(url_for('admin_users'))

    @app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
    @login_required
    def admin_delete_user(user_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_users'))
        
        user = User.query.get_or_404(user_id)
        
        # Não permitir deletar o próprio usuário
        if user.id == current_user.id:
            flash('Você não pode deletar sua própria conta.', 'error')
            return redirect(url_for('admin_users'))
        
        # Deletar usuário e dados relacionados
        user_name = user.name
        
        # Remover de equipe se pertencer a alguma
        if user.team_id:
            team = user.team
            user.team_id = None
            # Se era o dono da equipe, deletar a equipe
            if team.owner_id == user.id:
                db.session.delete(team)
        
        # Deletar registros relacionados
        UserChallenge.query.filter_by(user_id=user.id).delete()
        UserPathProgress.query.filter_by(user_id=user.id).delete()
        UserHuntProgress.query.filter_by(user_id=user.id).delete()
        
        db.session.delete(user)
        db.session.commit()
        
        flash(f'Usuário {user_name} foi deletado com sucesso.', 'success')
        return redirect(url_for('admin_users'))

    @app.route('/admin/export_faqs')
    @login_required
    def export_faqs():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        
        faqs = FAQ.query.all()
        faqs_data = []
        
        for faq in faqs:
            faq_dict = {
                'id': faq.id,
                'category': faq.category.name if faq.category else None,
                'question': faq.question,
                'answer': faq.answer,
                'image_url': faq.image_url,
                'video_url': faq.video_url,
                'file_name': faq.file_name,
                'created_at': faq.created_at.isoformat() if faq.created_at else None
            }
            faqs_data.append(faq_dict)
        
        # Criar resposta JSON para download
        response = jsonify({'faqs': faqs_data})
        response.headers['Content-Disposition'] = 'attachment; filename=faqs_export.json'
        response.headers['Content-Type'] = 'application/json'
        
        return response

    @app.route('/admin/teams', methods=['GET'])
    @login_required
    def admin_teams():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        all_teams = Team.query.all()
        return render_template('admin/admin_teams.html', teams=all_teams, form=form)

    @app.route('/admin/delete_team/<int:team_id>', methods=['POST'])
    @login_required
    def admin_delete_team(team_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_teams'))
        team = Team.query.get_or_404(team_id)
        for member in team.members:
            member.team_id = None
        db.session.delete(team)
        db.session.commit()
        flash('Time dissolvido com sucesso!', 'success')
        return redirect(url_for('admin_teams'))

    @app.route('/admin/levels', methods=['GET', 'POST'])
    @login_required
    def admin_levels():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Erro de validação CSRF.', 'error')
                return redirect(url_for('admin_levels'))
            action = request.form.get('action')
            if action == 'create_level':
                name = request.form['name']
                min_points = request.form['min_points']
                insignia_file = request.files.get('insignia_image')
                insignia_url = None
                if insignia_file:
                    upload_result = cloudinary.uploader.upload(insignia_file)
                    insignia_url = upload_result['secure_url']
                level = Level(name=name, min_points=min_points, insignia=insignia_url)
                db.session.add(level)
                db.session.commit()
                flash('Nível criado com sucesso!', 'success')
            elif action == 'import_levels':
                file = request.files['level_file']
                if file and file.filename.endswith('.json'):
                    try:
                        data = json.load(file)
                        for level_data in data:
                            level = Level(
                                name=level_data['name'],
                                min_points=level_data['min_points'],
                                insignia=level_data.get('insignia')
                            )
                            db.session.add(level)
                        db.session.commit()
                        flash('Níveis importados com sucesso!', 'success')
                    except Exception as e:
                        flash(f'Erro ao importar níveis: {str(e)}', 'error')
                else:
                    flash('Por favor, envie um arquivo JSON válido.', 'error')
            return redirect(url_for('admin_levels'))
        levels = Level.query.all()
        return render_template('admin/admin_levels.html', levels=levels, form=form)

    @app.route('/admin/delete_level/<int:level_id>', methods=['POST'])
    @login_required
    def admin_delete_level(level_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_levels'))
        level = Level.query.get_or_404(level_id)
        db.session.delete(level)
        db.session.commit()
        flash('Nível excluído com sucesso!', 'success')
        return redirect(url_for('admin_levels'))

    @app.route('/admin/challenges', methods=['GET', 'POST'])
    @login_required
    def admin_challenges():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Erro de validação CSRF.', 'error')
                return redirect(url_for('admin_challenges'))
            action = request.form.get('action')
            if action == 'create_challenge':
                challenge = Challenge(
                    title=request.form['title'],
                    description=request.form['description'],
                    level_required=request.form['level_required'],
                    points_reward=request.form['points_reward'],
                    challenge_type=request.form['challenge_type'],
                    expected_answer=request.form['expected_answer'],
                    expected_output=request.form.get('expected_output'),
                    hint=request.form.get('hint'),
                    hint_cost=request.form.get('hint_cost', 5),
                    is_team_challenge='is_team_challenge' in request.form
                )
                db.session.add(challenge)
                db.session.commit()
                flash('Desafio criado com sucesso!', 'success')
            elif action == 'import_challenges':
                file = request.files.get('challenge_file')
                if file and file.filename.endswith('.json'):
                    try:
                        data = json.load(file)
                        for challenge_data in data:
                            challenge = Challenge(
                                title=challenge_data['title'],
                                description=challenge_data['description'],
                                level_required=challenge_data['level_required'],
                                points_reward=challenge_data.get('points_reward', 10),
                                expected_answer=challenge_data['expected_answer'],
                                challenge_type=challenge_data.get('challenge_type', 'text'),
                                expected_output=challenge_data.get('expected_output'),
                                hint=challenge_data.get('hint'),
                                hint_cost=challenge_data.get('hint_cost', 5),
                                is_team_challenge=challenge_data.get('is_team_challenge', False)
                            )
                            db.session.add(challenge)
                        db.session.commit()
                        flash('Desafios importados com sucesso!', 'success')
                    except Exception as e:
                        flash(f'Erro ao importar desafios: {str(e)}', 'error')
                else:
                    flash('Por favor, envie um arquivo JSON válido.', 'error')
            return redirect(url_for('admin_challenges'))
        challenges = Challenge.query.all()
        levels = Level.query.all()
        faqs = FAQ.query.all()
        challenge_to_edit = None
        return render_template('admin/admin_challenges.html', challenges=challenges, levels=levels, faqs=faqs, challenge_to_edit=challenge_to_edit, form=form)

    @app.route('/admin/paths', methods=['GET', 'POST'])
    @login_required
    def admin_paths():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Erro de validação CSRF.', 'error')
                return redirect(url_for('admin_paths'))
            action = request.form.get('action')
            if action == 'create_path':
                new_path = LearningPath(
                    name=request.form['name'],
                    description=request.form.get('description'),
                    reward_points=request.form.get('reward_points', 100, type=int),
                    is_active='is_active' in request.form
                )
                db.session.add(new_path)
                db.session.commit()
                flash('Nova trilha de aprendizagem criada com sucesso!', 'success')
            elif action == 'add_challenge_to_path':
                path_id = request.form.get('path_id')
                challenge_id = request.form.get('challenge_id')
                step = request.form.get('step', type=int)
                path = LearningPath.query.get(path_id)
                if path and step is not None:
                    existing = PathChallenge.query.filter_by(path_id=path_id, challenge_id=challenge_id).first()
                    if not existing:
                        path_challenge = PathChallenge(path_id=path_id, challenge_id=challenge_id, step=step)
                        db.session.add(path_challenge)
                        db.session.commit()
                        flash('Desafio adicionado à trilha com sucesso!', 'success')
                    else:
                        flash('Este desafio já faz parte desta trilha.', 'warning')
                else:
                    flash('Falha ao adicionar desafio. Trilha ou passo inválido.', 'error')
            elif action == 'import_path':
                file = request.files.get('path_file')
                if file and file.filename.endswith('.json'):
                    try:
                        data = json.load(file)
                        new_path = LearningPath(
                            name=data['name'],
                            description=data.get('description'),
                            reward_points=data.get('reward_points', 100),
                            is_active=data.get('is_active', True)
                        )
                        db.session.add(new_path)
                        db.session.flush()
                        for challenge_data in data.get('challenges', []):
                            challenge = Challenge.query.filter_by(title=challenge_data['title']).first()
                            if challenge:
                                path_challenge = PathChallenge(
                                    path_id=new_path.id,
                                    challenge_id=challenge.id,
                                    step=challenge_data['step']
                                )
                                db.session.add(path_challenge)
                            else:
                                flash(f"Aviso: Desafio '{challenge_data['title']}' não encontrado e foi ignorado.", 'warning')
                        db.session.commit()
                        flash('Trilha de aprendizagem importada com sucesso!', 'success')
                    except Exception as e:
                        db.session.rollback()
                        flash(f'Erro ao importar a trilha: {str(e)}', 'error')
                else:
                    flash('Por favor, envie um arquivo JSON válido.', 'error')
            return redirect(url_for('admin_paths'))
        all_paths = LearningPath.query.all()
        all_challenges = Challenge.query.all()
        return render_template('admin/admin_paths.html', paths=all_paths, challenges=all_challenges, form=form)

    @app.route('/path/<int:path_id>')
    @login_required
    def view_path(path_id):
        path = LearningPath.query.get_or_404(path_id)
        if not path.is_active and not current_user.is_admin:
            flash('Esta trilha de aprendizagem não está ativa no momento.', 'warning')
            return redirect(url_for('list_paths'))
        
        user_completed_challenges = {uc.challenge_id for uc in current_user.completed_challenges}
        
        return render_template('learning_paths/view_path.html', path=path, user_completed_challenges=user_completed_challenges)

    @app.route('/admin/paths/edit/<int:path_id>', methods=['GET', 'POST'])
    @login_required
    def admin_edit_path(path_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        path_to_edit = LearningPath.query.get_or_404(path_id)
        if request.method == 'POST':
            path_to_edit.name = request.form.get('name')
            path_to_edit.description = request.form.get('description')
            path_to_edit.reward_points = request.form.get('reward_points', type=int)
            path_to_edit.is_active = request.form.get('is_active') == 'on'
            db.session.commit()
            flash('Trilha de aprendizagem atualizada com sucesso!', 'success')
            return redirect(url_for('admin_paths'))
        return render_template('admin/admin_edit_path.html', path=path_to_edit)

    @app.route('/admin/paths/delete/<int:path_id>', methods=['POST'])
    @login_required
    def admin_delete_path(path_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        path_to_delete = LearningPath.query.get_or_404(path_id)
        db.session.delete(path_to_delete)
        db.session.commit()
        flash('Trilha de aprendizagem excluída com sucesso!', 'success')
        return redirect(url_for('admin_paths'))

    @app.route('/admin/remove_challenge_from_path/<int:path_id>/<int:challenge_id>', methods=['POST'])
    @login_required
    def admin_remove_challenge_from_path(path_id, challenge_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_paths'))
        path_challenge = PathChallenge.query.filter_by(path_id=path_id, challenge_id=challenge_id).first_or_404()
        db.session.delete(path_challenge)
        db.session.commit()
        flash('Desafio removido da trilha com sucesso!', 'success')
        return redirect(url_for('admin_paths'))

    @app.route('/paths')
    @login_required
    def list_paths():
        all_paths = LearningPath.query.filter_by(is_active=True).all()
        completed_challenges_ids = {uc.challenge_id for uc in current_user.completed_challenges}
        completed_paths_ids = {up.path_id for up in UserPathProgress.query.filter_by(user_id=current_user.id).all()}
        paths_with_progress = []
        for path in all_paths:
            total_steps = len(path.challenges)
            completed_steps = 0
            for pc in path.challenges:
                if pc.challenge_id in completed_challenges_ids:
                    completed_steps += 1
            progress_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
            paths_with_progress.append({
                'path': path,
                'progress': progress_percentage,
                'is_completed': path.id in completed_paths_ids
            })
        return render_template('learning_paths/paths.html', paths_data=paths_with_progress)

    @app.route('/admin/achievements', methods=['GET', 'POST'])
    @login_required
    def admin_achievements():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Erro de validação CSRF.', 'error')
                return redirect(url_for('admin_achievements'))
            action = request.form.get('action')
            if action == 'create_achievement':
                name = request.form['name']
                description = request.form['description']
                trigger_type = request.form['trigger_type']
                trigger_value = request.form['trigger_value']
                icon_file = request.files.get('icon_image')
                icon_url = None
                if icon_file:
                    upload_result = cloudinary.uploader.upload(icon_file)
                    icon_url = upload_result['secure_url']
                achievement = Achievement(
                    name=name,
                    description=description,
                    trigger_type=trigger_type,
                    trigger_value=trigger_value,
                    icon=icon_url
                )
                db.session.add(achievement)
                db.session.commit()
                flash('Conquista criada com sucesso!', 'success')
            elif action == 'import_achievements':
                file = request.files['achievement_file']
                if file and file.filename.endswith('.json'):
                    try:
                        data = json.load(file)
                        for ach_data in data:
                            achievement = Achievement(
                                name=ach_data['name'],
                                description=ach_data.get('description'),
                                trigger_type=ach_data['trigger_type'],
                                trigger_value=ach_data['trigger_value'],
                                icon=ach_data.get('icon')
                            )
                            db.session.add(achievement)
                        db.session.commit()
                        flash('Conquistas importadas com sucesso!', 'success')
                    except Exception as e:
                        flash(f'Erro ao importar conquistas: {str(e)}', 'error')
                else:
                    flash('Por favor, envie um arquivo JSON válido.', 'error')
            return redirect(url_for('admin_achievements'))
        achievements = Achievement.query.all()
        return render_template('admin/admin_achievements.html', achievements=achievements, form=form)

    @app.route('/admin/daily_challenges')
    @login_required
    def admin_daily_challenges():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        history = DailyChallenge.query.order_by(DailyChallenge.day.desc()).all()
        return render_template('admin/admin_daily_challenges.html', history=history)

    @app.route('/admin/edit_achievement/<int:achievement_id>', methods=['POST'])
    @login_required
    def admin_edit_achievement(achievement_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_achievements'))
        achievement = Achievement.query.get_or_404(achievement_id)
        achievement.name = request.form['name']
        achievement.description = request.form['description']
        achievement.trigger_type = request.form['trigger_type']
        achievement.trigger_value = request.form['trigger_value']
        db.session.commit()
        flash('Conquista atualizada com sucesso!', 'success')
        return redirect(url_for('admin_achievements'))

    @app.route('/admin/delete_achievement/<int:achievement_id>', methods=['POST'])
    @login_required
    def admin_delete_achievement(achievement_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_achievements'))
        achievement = Achievement.query.get_or_404(achievement_id)
        db.session.delete(achievement)
        db.session.commit()
        flash('Conquista excluída com sucesso!', 'success')
        return redirect(url_for('admin_achievements'))

    @app.route('/admin/bossfights', methods=['GET', 'POST'])
    @login_required
    def admin_boss_fights():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Erro de validação CSRF.', 'error')
                return redirect(url_for('admin_boss_fights'))
            action = request.form.get('action')
            if action == 'create_boss':
                name = request.form['name']
                description = request.form['description']
                reward_points = request.form['reward_points']
                boss_image = request.files.get('boss_image')
                image_url = None
                if boss_image:
                    upload_result = cloudinary.uploader.upload(boss_image)
                    image_url = upload_result['secure_url']
                boss = BossFight(
                    name=name,
                    description=description,
                    reward_points=reward_points,
                    image_url=image_url
                )
                db.session.add(boss)
                db.session.commit()
                flash('Boss Fight criado com sucesso!', 'success')
            elif action == 'create_stage':
                boss_id = request.form['boss_id']
                name = request.form['name']
                order = request.form['order']
                stage = BossFightStage(boss_id=boss_id, name=name, order=order)
                db.session.add(stage)
                db.session.commit()
                flash('Etapa adicionada com sucesso!', 'success')
            elif action == 'create_step':
                stage_id = request.form['stage_id']
                description = request.form['description']
                expected_answer = request.form['expected_answer']
                step = BossFightStep(
                    stage_id=stage_id,
                    description=description,
                    expected_answer=expected_answer
                )
                db.session.add(step)
                db.session.commit()
                flash('Tarefa adicionada com sucesso!', 'success')
            elif action == 'import_boss':
                file = request.files.get('boss_file')
                if file and file.filename.endswith('.json'):
                    try:
                        data = json.load(file)
                        new_boss = BossFight(
                            name=data['name'],
                            description=data.get('description'),
                            reward_points=data.get('reward_points', 500),
                            is_active=data.get('is_active', False),
                            image_url=data.get('image_url')
                        )
                        db.session.add(new_boss)
                        db.session.flush()
                        for stage_data in data.get('stages', []):
                            new_stage = BossFightStage(
                                boss_fight_id=new_boss.id,
                                name=stage_data['name'],
                                order=stage_data['order']
                            )
                            db.session.add(new_stage)
                            db.session.flush()
                            for step_data in stage_data.get('steps', []):
                                new_step = BossFightStep(
                                    stage_id=new_stage.id,
                                    description=step_data['description'],
                                    expected_answer=step_data['expected_answer']
                                )
                                db.session.add(new_step)
                        db.session.commit()
                        flash('Boss Fight importado com sucesso!', 'success')
                    except Exception as e:
                        db.session.rollback()
                        flash(f'Erro ao importar Boss Fight: {str(e)}', 'error')
                else:
                    flash('Por favor, envie um arquivo JSON válido.', 'error')
            return redirect(url_for('admin_boss_fights'))
        boss_fights = BossFight.query.all()
        return render_template('admin/admin_boss_fights.html', boss_fights=boss_fights, form=form)

    @app.route('/admin/edit_boss_fight/<int:boss_id>', methods=['POST'])
    @login_required
    def admin_edit_boss_fight(boss_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_boss_fights'))
        boss = BossFight.query.get_or_404(boss_id)
        boss.name = request.form['name']
        boss.description = request.form['description']
        boss.reward_points = request.form['reward_points']
        boss.is_active = 'is_active' in request.form
        db.session.commit()
        flash('Boss Fight atualizado com sucesso!', 'success')
        return redirect(url_for('admin_boss_fights'))

    @app.route('/admin/delete_boss_fight/<int:boss_id>', methods=['POST'])
    @login_required
    def admin_delete_boss_fight(boss_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_boss_fights'))
        boss = BossFight.query.get_or_404(boss_id)
        db.session.delete(boss)
        db.session.commit()
        flash('Boss Fight excluído com sucesso!', 'success')
        return redirect(url_for('admin_boss_fights'))

    @app.route('/admin/delete_boss_stage/<int:stage_id>', methods=['POST'])
    @login_required
    def admin_delete_boss_stage(stage_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_boss_fights'))
        stage = BossFightStage.query.get_or_404(stage_id)
        db.session.delete(stage)
        db.session.commit()
        flash('Etapa excluída com sucesso!', 'success')
        return redirect(url_for('admin_boss_fights'))

    @app.route('/admin/delete_boss_step/<int:step_id>', methods=['POST'])
    @login_required
    def admin_delete_boss_step(step_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_boss_fights'))
        step = BossFightStep.query.get_or_404(step_id)
        db.session.delete(step)
        db.session.commit()
        flash('Tarefa excluída com sucesso!', 'success')
        return redirect(url_for('admin_boss_fights'))

    @app.route('/bossfights')
    @login_required
    def list_boss_fights():
        if not current_user.team:
            flash('Você precisa estar em uma equipe para participar de Boss Fights!', 'warning')
            return redirect(url_for('teams_list'))
        all_bosses = BossFight.query.filter_by(is_active=True).all()
        return render_template('boss_fights/boss_fights_list_user.html', bosses=all_bosses)

    @app.route('/bossfight/<int:boss_id>')
    @login_required
    def view_boss_fight(boss_id):
        if not current_user.team:
            flash('Você precisa estar em uma equipe para acessar Boss Fights.', 'warning')
            return redirect(url_for('list_boss_fights'))
        boss = BossFight.query.get_or_404(boss_id)
        team_progress = TeamBossProgress.query.filter_by(team_id=current_user.team_id).all()
        completed_step_ids = {progress.step_id for progress in team_progress}
        return render_template('boss_fights/view_boss_fight.html', boss=boss, completed_step_ids=completed_step_ids, team_progress=team_progress)

    @app.route('/bossfight/submit/<int:step_id>', methods=['POST'])
    @login_required
    def submit_boss_step(step_id):
        if not current_user.team:
            flash('Você precisa estar em uma equipe para acessar Boss Fights.', 'warning')
            return redirect(url_for('list_boss_fights'))
        step = BossFightStep.query.get_or_404(step_id)
        boss = step.stage.boss_fight
        submitted_answer = request.form.get('answer', '').strip()
        if submitted_answer.lower() == step.expected_answer.lower():
            if not TeamBossProgress.query.filter_by(team_id=current_user.team_id, step_id=step_id).first():
                progress = TeamBossProgress(
                    team_id=current_user.team_id,
                    step_id=step_id,
                    completed_by_user_id=current_user.id
                )
                db.session.add(progress)
                db.session.commit()
                flash(f'Parabéns! Você completou a tarefa "{step.description}" para sua equipe!', 'success')
                check_boss_fight_completion(current_user.team_id, boss.id)
            else:
                flash('Esta tarefa já foi completada pela sua equipe.', 'info')
        else:
            flash('Resposta incorreta. Tente novamente!', 'error')
        return redirect(url_for('view_boss_fight', boss_id=boss.id))

    @app.route('/admin/edit_challenge/<int:challenge_id>', methods=['POST'])
    @login_required
    def admin_edit_challenge(challenge_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_challenges'))
        challenge = Challenge.query.get_or_404(challenge_id)
        challenge.title = request.form['title']
        challenge.description = request.form['description']
        challenge.level_required = request.form['level_required']
        challenge.points_reward = request.form['points_reward']
        challenge.challenge_type = request.form['challenge_type']
        challenge.expected_answer = request.form['expected_answer']
        challenge.expected_output = request.form.get('expected_output')
        challenge.hint = request.form.get('hint')
        challenge.hint_cost = request.form.get('hint_cost', 5)
        challenge.is_team_challenge = 'is_team_challenge' in request.form
        db.session.commit()
        flash('Desafio atualizado com sucesso!', 'success')
        return redirect(url_for('admin_challenges'))

    @app.route('/admin/delete_challenge/<int:challenge_id>', methods=['POST'])
    @login_required
    def admin_delete_challenge(challenge_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_challenges'))
        challenge = Challenge.query.get_or_404(challenge_id)
        
        # Remover de trilhas antes de apagar
        PathChallenge.query.filter_by(challenge_id=challenge_id).delete()
        # Remover de desafios diários
        DailyChallenge.query.filter_by(challenge_id=challenge_id).delete()
        # Remover de completados
        UserChallenge.query.filter_by(challenge_id=challenge_id).delete()

        db.session.delete(challenge)
        db.session.commit()
        flash('Desafio excluído com sucesso!', 'success')
        return redirect(url_for('admin_challenges'))

    @app.route('/admin/hunts', methods=['GET', 'POST'])
    @login_required
    def admin_hunts():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Erro de validação CSRF.', 'error')
                return redirect(url_for('admin_hunts'))
            action = request.form.get('action')
            if action == 'create_hunt':
                hunt = ScavengerHunt(
                    name=request.form['name'],
                    description=request.form['description'],
                    reward_points=request.form['reward_points']
                )
                db.session.add(hunt)
                db.session.commit()
                flash('Caça ao Tesouro criada com sucesso!', 'success')
            elif action == 'create_step':
                hunt_id = request.form['hunt_id']
                description = request.form['description']
                location_hint = request.form['location_hint']
                qr_code_data = request.form['qr_code_data']
                step = ScavengerHuntStep(
                    hunt_id=hunt_id,
                    description=description,
                    location_hint=location_hint,
                    qr_code_data=qr_code_data
                )
                db.session.add(step)
                db.session.commit()
                flash('Etapa adicionada com sucesso!', 'success')
            return redirect(url_for('admin_hunts'))
        hunts = ScavengerHunt.query.all()
        return render_template('admin/admin_hunts.html', hunts=hunts, form=form)

    @app.route('/admin/edit_hunt/<int:hunt_id>', methods=['POST'])
    @login_required
    def admin_edit_hunt(hunt_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_hunts'))
        hunt = ScavengerHunt.query.get_or_404(hunt_id)
        hunt.name = request.form['name']
        hunt.description = request.form['description']
        hunt.reward_points = request.form['reward_points']
        hunt.is_active = 'is_active' in request.form
        db.session.commit()
        flash('Caça ao Tesouro atualizada com sucesso!', 'success')
        return redirect(url_for('admin_hunts'))

    @app.route('/admin/delete_hunt/<int:hunt_id>', methods=['POST'])
    @login_required
    def delete_hunt(hunt_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_hunts'))
        hunt = ScavengerHunt.query.get_or_404(hunt_id)
        db.session.delete(hunt)
        db.session.commit()
        flash('Caça ao Tesouro excluída com sucesso!', 'success')
        return redirect(url_for('admin_hunts'))

    @app.route('/admin/delete_hunt_step/<int:step_id>', methods=['POST'])
    @login_required
    def delete_hunt_step(step_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_hunts'))
        step = ScavengerHuntStep.query.get_or_404(step_id)
        db.session.delete(step)
        db.session.commit()
        flash('Etapa excluída com sucesso!', 'success')
        return redirect(url_for('admin_hunts'))

    @app.route('/admin/events', methods=['GET', 'POST'])
    @login_required
    def admin_events():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        form = BaseForm()
        if request.method == 'POST':
            if not form.validate_on_submit():
                flash('Erro de validação CSRF.', 'error')
                return redirect(url_for('admin_events'))
            
            start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
            end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')
            total_hp = int(request.form['total_hp'])

            new_event = GlobalEvent(
                name=request.form['name'],
                description=request.form['description'],
                total_hp=total_hp,
                current_hp=total_hp,
                start_date=start_date,
                end_date=end_date,
                reward_points_on_win=int(request.form['reward_points_on_win']),
                is_active='is_active' in request.form
            )
            db.session.add(new_event)
            db.session.commit()
            flash('Evento Global criado com sucesso!', 'success')
            return redirect(url_for('admin_events'))

        events = GlobalEvent.query.order_by(GlobalEvent.start_date.desc()).all()
        return render_template('admin/admin_events.html', events=events, form=form, now=datetime.utcnow())

    @app.route('/admin/events/edit/<int:event_id>', methods=['GET', 'POST'])
    @login_required
    def admin_edit_event(event_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        
        event = GlobalEvent.query.get_or_404(event_id)
        form = BaseForm()
        
        if request.method == 'POST':
            if not form.validate_on_submit():
                return redirect(url_for('admin_edit_event', event_id=event.id))
                
            event.name = request.form['name']
            event.description = request.form['description']
            event.total_hp = int(request.form['total_hp'])
            event.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
            event.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')
            event.reward_points_on_win = int(request.form['reward_points_on_win'])
            event.is_active = 'is_active' in request.form
            
            db.session.commit()
            flash('Evento Global atualizado com sucesso!', 'success')
            return redirect(url_for('admin_events'))

        return render_template('admin/admin_edit_event.html', event=event, form=form)

    @app.route('/admin/events/delete/<int:event_id>', methods=['POST'])
    @login_required
    def admin_delete_event(event_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))

        form = BaseForm()
        if not form.validate_on_submit():
            return redirect(url_for('admin_events'))

        event = GlobalEvent.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        flash('Evento Global apagado com sucesso.', 'success')
        return redirect(url_for('admin_events'))

    @app.route('/teams/challenge/<int:team_id>', methods=['POST'])
    @login_required
    def challenge_team(team_id):
        challenger_team = current_user.team
        challenged_team = Team.query.get_or_404(team_id)
        form = BaseForm()

        if not form.validate_on_submit():
            flash('Erro de validação.', 'error')
            return redirect(url_for('teams_list'))

        if not challenger_team:
            flash('Você precisa de estar numa equipa para desafiar outras.', 'error')
            return redirect(url_for('teams_list'))
        if challenger_team.owner_id != current_user.id:
            flash('Apenas o líder da equipa pode iniciar batalhas.', 'error')
            return redirect(url_for('teams_list'))
        if challenger_team.id == challenged_team.id:
            flash('Você não pode desafiar a sua própria equipa.', 'error')
            return redirect(url_for('teams_list'))

        existing_battle = TeamBattle.query.filter(
            ((TeamBattle.challenging_team_id == challenger_team.id) & (TeamBattle.challenged_team_id == challenged_team.id) |
            (TeamBattle.challenging_team_id == challenged_team.id) & (TeamBattle.challenged_team_id == challenged_team.id)) &
            (TeamBattle.status == 'active')
        ).first()

        if existing_battle:
            flash('Já existe uma batalha ativa entre estas duas equipas.', 'warning')
            return redirect(url_for('teams_list'))

        num_challenges = 5
        available_challenges = Challenge.query.filter_by(is_team_challenge=False).all()
        if len(available_challenges) < num_challenges:
            flash('Não há desafios suficientes na plataforma para iniciar uma batalha.', 'error')
            return redirect(url_for('teams_list'))
        
        selected_challenges = random.sample(available_challenges, num_challenges)
        
        end_time = datetime.utcnow() + timedelta(days=2)
        new_battle = TeamBattle(
            challenging_team_id=challenger_team.id,
            challenged_team_id=challenged_team.id,
            end_time=end_time,
            status='active'
        )
        db.session.add(new_battle)
        db.session.flush()

        for challenge in selected_challenges:
            battle_challenge = TeamBattleChallenge(battle_id=new_battle.id, challenge_id=challenge.id)
            db.session.add(battle_challenge)
        
        db.session.commit()

        flash(f'Desafio enviado para a equipa "{challenged_team.name}"! A batalha termina em 48 horas.', 'success')
        return redirect(url_for('view_battle', battle_id=new_battle.id))

    @app.route('/admin/battles')
    @login_required
    def admin_battles():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        
        battles = TeamBattle.query.order_by(TeamBattle.start_time.desc()).all()
        return render_template('admin/admin_battles.html', battles=battles, form=BaseForm())

    @app.route('/admin/battles/delete/<int:battle_id>', methods=['POST'])
    @login_required
    def admin_delete_battle(battle_id):
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('admin_battles'))
        
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_battles'))

        battle = TeamBattle.query.get_or_404(battle_id)
        TeamBattleChallenge.query.filter_by(battle_id=battle.id).delete()
        db.session.delete(battle)
        db.session.commit()
        flash(f'A batalha entre "{battle.challenging_team.name}" e "{battle.challenged_team.name}" foi apagada.', 'success')
        return redirect(url_for('admin_battles'))

    @app.route('/battle/<int:battle_id>')
    @login_required
    def view_battle(battle_id):
        battle = TeamBattle.query.get_or_404(battle_id)
        if current_user.team_id not in [battle.challenging_team_id, battle.challenged_team_id]:
            flash('A sua equipa não faz parte desta batalha.', 'error')
            return redirect(url_for('teams_list'))
        
        return render_template('events/view_battle.html', battle=battle)

    @app.route('/admin/battles/finalize', methods=['POST'])
    @login_required
    def trigger_finalize_battles():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))
        
        form = BaseForm()
        if not form.validate_on_submit():
            flash('Erro de validação CSRF.', 'error')
            return redirect(url_for('admin_battles'))
        
        count = finalize_ended_battles()
        if count > 0:
            flash(f'{count} batalha(s) foram finalizadas e as recompensas distribuídas.', 'success')
        else:
            flash('Nenhuma batalha ativa precisava de ser finalizada.', 'info')
            
        return redirect(url_for('admin_battles'))

    @app.route('/admin/import', methods=['GET', 'POST'])
    @login_required
    def admin_import_content():
        if not current_user.is_admin:
            flash('Acesso negado.', 'error')
            return redirect(url_for('user.index'))

        form = BaseForm()
        if form.validate_on_submit():
            file = request.files.get('content_file')
            if not file or not file.filename.endswith('.json'):
                flash('Por favor, envie um ficheiro JSON válido.', 'error')
                return redirect(url_for('admin_import_content'))
            
            try:
                content = json.load(file.stream)
                counts = {'faqs': 0, 'desafios': 0, 'trilhas': 0, 'boss_fights': 0, 'caca_tesouros': 0, 'eventos_globais': 0}

                if 'import_faqs' in request.form and 'faqs' in content:
                    existing_questions = {f.question for f in FAQ.query.all()}
                    for faq_data in content['faqs']:
                        if faq_data['question'] not in existing_questions:
                            category = Category.query.filter_by(name=faq_data['category']).first()
                            if not category:
                                category = Category(name=faq_data['category'])
                                db.session.add(category)
                                db.session.flush()
                            
                            new_faq = FAQ(category_id=category.id, **{k: v for k, v in faq_data.items() if k != 'category'})
                            db.session.add(new_faq)
                            counts['faqs'] += 1

                if 'import_desafios' in request.form and 'desafios' in content:
                    existing_titles = {c.title for c in Challenge.query.all()}
                    for challenge_data in content['desafios']:
                        if challenge_data['title'] not in existing_titles:
                            new_challenge = Challenge(**challenge_data)
                            db.session.add(new_challenge)
                            counts['desafios'] += 1

                if 'import_trilhas' in request.form and 'trilhas' in content:
                    existing_names = {p.name for p in LearningPath.query.all()}
                    for path_data in content['trilhas']:
                        if path_data['name'] not in existing_names:
                            challenges_in_path_data = path_data.pop('challenges', [])
                            new_path = LearningPath(**path_data)
                            db.session.add(new_path)
                            db.session.flush()
                            for c_data in challenges_in_path_data:
                                challenge = Challenge.query.filter_by(title=c_data['title']).first()
                                if challenge:
                                    pc = PathChallenge(path_id=new_path.id, challenge_id=challenge.id, step=c_data['step'])
                                    db.session.add(pc)
                            counts['trilhas'] += 1

                if 'import_boss_fights' in request.form and 'boss_fights' in content:
                    existing_names = {b.name for b in BossFight.query.all()}
                    for boss_data in content['boss_fights']:
                        if boss_data['name'] not in existing_names:
                            stages_data = boss_data.pop('stages', [])
                            new_boss = BossFight(**boss_data)
                            db.session.add(new_boss)
                            db.session.flush()
                            for s_data in stages_data:
                                steps_data = s_data.pop('steps', [])
                                new_stage = BossFightStage(boss_fight_id=new_boss.id, **s_data)
                                db.session.add(new_stage)
                                db.session.flush()
                                for step_data in steps_data:
                                    new_step = BossFightStep(stage_id=new_stage.id, **step_data)
                                    db.session.add(new_step)
                            counts['boss_fights'] += 1

                if 'import_caca_tesouros' in request.form and 'caca_tesouros' in content:
                    existing_names = {h.name for h in ScavengerHunt.query.all()}
                    for hunt_data in content['caca_tesouros']:
                        if hunt_data['name'] not in existing_names:
                            steps_data = hunt_data.pop('steps', [])
                            new_hunt = ScavengerHunt(**hunt_data)
                            db.session.add(new_hunt)
                            db.session.flush()
                            for step_data in steps_data:
                                new_step = ScavengerHuntStep(hunt_id=new_hunt.id, **step_data)
                                db.session.add(new_step)
                            counts['caca_tesouros'] += 1
                
                if 'import_eventos_globais' in request.form and 'eventos_globais' in content:
                    existing_names = {e.name for e in GlobalEvent.query.all()}
                    for event_data in content['eventos_globais']:
                        if event_data['name'] not in existing_names:
                            event_data['start_date'] = datetime.fromisoformat(event_data['start_date'])
                            event_data['end_date'] = datetime.fromisoformat(event_data['end_date'])
                            event_data['current_hp'] = event_data['total_hp']
                            
                            new_event = GlobalEvent(**event_data)
                            db.session.add(new_event)
                            counts['eventos_globais'] += 1

                db.session.commit()
                flash(f"Importação concluída! Adicionados: {counts['faqs']} FAQs, {counts['desafios']} Desafios, "
                    f"{counts['trilhas']} Trilhas, {counts['boss_fights']} Boss Fights, "
                    f"{counts['caca_tesouros']} Caças ao Tesouro, {counts['eventos_globais']} Eventos Globais.", 'success')

            except Exception as e:
                db.session.rollback()
                flash(f'Ocorreu um erro durante a importação: {e}', 'error')
            
            return redirect(url_for('admin_import_content'))
        
        return render_template('admin/admin_import.html', form=form)

    return app
