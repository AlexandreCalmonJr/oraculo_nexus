"""
Serviço de Auditoria para Logs Administrativos
Registra e gerencia todas as ações administrativas no sistema
"""
from flask import request
from flask_login import current_user
from datetime import datetime, timedelta
from app.extensions import db
from app.models.admin_log import AdminLog


class AuditService:
    """Serviço para gerenciar logs de auditoria administrativa"""
    
    @staticmethod
    def _get_client_info():
        """Captura informações do cliente (IP e User Agent)"""
        ip_address = request.remote_addr if request else None
        user_agent = request.headers.get('User-Agent', '')[:255] if request else None
        return ip_address, user_agent
    
    @staticmethod
    def log_action(admin_id, action, resource_type, resource_id, description, changes=None):
        """
        Registra uma ação administrativa genérica
        
        Args:
            admin_id: ID do administrador
            action: Tipo de ação (CREATE, UPDATE, DELETE, etc.)
            resource_type: Tipo de recurso (User, Challenge, etc.)
            resource_id: ID do recurso afetado
            description: Descrição detalhada da ação
            changes: Dicionário com mudanças (opcional)
        
        Returns:
            AdminLog: Objeto de log criado
        """
        ip_address, user_agent = AuditService._get_client_info()
        
        log = AdminLog(
            admin_id=admin_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            changes=changes or {}
        )
        
        db.session.add(log)
        db.session.commit()
        
        # Verificar atividade suspeita após ações críticas
        if action in ['DELETE', 'UPDATE'] and admin_id:
            try:
                from app.services.security_monitor import security_monitor
                alert = security_monitor.check_suspicious_activity(admin_id)
                
                if alert['is_suspicious'] and alert['severity'] in ['high', 'critical']:
                    security_monitor.alert_super_admins(alert)
            except Exception as e:
                print(f"Erro ao verificar segurança: {e}")
        
        return log
    
    @staticmethod
    def log_create(admin_id, resource_type, resource_id, resource_name, details=None):
        """Registra criação de recurso"""
        description = f"Criou {resource_type}: {resource_name}"
        changes = {'created': details} if details else None
        
        return AuditService.log_action(
            admin_id=admin_id,
            action='CREATE',
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            changes=changes
        )
    
    @staticmethod
    def log_update(admin_id, resource_type, resource_id, resource_name, old_data, new_data):
        """
        Registra atualização de recurso com diff
        
        Args:
            old_data: Dicionário com dados antigos
            new_data: Dicionário com dados novos
        """
        # Calcular diferenças
        changes = {
            'before': old_data,
            'after': new_data,
            'diff': {}
        }
        
        # Identificar campos alterados
        for key in new_data:
            if key in old_data and old_data[key] != new_data[key]:
                changes['diff'][key] = {
                    'old': old_data[key],
                    'new': new_data[key]
                }
        
        description = f"Atualizou {resource_type}: {resource_name}"
        if changes['diff']:
            fields = ', '.join(changes['diff'].keys())
            description += f" (campos: {fields})"
        
        return AuditService.log_action(
            admin_id=admin_id,
            action='UPDATE',
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            changes=changes
        )
    
    @staticmethod
    def log_delete(admin_id, resource_type, resource_id, resource_name, data=None):
        """Registra exclusão de recurso"""
        description = f"Deletou {resource_type}: {resource_name}"
        changes = {'deleted': data} if data else None
        
        return AuditService.log_action(
            admin_id=admin_id,
            action='DELETE',
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            changes=changes
        )
    
    @staticmethod
    def log_view(admin_id, resource_type, resource_id, resource_name):
        """Registra visualização de dados sensíveis"""
        description = f"Visualizou {resource_type}: {resource_name}"
        
        return AuditService.log_action(
            admin_id=admin_id,
            action='VIEW',
            resource_type=resource_type,
            resource_id=resource_id,
            description=description
        )
    
    @staticmethod
    def log_export(admin_id, resource_type, count, format='CSV'):
        """Registra exportação de dados"""
        description = f"Exportou {count} {resource_type}(s) em formato {format}"
        changes = {'count': count, 'format': format}
        
        return AuditService.log_action(
            admin_id=admin_id,
            action='EXPORT',
            resource_type=resource_type,
            resource_id=None,
            description=description,
            changes=changes
        )
    
    @staticmethod
    def log_broadcast(admin_id, message, recipients_count):
        """Registra envio de notificação broadcast"""
        description = f"Enviou notificação broadcast para {recipients_count} usuários"
        changes = {'message': message, 'recipients': recipients_count}
        
        return AuditService.log_action(
            admin_id=admin_id,
            action='BROADCAST',
            resource_type='Notification',
            resource_id=None,
            description=description,
            changes=changes
        )
    
    @staticmethod
    def log_import(admin_id, resource_type, count, source):
        """Registra importação de dados"""
        description = f"Importou {count} {resource_type}(s) de {source}"
        changes = {'count': count, 'source': source}
        
        return AuditService.log_action(
            admin_id=admin_id,
            action='IMPORT',
            resource_type=resource_type,
            resource_id=None,
            description=description,
            changes=changes
        )
    
    @staticmethod
    def get_logs(filters=None, limit=50, offset=0):
        """
        Busca logs com filtros
        
        Args:
            filters: Dicionário com filtros (admin_id, action, resource_type, date_from, date_to)
            limit: Número máximo de resultados
            offset: Offset para paginação
        
        Returns:
            dict: {'logs': [...], 'total': int}
        """
        query = AdminLog.query
        
        if filters:
            if 'admin_id' in filters and filters['admin_id']:
                query = query.filter_by(admin_id=filters['admin_id'])
            
            if 'action' in filters and filters['action']:
                query = query.filter_by(action=filters['action'])
            
            if 'resource_type' in filters and filters['resource_type']:
                query = query.filter_by(resource_type=filters['resource_type'])
            
            if 'date_from' in filters and filters['date_from']:
                query = query.filter(AdminLog.created_at >= filters['date_from'])
            
            if 'date_to' in filters and filters['date_to']:
                query = query.filter(AdminLog.created_at <= filters['date_to'])
        
        total = query.count()
        logs = query.order_by(AdminLog.created_at.desc()).limit(limit).offset(offset).all()
        
        return {
            'logs': [log.to_dict() for log in logs],
            'total': total
        }
    
    @staticmethod
    def get_user_activity(admin_id, days=30):
        """Retorna atividade de um admin nos últimos N dias"""
        date_from = datetime.utcnow() - timedelta(days=days)
        
        logs = AdminLog.query.filter(
            AdminLog.admin_id == admin_id,
            AdminLog.created_at >= date_from
        ).order_by(AdminLog.created_at.desc()).all()
        
        return [log.to_dict() for log in logs]
    
    @staticmethod
    def get_resource_history(resource_type, resource_id):
        """Retorna histórico completo de um recurso"""
        logs = AdminLog.query.filter_by(
            resource_type=resource_type,
            resource_id=resource_id
        ).order_by(AdminLog.created_at.desc()).all()
        
        return [log.to_dict() for log in logs]
    
    @staticmethod
    def get_stats(days=30):
        """Retorna estatísticas de auditoria"""
        from sqlalchemy import func
        
        date_from = datetime.utcnow() - timedelta(days=days)
        
        # Total de ações
        total_actions = AdminLog.query.filter(AdminLog.created_at >= date_from).count()
        
        # Ações por tipo
        actions_by_type = db.session.query(
            AdminLog.action,
            func.count(AdminLog.id).label('count')
        ).filter(AdminLog.created_at >= date_from).group_by(AdminLog.action).all()
        
        # Ações por admin
        actions_by_admin = db.session.query(
            AdminLog.admin_id,
            func.count(AdminLog.id).label('count')
        ).filter(AdminLog.created_at >= date_from).group_by(AdminLog.admin_id).all()
        
        # Recursos mais modificados
        resources_modified = db.session.query(
            AdminLog.resource_type,
            func.count(AdminLog.id).label('count')
        ).filter(AdminLog.created_at >= date_from).group_by(AdminLog.resource_type).all()
        
        return {
            'total_actions': total_actions,
            'actions_by_type': [{'action': a, 'count': c} for a, c in actions_by_type],
            'actions_by_admin': [{'admin_id': a, 'count': c} for a, c in actions_by_admin],
            'resources_modified': [{'resource': r, 'count': c} for r, c in resources_modified]
        }


# Instância global do serviço
audit_service = AuditService()
