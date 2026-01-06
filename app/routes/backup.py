"""
Rotas para Gerenciamento de Backups
Interface admin para criar, restaurar e gerenciar backups
"""
from flask import Blueprint, render_template, request, jsonify, send_file, redirect, url_for
from flask_login import login_required, current_user
from app.services.backup_service import backup_service
from app.services.restore_service import restore_service
from app.services.audit_service import audit_service
import io

backup_bp = Blueprint('backup', __name__, url_prefix='/admin/backup')


@backup_bp.route('/')
@login_required
def backup_page():
    """Página de gerenciamento de backups"""
    if not current_user.is_admin:
        return redirect(url_for('user.index'))
    
    return render_template('admin/admin_backup.html')


@backup_bp.route('/api/list')
@login_required
def api_list_backups():
    """API: Lista todos os backups"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    backups = backup_service.list_backups()
    stats = backup_service.get_backup_stats()
    
    return jsonify({
        'success': True,
        'backups': [b.to_dict() for b in backups],
        'stats': stats
    })


@backup_bp.route('/api/create', methods=['POST'])
@login_required
def api_create_backup():
    """API: Cria um novo backup"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    try:
        data = request.get_json() or {}
        notes = data.get('notes', '')
        
        backup = backup_service.create_backup(
            created_by=current_user.id,
            backup_type='manual',
            notes=notes
        )
        
        # Registrar log de auditoria
        audit_service.log_action(
            admin_id=current_user.id,
            action='CREATE',
            resource_type='Backup',
            resource_id=backup.id,
            description=f'Criou backup manual: {backup.filename}',
            changes={'size_mb': backup.to_dict()['size_mb']}
        )
        
        return jsonify({
            'success': True,
            'message': 'Backup criado com sucesso',
            'backup': backup.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao criar backup: {str(e)}'
        }), 500


@backup_bp.route('/api/validate/<int:backup_id>')
@login_required
def api_validate_backup(backup_id):
    """API: Valida um backup"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    result = backup_service.validate_backup(backup_id)
    
    return jsonify({
        'success': True,
        'validation': result
    })


@backup_bp.route('/api/restore/<int:backup_id>', methods=['POST'])
@login_required
def api_restore_backup(backup_id):
    """API: Restaura um backup"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    try:
        result = restore_service.restore_from_backup(
            backup_id=backup_id,
            created_by=current_user.id
        )
        
        if result['success']:
            # Registrar log de auditoria
            audit_service.log_action(
                admin_id=current_user.id,
                action='UPDATE',
                resource_type='Database',
                resource_id=backup_id,
                description=f'Restaurou banco de dados do backup #{backup_id}',
                changes={
                    'safety_backup_id': result.get('safety_backup_id'),
                    'restored_from': backup_id
                }
            )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao restaurar backup: {str(e)}'
        }), 500


@backup_bp.route('/api/delete/<int:backup_id>', methods=['POST'])
@login_required
def api_delete_backup(backup_id):
    """API: Remove um backup"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    try:
        backup = backup_service.get_backup_info(backup_id)
        if not backup:
            return jsonify({'success': False, 'error': 'Backup não encontrado'}), 404
        
        backup_filename = backup.filename
        
        success = backup_service.delete_backup(backup_id)
        
        if success:
            # Registrar log de auditoria
            audit_service.log_delete(
                admin_id=current_user.id,
                resource_type='Backup',
                resource_id=backup_id,
                resource_name=backup_filename
            )
        
        return jsonify({
            'success': success,
            'message': 'Backup removido com sucesso' if success else 'Erro ao remover backup'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao remover backup: {str(e)}'
        }), 500


@backup_bp.route('/api/download/<int:backup_id>')
@login_required
def api_download_backup(backup_id):
    """API: Download de um backup"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    backup = backup_service.get_backup_info(backup_id)
    if not backup:
        return jsonify({'success': False, 'error': 'Backup não encontrado'}), 404
    
    from pathlib import Path
    backup_path = Path(backup.filepath)
    
    if not backup_path.exists():
        return jsonify({'success': False, 'error': 'Arquivo de backup não encontrado'}), 404
    
    # Registrar log de auditoria
    audit_service.log_action(
        admin_id=current_user.id,
        action='EXPORT',
        resource_type='Backup',
        resource_id=backup_id,
        description=f'Baixou backup: {backup.filename}'
    )
    
    return send_file(
        backup_path,
        as_attachment=True,
        download_name=backup.filename
    )


@backup_bp.route('/api/cleanup', methods=['POST'])
@login_required
def api_cleanup_backups():
    """API: Limpa backups antigos"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
    
    try:
        data = request.get_json() or {}
        keep_count = int(data.get('keep_count', 10))
        keep_days = int(data.get('keep_days', 30))
        
        removed_count = backup_service.cleanup_old_backups(
            keep_count=keep_count,
            keep_days=keep_days
        )
        
        # Registrar log de auditoria
        audit_service.log_action(
            admin_id=current_user.id,
            action='DELETE',
            resource_type='Backup',
            resource_id=None,
            description=f'Limpou {removed_count} backups antigos',
            changes={'removed_count': removed_count, 'keep_count': keep_count, 'keep_days': keep_days}
        )
        
        return jsonify({
            'success': True,
            'message': f'{removed_count} backups removidos',
            'removed_count': removed_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro ao limpar backups: {str(e)}'
        }), 500
