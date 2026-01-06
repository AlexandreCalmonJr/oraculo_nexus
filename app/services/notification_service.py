"""
Serviço de Notificações em Tempo Real
Gerencia notificações via WebSocket usando Flask-SocketIO
Agora com persistência em banco de dados
"""
from flask_socketio import emit
from datetime import datetime
from app.extensions import db
from app.models.notifications import Notification


class NotificationService:
    """Serviço para enviar notificações em tempo real e persistentes"""
    
    def __init__(self, socketio):
        self.socketio = socketio
    
    def _save_notification(self, user_id, event_type, category, message, data=None):
        """
        Salva notificação no banco de dados
        
        Args:
            user_id: ID do usuário (None para notificações globais)
            event_type: Tipo do evento ('success', 'info', 'warning', 'error')
            category: Categoria da notificação
            message: Mensagem da notificação
            data: Dados adicionais (opcional)
        
        Returns:
            Notification: Objeto de notificação criado
        """
        notification = Notification(
            user_id=user_id,
            type=event_type,
            category=category,
            message=message,
            data=data or {}
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    def notify_all(self, event_type, message, category='general', data=None, save_to_db=True):
        """
        Envia notificação para todos os usuários conectados
        
        Args:
            event_type: Tipo do evento ('success', 'info', 'warning', 'error')
            message: Mensagem da notificação
            category: Categoria da notificação
            data: Dados adicionais (opcional)
            save_to_db: Se True, salva no banco de dados
        """
        notification_data = {
            'type': event_type,
            'category': category,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': data or {}
        }
        
        # Salvar no banco se solicitado (notificações globais não são salvas por padrão)
        if save_to_db:
            # Para notificações broadcast, podemos criar uma entrada global
            self._save_notification(None, event_type, category, message, data)
        
        # Emitir para todos os clientes conectados
        self.socketio.emit('notification', notification_data, namespace='/')
    
    def notify_user(self, user_id, event_type, message, category='general', data=None, save_to_db=True):
        """
        Envia notificação para um usuário específico
        
        Args:
            user_id: ID do usuário
            event_type: Tipo do evento
            message: Mensagem da notificação
            category: Categoria da notificação
            data: Dados adicionais (opcional)
            save_to_db: Se True, salva no banco de dados
        """
        # Salvar no banco de dados
        if save_to_db:
            notification = self._save_notification(user_id, event_type, category, message, data)
            notification_data = notification.to_dict()
        else:
            notification_data = {
                'type': event_type,
                'category': category,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'data': data or {}
            }
        
        # Enviar via WebSocket
        self.socketio.emit('notification', notification_data, room=f'user_{user_id}')
    
    def notify_admins(self, event_type, message, category='admin', data=None, save_to_db=True):
        """
        Envia notificação apenas para administradores
        
        Args:
            event_type: Tipo do evento
            message: Mensagem da notificação
            category: Categoria da notificação
            data: Dados adicionais (opcional)
            save_to_db: Se True, salva no banco de dados para todos os admins
        """
        notification_data = {
            'type': event_type,
            'category': category,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'data': data or {}
        }
        
        # Salvar no banco para todos os admins
        if save_to_db:
            from app.models import User
            admins = User.query.filter_by(is_admin=True).all()
            for admin in admins:
                self._save_notification(admin.id, event_type, category, message, data)
        
        self.socketio.emit('admin_notification', notification_data, room='admins')
    
    # ===== MÉTODOS DE GERENCIAMENTO =====
    
    def get_user_notifications(self, user_id, filter_type='all', limit=50, offset=0):
        """
        Obtém notificações de um usuário
        
        Args:
            user_id: ID do usuário
            filter_type: 'all', 'unread', 'read'
            limit: Número máximo de notificações
            offset: Offset para paginação
        
        Returns:
            dict: Notificações e contagem total
        """
        query = Notification.query.filter_by(user_id=user_id)
        
        if filter_type == 'unread':
            query = query.filter_by(is_read=False)
        elif filter_type == 'read':
            query = query.filter_by(is_read=True)
        
        total = query.count()
        notifications = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset).all()
        
        return {
            'notifications': [n.to_dict() for n in notifications],
            'total': total,
            'unread_count': Notification.query.filter_by(user_id=user_id, is_read=False).count()
        }
    
    def mark_as_read(self, notification_id, user_id):
        """Marca notificação como lida"""
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False
    
    def mark_as_unread(self, notification_id, user_id):
        """Marca notificação como não lida"""
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.is_read = False
            db.session.commit()
            return True
        return False
    
    def mark_all_as_read(self, user_id):
        """Marca todas as notificações do usuário como lidas"""
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        return True
    
    def delete_notification(self, notification_id, user_id):
        """Deleta uma notificação"""
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            db.session.delete(notification)
            db.session.commit()
            return True
        return False
    
    def clear_read_notifications(self, user_id):
        """Deleta todas as notificações lidas do usuário"""
        Notification.query.filter_by(user_id=user_id, is_read=True).delete()
        db.session.commit()
        return True
    
    def get_unread_count(self, user_id):
        """Obtém contagem de notificações não lidas"""
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    # ===== EVENTOS ESPECÍFICOS =====
    
    def notify_new_user(self, username, user_id):
        """Notifica sobre novo usuário registrado"""
        # Notificação para o novo usuário
        self.notify_user(
            user_id,
            'success',
            f'🎉 Bem-vindo ao Oráculo Nexus, {username}! Explore os desafios e comece sua jornada.',
            category='welcome',
            data={'username': username}
        )
        
        # Notificação para admins
        self.notify_admins(
            'info',
            f'Novo usuário registrado: {username}',
            category='user_registration',
            data={'username': username, 'user_id': user_id}
        )
    
    def notify_challenge_completed(self, username, user_id, challenge_title, points):
        """Notifica sobre desafio completado"""
        # Notificação pessoal
        self.notify_user(
            user_id,
            'success',
            f'🎉 Você completou o desafio "{challenge_title}" e ganhou {points} pontos!',
            category='challenge',
            data={
                'username': username,
                'challenge': challenge_title,
                'points': points
            }
        )
        
        # Broadcast para todos (sem salvar no DB para evitar spam)
        self.notify_all(
            'success',
            f'🎉 {username} completou o desafio "{challenge_title}" e ganhou {points} pontos!',
            category='challenge',
            data={
                'username': username,
                'challenge': challenge_title,
                'points': points
            },
            save_to_db=False
        )
    
    def notify_level_up(self, username, user_id, new_level):
        """Notifica sobre subida de nível"""
        # Notificação pessoal
        self.notify_user(
            user_id,
            'success',
            f'🎊 Parabéns! Você subiu para o nível {new_level}!',
            category='level_up',
            data={
                'username': username,
                'level': new_level
            }
        )
        
        # Broadcast para todos (sem salvar no DB)
        self.notify_all(
            'success',
            f'🎊 {username} subiu para o nível {new_level}!',
            category='level_up',
            data={
                'username': username,
                'level': new_level
            },
            save_to_db=False
        )
    
    def notify_boss_defeated(self, boss_name, username, user_id):
        """Notifica sobre boss derrotado"""
        # Notificação pessoal
        self.notify_user(
            user_id,
            'success',
            f'⚔️ Você derrotou o boss "{boss_name}"!',
            category='boss',
            data={
                'username': username,
                'boss': boss_name
            }
        )
        
        # Broadcast para todos (sem salvar no DB)
        self.notify_all(
            'success',
            f'⚔️ {username} derrotou o boss "{boss_name}"!',
            category='boss',
            data={
                'username': username,
                'boss': boss_name
            },
            save_to_db=False
        )
    
    def notify_team_created(self, team_name, owner_name, owner_id):
        """Notifica sobre novo time criado"""
        # Notificação pessoal
        self.notify_user(
            owner_id,
            'success',
            f'👥 Você criou o time "{team_name}"!',
            category='team',
            data={
                'team': team_name,
                'owner': owner_name
            }
        )
        
        # Broadcast para todos (sem salvar no DB)
        self.notify_all(
            'info',
            f'👥 Novo time criado: "{team_name}" por {owner_name}',
            category='team',
            data={
                'team': team_name,
                'owner': owner_name
            },
            save_to_db=False
        )
    
    def notify_event_update(self, event_name, progress):
        """Notifica sobre atualização de evento global"""
        self.notify_all(
            'info',
            f'🌍 Evento "{event_name}": {progress}% completo',
            category='event',
            data={
                'event': event_name,
                'progress': progress
            },
            save_to_db=False
        )
    
    def notify_achievement_unlocked(self, username, user_id, achievement_name):
        """Notifica sobre conquista desbloqueada"""
        # Notificação pessoal
        self.notify_user(
            user_id,
            'success',
            f'🏆 Você desbloqueou a conquista "{achievement_name}"!',
            category='achievement',
            data={
                'username': username,
                'achievement': achievement_name
            }
        )
        
        # Broadcast para todos (sem salvar no DB)
        self.notify_all(
            'success',
            f'🏆 {username} desbloqueou a conquista "{achievement_name}"!',
            category='achievement',
            data={
                'username': username,
                'achievement': achievement_name
            },
            save_to_db=False
        )
    
    def notify_system_alert(self, message, severity='warning'):
        """Notifica sobre alerta do sistema"""
        self.notify_admins(
            severity,
            f'⚠️ Alerta do Sistema: {message}',
            category='system',
            data={'alert': message}
        )


# Instância global (será inicializada no __init__.py)
notification_service = None


def init_notification_service(socketio):
    """Inicializa o serviço de notificações"""
    global notification_service
    notification_service = NotificationService(socketio)
    return notification_service
