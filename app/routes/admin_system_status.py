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
