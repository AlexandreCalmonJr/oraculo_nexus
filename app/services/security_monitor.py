"""
Serviço de Monitoramento de Segurança
Detecta atividades suspeitas e envia alertas para super-admins
"""
from datetime import datetime, timedelta
from app.extensions import db
from app.models import AdminLog, User
from app.services.notification_service import notification_service
from sqlalchemy import func


class SecurityMonitor:
    """Monitor de segurança para detectar atividades suspeitas"""
    
    # Thresholds de segurança
    MAX_DELETIONS_PER_HOUR = 10
    MAX_FAILED_ACTIONS_PER_HOUR = 20
    MAX_ACTIONS_PER_MINUTE = 30
    SUSPICIOUS_HOURS = (0, 1, 2, 3, 4, 5)  # Horário suspeito: 00h-05h
    
    @staticmethod
    def check_suspicious_activity(admin_id):
        """
        Verifica se há atividade suspeita de um admin
        
        Returns:
            dict: {'is_suspicious': bool, 'reasons': [str], 'severity': str}
        """
        reasons = []
        severity = 'low'
        
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        one_minute_ago = now - timedelta(minutes=1)
        
        # 1. Verificar múltiplas exclusões em curto período
        recent_deletions = AdminLog.query.filter(
            AdminLog.admin_id == admin_id,
            AdminLog.action == 'DELETE',
            AdminLog.created_at >= one_hour_ago
        ).count()
        
        if recent_deletions >= SecurityMonitor.MAX_DELETIONS_PER_HOUR:
            reasons.append(f'Múltiplas exclusões detectadas: {recent_deletions} na última hora')
            severity = 'high'
        
        # 2. Verificar ações em horário suspeito
        current_hour = now.hour
        if current_hour in SecurityMonitor.SUSPICIOUS_HOURS:
            recent_actions = AdminLog.query.filter(
                AdminLog.admin_id == admin_id,
                AdminLog.created_at >= one_hour_ago
            ).count()
            
            if recent_actions > 5:
                reasons.append(f'Atividade fora do horário normal: {recent_actions} ações às {current_hour}h')
                severity = 'medium' if severity == 'low' else severity
        
        # 3. Verificar taxa de ações muito alta
        actions_per_minute = AdminLog.query.filter(
            AdminLog.admin_id == admin_id,
            AdminLog.created_at >= one_minute_ago
        ).count()
        
        if actions_per_minute >= SecurityMonitor.MAX_ACTIONS_PER_MINUTE:
            reasons.append(f'Taxa de ações muito alta: {actions_per_minute} ações no último minuto')
            severity = 'high'
        
        # 4. Verificar mudanças de IP suspeitas
        recent_logs = AdminLog.query.filter(
            AdminLog.admin_id == admin_id,
            AdminLog.created_at >= one_hour_ago
        ).order_by(AdminLog.created_at.desc()).limit(10).all()
        
        if recent_logs:
            ips = set(log.ip_address for log in recent_logs if log.ip_address)
            if len(ips) > 3:
                reasons.append(f'Múltiplos IPs detectados: {len(ips)} IPs diferentes na última hora')
                severity = 'high'
        
        # 5. Verificar padrão de exclusões em massa
        if recent_deletions > 0:
            deletion_logs = AdminLog.query.filter(
                AdminLog.admin_id == admin_id,
                AdminLog.action == 'DELETE',
                AdminLog.created_at >= one_hour_ago
            ).all()
            
            resource_types = [log.resource_type for log in deletion_logs]
            if len(set(resource_types)) == 1 and len(resource_types) >= 5:
                reasons.append(f'Exclusão em massa detectada: {len(resource_types)} {resource_types[0]}s deletados')
                severity = 'critical'
        
        is_suspicious = len(reasons) > 0
        
        return {
            'is_suspicious': is_suspicious,
            'reasons': reasons,
            'severity': severity,
            'admin_id': admin_id,
            'timestamp': now.isoformat()
        }
    
    @staticmethod
    def alert_super_admins(alert_data):
        """
        Envia alerta para todos os super-admins
        
        Args:
            alert_data: Dados do alerta de segurança
        """
        admin = User.query.get(alert_data['admin_id'])
        admin_name = admin.name if admin else f"Admin #{alert_data['admin_id']}"
        
        # Formatar mensagem de alerta
        severity_emoji = {
            'low': '⚠️',
            'medium': '🔶',
            'high': '🔴',
            'critical': '🚨'
        }
        
        emoji = severity_emoji.get(alert_data['severity'], '⚠️')
        
        message = f"{emoji} **ALERTA DE SEGURANÇA - {alert_data['severity'].upper()}**\n\n"
        message += f"**Admin:** {admin_name}\n"
        message += f"**Horário:** {datetime.fromisoformat(alert_data['timestamp']).strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        message += "**Atividades suspeitas detectadas:**\n"
        
        for i, reason in enumerate(alert_data['reasons'], 1):
            message += f"{i}. {reason}\n"
        
        # Buscar todos os super-admins (exceto o próprio admin suspeito)
        super_admins = User.query.filter(
            User.is_admin == True,
            User.id != alert_data['admin_id']
        ).all()
        
        # Enviar notificação para cada super-admin
        for super_admin in super_admins:
            notification_service.notify_user(
                user_id=super_admin.id,
                event_type='warning',
                message=message,
                category='security',
                data=alert_data,
                save_to_db=True
            )
        
        # Também enviar broadcast para admins conectados
        notification_service.notify_admins(
            event_type='warning',
            message=f"🔒 Atividade suspeita detectada de {admin_name}",
            category='security',
            data={'severity': alert_data['severity']}
        )
    
    @staticmethod
    def get_security_stats(days=30):
        """
        Retorna estatísticas de segurança
        
        Returns:
            dict: Estatísticas de atividades suspeitas
        """
        date_from = datetime.utcnow() - timedelta(days=days)
        
        # Total de exclusões
        total_deletions = AdminLog.query.filter(
            AdminLog.action == 'DELETE',
            AdminLog.created_at >= date_from
        ).count()
        
        # Exclusões por admin
        deletions_by_admin = db.session.query(
            AdminLog.admin_id,
            User.name,
            func.count(AdminLog.id).label('count')
        ).join(User, AdminLog.admin_id == User.id).filter(
            AdminLog.action == 'DELETE',
            AdminLog.created_at >= date_from
        ).group_by(AdminLog.admin_id, User.name).order_by(
            func.count(AdminLog.id).desc()
        ).limit(10).all()
        
        # Ações por horário
        hourly_activity = db.session.query(
            func.extract('hour', AdminLog.created_at).label('hour'),
            func.count(AdminLog.id).label('count')
        ).filter(
            AdminLog.created_at >= date_from
        ).group_by('hour').all()
        
        # Ações fora do horário
        suspicious_hours_count = AdminLog.query.filter(
            AdminLog.created_at >= date_from,
            func.extract('hour', AdminLog.created_at).in_(SecurityMonitor.SUSPICIOUS_HOURS)
        ).count()
        
        return {
            'total_deletions': total_deletions,
            'deletions_by_admin': [
                {'admin_id': admin_id, 'admin_name': name, 'count': count}
                for admin_id, name, count in deletions_by_admin
            ],
            'hourly_activity': [
                {'hour': int(hour), 'count': count}
                for hour, count in hourly_activity
            ],
            'suspicious_hours_count': suspicious_hours_count,
            'period_days': days
        }
    
    @staticmethod
    def get_admin_risk_score(admin_id, days=30):
        """
        Calcula score de risco de um admin
        
        Returns:
            dict: {'score': int (0-100), 'level': str, 'factors': [str]}
        """
        date_from = datetime.utcnow() - timedelta(days=days)
        
        score = 0
        factors = []
        
        # Fator 1: Número de exclusões
        deletions = AdminLog.query.filter(
            AdminLog.admin_id == admin_id,
            AdminLog.action == 'DELETE',
            AdminLog.created_at >= date_from
        ).count()
        
        if deletions > 50:
            score += 30
            factors.append(f'Alto número de exclusões: {deletions}')
        elif deletions > 20:
            score += 15
            factors.append(f'Número moderado de exclusões: {deletions}')
        
        # Fator 2: Atividade fora do horário
        suspicious_actions = AdminLog.query.filter(
            AdminLog.admin_id == admin_id,
            AdminLog.created_at >= date_from,
            func.extract('hour', AdminLog.created_at).in_(SecurityMonitor.SUSPICIOUS_HOURS)
        ).count()
        
        if suspicious_actions > 10:
            score += 25
            factors.append(f'Atividade fora do horário: {suspicious_actions} ações')
        elif suspicious_actions > 5:
            score += 10
            factors.append(f'Alguma atividade fora do horário: {suspicious_actions} ações')
        
        # Fator 3: Variação de IPs
        logs_with_ip = AdminLog.query.filter(
            AdminLog.admin_id == admin_id,
            AdminLog.created_at >= date_from,
            AdminLog.ip_address.isnot(None)
        ).all()
        
        unique_ips = len(set(log.ip_address for log in logs_with_ip))
        if unique_ips > 5:
            score += 20
            factors.append(f'Múltiplos IPs: {unique_ips} IPs diferentes')
        elif unique_ips > 3:
            score += 10
            factors.append(f'Alguns IPs diferentes: {unique_ips}')
        
        # Fator 4: Taxa de ações
        total_actions = AdminLog.query.filter(
            AdminLog.admin_id == admin_id,
            AdminLog.created_at >= date_from
        ).count()
        
        actions_per_day = total_actions / days
        if actions_per_day > 50:
            score += 15
            factors.append(f'Alta taxa de ações: {actions_per_day:.1f} por dia')
        
        # Determinar nível de risco
        if score >= 70:
            level = 'critical'
        elif score >= 50:
            level = 'high'
        elif score >= 30:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'score': min(score, 100),
            'level': level,
            'factors': factors,
            'admin_id': admin_id
        }


# Instância global
security_monitor = SecurityMonitor()
