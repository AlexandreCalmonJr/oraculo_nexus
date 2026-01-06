"""
Rotas de Desafios com IA Integrada
Adicione estas rotas ao seu arquivo de rotas principal
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models.challenges import Challenge, UserChallenge
from app.services.ai_challenge_service import ai_challenge_service

# Criar blueprint
challenges_bp = Blueprint('challenges', __name__, url_prefix='/challenges')


@challenges_bp.route('/')
@login_required
def list_challenges():
    """Lista todos os desafios disponíveis"""
    all_challenges = Challenge.query.all()
    
    # IDs dos desafios já completados pelo usuário
    completed_ids = {uc.challenge_id for uc in current_user.completed_challenges}
    
    # Separar desafios completados e pendentes
    completed = [c for c in all_challenges if c.id in completed_ids]
    pending = [c for c in all_challenges if c.id not in completed_ids]
    
    return render_template(
        'challenges/list.html',
        pending_challenges=pending,
        completed_challenges=completed
    )


@challenges_bp.route('/<int:challenge_id>')
@login_required
def challenge_detail(challenge_id):
    """Exibe detalhes de um desafio específico"""
    challenge = Challenge.query.get_or_404(challenge_id)
    
    # Verificar se já completou
    is_completed = UserChallenge.query.filter_by(
        user_id=current_user.id,
        challenge_id=challenge.id
    ).first() is not None
    
    # Contar tentativas (para dicas progressivas)
    attempts = session.get(f'challenge_{challenge_id}_attempts', 0)
    
    return render_template(
        'challenges/detail.html',
        challenge=challenge,
        is_completed=is_completed,
        attempts=attempts
    )


@challenges_bp.route('/<int:challenge_id>/submit', methods=['POST'])
@login_required
def submit_challenge(challenge_id):
    """Submete resposta para um desafio com validação IA"""
    challenge = Challenge.query.get_or_404(challenge_id)
    user_answer = request.form.get('answer', '').strip()
    
    if not user_answer:
        flash('❌ Por favor, forneça uma resposta.', 'error')
        return redirect(url_for('challenges.challenge_detail', challenge_id=challenge_id))
    
    # Verificar se já completou
    already_completed = UserChallenge.query.filter_by(
        user_id=current_user.id,
        challenge_id=challenge.id
    ).first()
    
    if already_completed:
        flash('✅ Você já completou este desafio!', 'info')
        return redirect(url_for('challenges.challenge_detail', challenge_id=challenge_id))
    
    # VALIDAÇÃO COM IA
    validation = ai_challenge_service.validate_answer(
        challenge=challenge,
        user_answer=user_answer,
        use_ai=True
    )
    
    is_correct = validation['is_correct']
    confidence = validation['confidence']
    
    # FEEDBACK PERSONALIZADO COM IA
    feedback = ai_challenge_service.generate_feedback(
        challenge=challenge,
        user_answer=user_answer,
        is_correct=is_correct
    )
    
    # Incrementar tentativas
    from flask import session
    attempts_key = f'challenge_{challenge_id}_attempts'
    session[attempts_key] = session.get(attempts_key, 0) + 1
    
    if is_correct and confidence > 0.7:  # Threshold de confiança
        # Marcar como completado
        user_challenge = UserChallenge(
            user_id=current_user.id,
            challenge_id=challenge.id
        )
        db.session.add(user_challenge)
        
        # Adicionar pontos
        current_user.points += challenge.points_reward
        
        # Atualizar nível se necessário
        from app.models.levels import Level
        new_level = Level.query.filter(
            Level.min_points <= current_user.points
        ).order_by(Level.min_points.desc()).first()
        
        if new_level and (not current_user.level or new_level.id != current_user.level_id):
            current_user.level_id = new_level.id
            flash(f'🎉 Parabéns! Você subiu para o nível {new_level.name}!', 'success')
        
        db.session.commit()
        
        # Limpar tentativas
        session.pop(attempts_key, None)
        
        flash(feedback, 'success')
        flash(f'💰 Você ganhou {challenge.points_reward} pontos!', 'success')
        
        return redirect(url_for('challenges.list_challenges'))
    else:
        flash(feedback, 'error')
        if confidence < 0.5:
            flash(f'💡 Confiança: {confidence:.0%}. Revise sua resposta.', 'warning')
        
        return redirect(url_for('challenges.challenge_detail', challenge_id=challenge_id))


@challenges_bp.route('/<int:challenge_id>/hint', methods=['POST'])
@login_required
def get_hint(challenge_id):
    """Obtém dica contextual para o desafio"""
    challenge = Challenge.query.get_or_404(challenge_id)
    
    # Contar tentativas
    from flask import session
    attempts = session.get(f'challenge_{challenge_id}_attempts', 0)
    
    # Verificar se usuário tem pontos suficientes
    if current_user.points < challenge.hint_cost:
        return jsonify({
            'success': False,
            'error': f'Você precisa de {challenge.hint_cost} pontos para obter uma dica.'
        }), 400
    
    # GERAR DICA COM IA
    hint = ai_challenge_service.generate_hint(
        challenge=challenge,
        user_attempts=attempts
    )
    
    # Deduzir pontos
    current_user.points -= challenge.hint_cost
    db.session.commit()
    
    return jsonify({
        'success': True,
        'hint': hint,
        'cost': challenge.hint_cost,
        'remaining_points': current_user.points
    })


@challenges_bp.route('/api/<int:challenge_id>/validate', methods=['POST'])
@login_required
def api_validate(challenge_id):
    """API para validação em tempo real (AJAX)"""
    challenge = Challenge.query.get_or_404(challenge_id)
    data = request.get_json()
    user_answer = data.get('answer', '').strip()
    
    if not user_answer:
        return jsonify({'error': 'Resposta vazia'}), 400
    
    # Validação com IA
    validation = ai_challenge_service.validate_answer(
        challenge=challenge,
        user_answer=user_answer,
        use_ai=True
    )
    
    return jsonify({
        'is_correct': validation['is_correct'],
        'confidence': validation['confidence'],
        'explanation': validation['explanation']
    })


# ===== ROTAS ADMIN =====

@challenges_bp.route('/admin/generate', methods=['GET', 'POST'])
@login_required
def admin_generate():
    """Admin: Gera um novo desafio usando IA"""
    if not current_user.is_admin:
        flash('Acesso negado.', 'error')
        return redirect(url_for('challenges.list_challenges'))
    
    if request.method == 'POST':
        topic = request.form.get('topic', 'Python')
        difficulty = request.form.get('difficulty', 'medium')
        challenge_type = request.form.get('type', 'text')
        
        # GERAR DESAFIO COM IA
        challenge_data = ai_challenge_service.generate_challenge(
            topic=topic,
            difficulty=difficulty,
            challenge_type=challenge_type
        )
        
        if not challenge_data:
            flash('❌ Erro ao gerar desafio com IA.', 'error')
            return redirect(url_for('admin_challenges'))
        
        # Criar desafio no banco
        new_challenge = Challenge(
            title=challenge_data['title'],
            description=challenge_data['description'],
            expected_answer=challenge_data['expected_answer'],
            hint=challenge_data.get('hint'),
            points_reward=challenge_data['points_reward'],
            level_required=challenge_data['level_required'],
            challenge_type=challenge_data['challenge_type']
        )
        
        db.session.add(new_challenge)
        db.session.commit()
        
        flash(f'✨ Desafio "{new_challenge.title}" gerado com IA!', 'success')
        return redirect(url_for('admin_edit_challenge', challenge_id=new_challenge.id))
    
    return render_template('admin/generate_challenge.html')
