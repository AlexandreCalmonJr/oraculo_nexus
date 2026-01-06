"""
API de Estatísticas para Gráficos do Dashboard Admin
Adicione estas rotas ao seu arquivo de rotas admin
"""
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models.user import User
from app.models.challenges import Challenge, UserChallenge
from app.models.gamification import Level
from app.models.learning_paths import LearningPath, UserPathProgress



# Criar blueprint
admin_api_bp = Blueprint('admin_api', __name__, url_prefix='/admin/api')


@admin_api_bp.route('/stats')
@login_required
def get_stats():
    """Retorna estatísticas para os gráficos do dashboard"""
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Período de análise (últimos 30 dias)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # ===== GRÁFICO 1: Usuários Ativos (Linha Temporal) =====
    users_timeline = []
    for i in range(30):
        date = datetime.utcnow() - timedelta(days=29-i)
        count = User.query.filter(
            func.date(User.registered_at) == date.date()
        ).count()
        users_timeline.append({
            'date': date.strftime('%d/%m'),
            'count': count
        })

    
    # ===== GRÁFICO 2: Desafios Completados (Barra por Dia) =====
    challenges_daily = []
    for i in range(7):  # Última semana
        date = datetime.utcnow() - timedelta(days=6-i)
        count = UserChallenge.query.filter(
            func.date(UserChallenge.completed_at) == date.date()
        ).count()
        challenges_daily.append({
            'day': date.strftime('%a'),
            'count': count
        })
    
    # ===== GRÁFICO 3: Distribuição de Níveis (Pizza) =====
    levels_distribution = db.session.query(
        Level.name,
        func.count(User.id).label('count')
    ).join(User, User.level_id == Level.id, isouter=True)\
     .group_by(Level.name)\
     .all()
    
    levels_data = [
        {'level': level, 'count': count}
        for level, count in levels_distribution
    ]
    
    # ===== GRÁFICO 4: Engajamento por Trilha (Barra Horizontal) =====
    paths_engagement = db.session.query(
        LearningPath.name,
        func.count(UserPathProgress.id).label('users')
    ).join(UserPathProgress, UserPathProgress.path_id == LearningPath.id, isouter=True)\
     .group_by(LearningPath.name)\
     .order_by(func.count(UserPathProgress.id).desc())\
     .limit(10)\
     .all()
    
    paths_data = [
        {'path': path, 'users': users}
        for path, users in paths_engagement
    ]
    
    # ===== GRÁFICO 5: Taxa de Conclusão (Área) =====
    completion_rate = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=6-i)
        started = UserPathProgress.query.filter(
            func.date(UserPathProgress.started_at) <= date.date()
        ).count()
        completed = UserPathProgress.query.filter(
            func.date(UserPathProgress.completed_at) <= date.date()
        ).count()
        rate = (completed / started * 100) if started > 0 else 0
        completion_rate.append({
            'day': date.strftime('%a'),
            'rate': round(rate, 1)
        })
    
    # ===== GRÁFICO 6: Atividade por Hora (Heatmap) =====
    hourly_activity = db.session.query(
        func.extract('hour', UserChallenge.completed_at).label('hour'),
        func.count(UserChallenge.id).label('count')
    ).filter(UserChallenge.completed_at >= thirty_days_ago)\
     .group_by('hour')\
     .all()
    
    activity_data = [0] * 24  # 24 horas
    for hour, count in hourly_activity:
        if hour is not None:
            activity_data[int(hour)] = count
    
    # Retornar todos os dados
    return jsonify({
        'users_timeline': users_timeline,
        'challenges_daily': challenges_daily,
        'levels_distribution': levels_data,
        'paths_engagement': paths_data,
        'completion_rate': completion_rate,
        'hourly_activity': activity_data
    })


@admin_api_bp.route('/stats/summary')
@login_required
def get_summary_stats():
    """Retorna estatísticas resumidas para os cards"""
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Estatísticas gerais
    total_users = User.query.count()
    total_challenges = Challenge.query.count()
    total_completed = UserChallenge.query.count()
    
    # Usuários ativos (últimos 7 dias)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_users = User.query.filter(
        User.last_login >= seven_days_ago
    ).count() if hasattr(User, 'last_login') else 0
    
    # Novos usuários (hoje)
    today = datetime.utcnow().date()
    new_users_today = User.query.filter(
        func.date(User.registered_at) == today
    ).count()
    
    # Desafios completados (hoje)
    challenges_today = UserChallenge.query.filter(
        func.date(UserChallenge.completed_at) == today
    ).count()
    
    return jsonify({
        'total_users': total_users,
        'total_challenges': total_challenges,
        'total_completed': total_completed,
        'active_users': active_users,
        'new_users_today': new_users_today,
        'challenges_today': challenges_today
    })
# Adicionar ao final do arquivo admin_api.py

@admin_api_bp.route('/system/status')
@login_required
def system_status():
    '''Retorna status completo do sistema'''
    if not current_user.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    import psutil
    import sys
    
    # STATUS DO BANCO DE DADOS
    db_status = {'online': False, 'response_time': 0}
    try:
        from datetime import datetime
        start = datetime.now()
        db.session.execute(db.text('SELECT 1'))
        db_status['online'] = True
        db_status['response_time'] = (datetime.now() - start).total_seconds() * 1000
    except:
        pass
    
    # STATUS DA IA
    from app.services.ai_service import ai_service
    ai_status = {'online': False, 'api_key_configured': ai_service.client is not None}
    if ai_service.client:
        try:
            start = datetime.now()
            response = ai_service.generate_response('teste', '')
            ai_status['online'] = response is not None
            ai_status['response_time'] = (datetime.now() - start).total_seconds() * 1000
        except:
            pass
    
    # STATUS DO SERVIDOR
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    
    server_status = {
        'cpu_percent': psutil.cpu_percent(interval=0.5),
        'memory_percent': memory.percent,
        'memory_used': f'{memory.used / (1024**3):.2f} GB',
        'memory_total': f'{memory.total / (1024**3):.2f} GB',
        'disk_percent': disk.percent,
        'disk_used': f'{disk.used / (1024**3):.2f} GB',
        'disk_total': f'{disk.total / (1024**3):.2f} GB',
        'uptime': f'{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m',
        'python_version': sys.version.split()[0],
        'flask_env': os.getenv('FLASK_ENV', 'production')
    }
    
    return jsonify({
        'database': db_status,
        'ai': ai_status,
        'server': server_status,
        'timestamp': datetime.now().isoformat()
    })
