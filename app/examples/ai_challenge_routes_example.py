"""
Exemplo de integração do AIChallengeService nas rotas
"""
from flask import request, jsonify, flash, redirect, url_for
from app.services.ai_challenge_service import ai_challenge_service
from app.models.challenges import Challenge, UserChallenge
from app.extensions import db
from flask_login import current_user, login_required


# ===== EXEMPLO 1: Validar Resposta de Desafio =====
@app.route('/challenge/<int:challenge_id>/submit', methods=['POST'])
@login_required
def submit_challenge(challenge_id):
    """Submete resposta para um desafio com validação IA"""
    challenge = Challenge.query.get_or_404(challenge_id)
    user_answer = request.form.get('answer', '').strip()
    
    if not user_answer:
        flash('Por favor, forneça uma resposta.', 'error')
        return redirect(url_for('challenge_detail', challenge_id=challenge_id))
    
    # VALIDAÇÃO COM IA
    validation = ai_challenge_service.validate_answer(
        challenge=challenge,
        user_answer=user_answer,
        use_ai=True  # Usar validação semântica
    )
    
    is_correct = validation['is_correct']
    confidence = validation['confidence']
    
    # FEEDBACK PERSONALIZADO COM IA
    feedback = ai_challenge_service.generate_feedback(
        challenge=challenge,
        user_answer=user_answer,
        is_correct=is_correct
    )
    
    if is_correct and confidence > 0.7:  # Threshold de confiança
        # Marcar como completado
        user_challenge = UserChallenge(
            user_id=current_user.id,
            challenge_id=challenge.id
        )
        db.session.add(user_challenge)
        
        # Adicionar pontos
        current_user.points += challenge.points_reward
        db.session.commit()
        
        flash(f'✅ {feedback}', 'success')
        flash(f'Você ganhou {challenge.points_reward} pontos!', 'success')
    else:
        flash(f'❌ {feedback}', 'error')
        if confidence < 0.5:
            flash(f'💡 Confiança baixa ({confidence:.0%}). Revise sua resposta.', 'warning')
    
    return redirect(url_for('challenge_detail', challenge_id=challenge_id))


# ===== EXEMPLO 2: Solicitar Dica =====
@app.route('/challenge/<int:challenge_id>/hint', methods=['POST'])
@login_required
def get_challenge_hint(challenge_id):
    """Obtém dica contextual para o desafio"""
    challenge = Challenge.query.get_or_404(challenge_id)
    
    # Contar tentativas do usuário
    attempts = UserChallenge.query.filter_by(
        user_id=current_user.id,
        challenge_id=challenge.id
    ).count()
    
    # Verificar se usuário tem pontos suficientes
    if current_user.points < challenge.hint_cost:
        return jsonify({
            'error': 'Pontos insuficientes para dica'
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
        'hint': hint,
        'cost': challenge.hint_cost,
        'remaining_points': current_user.points
    })


# ===== EXEMPLO 3: Admin - Gerar Desafio com IA =====
@app.route('/admin/challenge/generate', methods=['POST'])
@login_required
def admin_generate_challenge():
    """Gera um novo desafio usando IA"""
    if not current_user.is_admin:
        flash('Acesso negado.', 'error')
        return redirect(url_for('user.index'))
    
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
        flash('Erro ao gerar desafio com IA.', 'error')
        return redirect(url_for('admin_challenges'))
    
    # Criar desafio no banco
    new_challenge = Challenge(
        title=challenge_data['title'],
        description=challenge_data['description'],
        expected_answer=challenge_data['expected_answer'],
        hint=challenge_data['hint'],
        points_reward=challenge_data['points_reward'],
        level_required=challenge_data['level_required'],
        challenge_type=challenge_data['challenge_type']
    )
    
    db.session.add(new_challenge)
    db.session.commit()
    
    flash(f'✨ Desafio "{new_challenge.title}" gerado com IA!', 'success')
    return redirect(url_for('admin_edit_challenge', challenge_id=new_challenge.id))


# ===== EXEMPLO 4: API para Frontend =====
@app.route('/api/challenge/<int:challenge_id>/validate', methods=['POST'])
@login_required
def api_validate_challenge(challenge_id):
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
