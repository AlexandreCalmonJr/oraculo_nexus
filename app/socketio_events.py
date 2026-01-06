"""
Event Handlers para SocketIO
Gerencia conexões e salas de usuários
"""
from flask import request
from flask_socketio import join_room, leave_room, emit
from flask_login import current_user


def register_socketio_events(socketio):
    """Registra todos os event handlers do SocketIO"""
    
    @socketio.on('connect')
    def handle_connect():
        """Evento de conexão do cliente"""
        print(f'[SocketIO] Cliente conectado: {request.sid}')
        
        if current_user.is_authenticated:
            # Entrar na sala do usuário
            join_room(f'user_{current_user.id}')
            print(f'[SocketIO] Usuário {current_user.name} entrou na sala user_{current_user.id}')
            
            # Se for admin, entrar na sala de admins
            if current_user.is_admin:
                join_room('admins')
                print(f'[SocketIO] Admin {current_user.name} entrou na sala admins')
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Evento de desconexão do cliente"""
        print(f'[SocketIO] Cliente desconectado: {request.sid}')
    
    @socketio.on('join_user_room')
    def handle_join_user_room(data):
        """Permite que o cliente entre na sua sala de usuário"""
        if current_user.is_authenticated:
            user_id = data.get('user_id')
            if user_id == current_user.id:
                join_room(f'user_{user_id}')
                emit('room_joined', {'room': f'user_{user_id}'})
    
    @socketio.on('join_admin_room')
    def handle_join_admin_room():
        """Permite que admins entrem na sala de admins"""
        if current_user.is_authenticated and current_user.is_admin:
            join_room('admins')
            emit('room_joined', {'room': 'admins'})
    
    @socketio.on('leave_user_room')
    def handle_leave_user_room(data):
        """Permite que o cliente saia da sua sala de usuário"""
        if current_user.is_authenticated:
            user_id = data.get('user_id')
            if user_id == current_user.id:
                leave_room(f'user_{user_id}')
                emit('room_left', {'room': f'user_{user_id}'})
