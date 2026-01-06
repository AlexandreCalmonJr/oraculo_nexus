"""
Rotas de Gerenciamento de Notificações
Permite aos usuários visualizar e gerenciar suas notificações
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.services.notification_service import notification_service
from app.forms import BaseForm

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@notifications_bp.route('/')
@login_required
def notifications_page():
    """Página de gerenciamento de notificações"""
    return render_template('user/notifications.html')


@notifications_bp.route('/api/list')
@login_required
def api_list_notifications():
    """API: Lista notificações do usuário com paginação e filtros"""
    filter_type = request.args.get('filter', 'all')  # all, unread, read
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    offset = (page - 1) * per_page
    
    result = notification_service.get_user_notifications(
        current_user.id,
        filter_type=filter_type,
        limit=per_page,
        offset=offset
    )
    
    return jsonify({
        'success': True,
        'notifications': result['notifications'],
        'total': result['total'],
        'unread_count': result['unread_count'],
        'page': page,
        'per_page': per_page,
        'total_pages': (result['total'] + per_page - 1) // per_page
    })


@notifications_bp.route('/api/<int:notification_id>/read', methods=['POST'])
@login_required
def api_mark_as_read(notification_id):
    """API: Marca notificação como lida"""
    form = BaseForm()
    if not form.validate_on_submit():
        return jsonify({'success': False, 'error': 'Erro de validação CSRF'}), 400
    
    success = notification_service.mark_as_read(notification_id, current_user.id)
    
    if success:
        unread_count = notification_service.get_unread_count(current_user.id)
        return jsonify({'success': True, 'unread_count': unread_count})
    else:
        return jsonify({'success': False, 'error': 'Notificação não encontrada'}), 404


@notifications_bp.route('/api/<int:notification_id>/unread', methods=['POST'])
@login_required
def api_mark_as_unread(notification_id):
    """API: Marca notificação como não lida"""
    form = BaseForm()
    if not form.validate_on_submit():
        return jsonify({'success': False, 'error': 'Erro de validação CSRF'}), 400
    
    success = notification_service.mark_as_unread(notification_id, current_user.id)
    
    if success:
        unread_count = notification_service.get_unread_count(current_user.id)
        return jsonify({'success': True, 'unread_count': unread_count})
    else:
        return jsonify({'success': False, 'error': 'Notificação não encontrada'}), 404


@notifications_bp.route('/api/<int:notification_id>', methods=['DELETE'])
@login_required
def api_delete_notification(notification_id):
    """API: Deleta uma notificação"""
    form = BaseForm()
    if not form.validate_on_submit():
        return jsonify({'success': False, 'error': 'Erro de validação CSRF'}), 400
    
    success = notification_service.delete_notification(notification_id, current_user.id)
    
    if success:
        unread_count = notification_service.get_unread_count(current_user.id)
        return jsonify({'success': True, 'unread_count': unread_count})
    else:
        return jsonify({'success': False, 'error': 'Notificação não encontrada'}), 404


@notifications_bp.route('/api/mark-all-read', methods=['POST'])
@login_required
def api_mark_all_read():
    """API: Marca todas as notificações como lidas"""
    form = BaseForm()
    if not form.validate_on_submit():
        return jsonify({'success': False, 'error': 'Erro de validação CSRF'}), 400
    
    notification_service.mark_all_as_read(current_user.id)
    
    return jsonify({'success': True, 'unread_count': 0})


@notifications_bp.route('/api/clear-read', methods=['POST'])
@login_required
def api_clear_read():
    """API: Remove todas as notificações lidas"""
    form = BaseForm()
    if not form.validate_on_submit():
        return jsonify({'success': False, 'error': 'Erro de validação CSRF'}), 400
    
    notification_service.clear_read_notifications(current_user.id)
    unread_count = notification_service.get_unread_count(current_user.id)
    
    return jsonify({'success': True, 'unread_count': unread_count})


@notifications_bp.route('/api/unread-count')
@login_required
def api_unread_count():
    """API: Obtém contagem de notificações não lidas"""
    unread_count = notification_service.get_unread_count(current_user.id)
    return jsonify({'success': True, 'unread_count': unread_count})


# ===== ROTAS ADMIN =====

@notifications_bp.route('/admin')
@login_required
def admin_notifications():
    """Página admin de gerenciamento de notificações"""
    if not current_user.is_admin:
        flash('Acesso negado.', 'error')
        return redirect(url_for('user.index'))
    
    form = BaseForm()
    return render_template('admin/admin_notifications.html', form=form)


@notifications_bp.route('/admin/api/broadcast', methods=['POST'])
@login_required
def admin_broadcast_notification():
    """API Admin: Envia notificação broadcast para todos os usuários"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
        
        message = data.get('message', '').strip()
        event_type = data.get('type', 'info')
        category = data.get('category', 'system')
        
        if not message:
            return jsonify({'success': False, 'error': 'Mensagem é obrigatória'}), 400
        
        # Verificar se notification_service está disponível
        if not notification_service:
            return jsonify({'success': False, 'error': 'Serviço de notificações não disponível'}), 500
        
        # Enviar notificação broadcast
        notification_service.notify_all(
            event_type=event_type,
            message=message,
            category=category,
            save_to_db=False  # Broadcast não salva no DB
        )
        
        # Registrar log de auditoria
        from app.services.audit_service import audit_service
        audit_service.log_broadcast(
            admin_id=current_user.id,
            message=message,
            recipients_count=0  # TODO: contar usuários conectados
        )
        
        return jsonify({'success': True, 'message': 'Notificação enviada com sucesso'})
    
    except Exception as e:
        import traceback
        print(f"Erro ao enviar broadcast: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': f'Erro ao enviar notificação: {str(e)}'}), 500


@notifications_bp.route('/admin/api/stats')
@login_required
def admin_notification_stats():
    """API Admin: Estatísticas de notificações"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    from app.models import Notification, User
    
    total_notifications = Notification.query.count()
    unread_notifications = Notification.query.filter_by(is_read=False).count()
    total_users = User.query.count()
    
    # Notificações por categoria
    from sqlalchemy import func
    category_stats = db.session.query(
        Notification.category,
        func.count(Notification.id).label('count')
    ).group_by(Notification.category).all()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_notifications': total_notifications,
            'unread_notifications': unread_notifications,
            'total_users': total_users,
            'categories': [{'category': cat, 'count': count} for cat, count in category_stats]
        }
    })
