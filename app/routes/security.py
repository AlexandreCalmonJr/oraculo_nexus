"""
Rotas para Dashboard de Segurança
Monitoramento de atividades suspeitas e análise de riscos
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.services.security_monitor import security_monitor
from app.models import User

security_bp = Blueprint('security', __name__, url_prefix='/admin/security')


@security_bp.route('/')
@login_required
def security_dashboard():
    """Página do dashboard de segurança"""
    if not current_user.is_admin:
        return redirect(url_for('user.index'))
    
    # Buscar todos os admins para análise
    admins = User.query.filter_by(is_admin=True).all()
    
    return render_template('admin/admin_security.html', admins=admins)


@security_bp.route('/api/stats')
@login_required
def api_security_stats():
    """API: Estatísticas de segurança"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    days = int(request.args.get('days', 30))
    stats = security_monitor.get_security_stats(days=days)
    
    return jsonify({'success': True, 'stats': stats})


@security_bp.route('/api/check/<int:admin_id>')
@login_required
def api_check_admin(admin_id):
    """API: Verificar atividade suspeita de um admin"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    alert = security_monitor.check_suspicious_activity(admin_id)
    
    return jsonify({'success': True, 'alert': alert})


@security_bp.route('/api/risk-score/<int:admin_id>')
@login_required
def api_risk_score(admin_id):
    """API: Score de risco de um admin"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    days = int(request.args.get('days', 30))
    risk = security_monitor.get_admin_risk_score(admin_id, days=days)
    
    return jsonify({'success': True, 'risk': risk})


@security_bp.route('/api/all-risks')
@login_required
def api_all_risks():
    """API: Score de risco de todos os admins"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    days = int(request.args.get('days', 30))
    admins = User.query.filter_by(is_admin=True).all()
    
    risks = []
    for admin in admins:
        risk = security_monitor.get_admin_risk_score(admin.id, days=days)
        risk['admin_name'] = admin.name
        risks.append(risk)
    
    # Ordenar por score (maior primeiro)
    risks.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify({'success': True, 'risks': risks})
