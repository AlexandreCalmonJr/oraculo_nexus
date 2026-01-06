"""
Rotas para Visualização de Logs Administrativos
Permite visualizar, filtrar e exportar logs de auditoria
"""
from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.services.audit_service import audit_service
from app.models import User
import csv
import io

admin_logs_bp = Blueprint('admin_logs', __name__, url_prefix='/admin/logs')


@admin_logs_bp.route('/')
@login_required
def logs_page():
    """Página de visualização de logs"""
    if not current_user.is_admin:
        return redirect(url_for('user.index'))
    
    # Buscar lista de admins para filtro
    admins = User.query.filter_by(is_admin=True).all()
    
    return render_template('admin/admin_logs.html', admins=admins)


@admin_logs_bp.route('/api/list')
@login_required
def api_list_logs():
    """API: Lista logs com filtros e paginação"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    # Parâmetros de filtro
    filters = {}
    
    admin_id = request.args.get('admin_id')
    if admin_id:
        filters['admin_id'] = int(admin_id)
    
    action = request.args.get('action')
    if action:
        filters['action'] = action
    
    resource_type = request.args.get('resource_type')
    if resource_type:
        filters['resource_type'] = resource_type
    
    date_from = request.args.get('date_from')
    if date_from:
        filters['date_from'] = datetime.fromisoformat(date_from)
    
    date_to = request.args.get('date_to')
    if date_to:
        filters['date_to'] = datetime.fromisoformat(date_to)
    
    # Paginação
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    offset = (page - 1) * per_page
    
    # Buscar logs
    result = audit_service.get_logs(filters=filters, limit=per_page, offset=offset)
    
    return jsonify({
        'success': True,
        'logs': result['logs'],
        'total': result['total'],
        'page': page,
        'per_page': per_page,
        'total_pages': (result['total'] + per_page - 1) // per_page
    })


@admin_logs_bp.route('/api/<int:log_id>')
@login_required
def api_get_log(log_id):
    """API: Detalhes de um log específico"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    from app.models import AdminLog
    log = AdminLog.query.get(log_id)
    
    if not log:
        return jsonify({'success': False, 'error': 'Log não encontrado'}), 404
    
    return jsonify({'success': True, 'log': log.to_dict()})


@admin_logs_bp.route('/api/stats')
@login_required
def api_stats():
    """API: Estatísticas de auditoria"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    days = int(request.args.get('days', 30))
    stats = audit_service.get_stats(days=days)
    
    return jsonify({'success': True, 'stats': stats})


@admin_logs_bp.route('/api/export')
@login_required
def api_export():
    """API: Exportar logs em CSV"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    # Aplicar mesmos filtros da listagem
    filters = {}
    admin_id = request.args.get('admin_id')
    if admin_id:
        filters['admin_id'] = int(admin_id)
    
    action = request.args.get('action')
    if action:
        filters['action'] = action
    
    resource_type = request.args.get('resource_type')
    if resource_type:
        filters['resource_type'] = resource_type
    
    # Buscar todos os logs (sem paginação)
    result = audit_service.get_logs(filters=filters, limit=10000, offset=0)
    
    # Criar CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow(['ID', 'Data/Hora', 'Admin', 'Ação', 'Recurso', 'ID Recurso', 'Descrição', 'IP'])
    
    # Dados
    for log in result['logs']:
        writer.writerow([
            log['id'],
            log['created_at'],
            log['admin_name'],
            log['action'],
            log['resource_type'],
            log['resource_id'] or '',
            log['description'],
            log['ip_address'] or ''
        ])
    
    # Preparar resposta
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'admin_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )
