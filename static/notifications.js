/**
 * Sistema de Notificações em Tempo Real
 * Gerencia notificações via WebSocket
 */

class NotificationManager {
    constructor() {
        this.socket = null;
        this.container = null;
        this.notifications = [];
        this.maxNotifications = 5;
        this.init();
    }

    init() {
        // Criar container de notificações
        this.createContainer();

        // Conectar ao WebSocket
        this.connectSocket();
    }

    createContainer() {
        // Criar container se não existir
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
            this.container = container;
        } else {
            this.container = document.getElementById('notification-container');
        }
    }

    connectSocket() {
        // Conectar ao servidor SocketIO
        this.socket = io();

        // Listener para notificações gerais
        this.socket.on('notification', (data) => {
            this.showNotification(data);
        });

        // Listener para notificações admin
        this.socket.on('admin_notification', (data) => {
            this.showNotification(data);
        });

        // Eventos de conexão
        this.socket.on('connect', () => {
            console.log('[Notifications] Conectado ao servidor');

            // Entrar na sala do usuário se estiver logado
            const userId = document.body.dataset.userId;
            if (userId) {
                this.socket.emit('join_user_room', { user_id: userId });
            }

            // Entrar na sala de admins se for admin
            const isAdmin = document.body.dataset.isAdmin === 'true';
            if (isAdmin) {
                this.socket.emit('join_admin_room');
            }
        });

        this.socket.on('disconnect', () => {
            console.log('[Notifications] Desconectado do servidor');
        });
    }

    showNotification(data) {
        const { type, message, timestamp } = data;

        // Criar elemento de notificação
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;

        // Ícone baseado no tipo
        const icons = {
            success: 'fa-check-circle',
            info: 'fa-info-circle',
            warning: 'fa-exclamation-triangle',
            error: 'fa-times-circle'
        };

        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas ${icons[type] || 'fa-bell'}"></i>
            </div>
            <div class="notification-content">
                <p class="notification-message">${message}</p>
                <span class="notification-time">${this.formatTime(timestamp)}</span>
            </div>
            <button class="notification-close" onclick="notificationManager.closeNotification(this)">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Adicionar ao container
        this.container.appendChild(notification);
        this.notifications.push(notification);

        // Animar entrada
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        // Auto-remover após 5 segundos
        setTimeout(() => {
            this.closeNotification(notification);
        }, 5000);

        // Limitar número de notificações
        if (this.notifications.length > this.maxNotifications) {
            const oldest = this.notifications.shift();
            this.closeNotification(oldest);
        }

        // Tocar som (opcional)
        this.playSound(type);
    }

    closeNotification(element) {
        if (typeof element === 'object' && element.parentElement) {
            element.classList.remove('show');
            setTimeout(() => {
                if (element.parentElement) {
                    element.parentElement.removeChild(element);
                }
                const index = this.notifications.indexOf(element);
                if (index > -1) {
                    this.notifications.splice(index, 1);
                }
            }, 300);
        } else if (typeof element === 'object') {
            // Chamado do botão de fechar
            const notification = element.closest('.notification');
            this.closeNotification(notification);
        }
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = Math.floor((now - date) / 1000); // segundos

        if (diff < 60) return 'Agora';
        if (diff < 3600) return `${Math.floor(diff / 60)}m atrás`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h atrás`;
        return date.toLocaleDateString();
    }

    playSound(type) {
        // Som opcional (pode ser desabilitado pelo usuário)
        if (localStorage.getItem('notificationSound') !== 'false') {
            const audio = new Audio('/static/sounds/notification.mp3');
            audio.volume = 0.3;
            audio.play().catch(() => {
                // Ignorar erro se som não estiver disponível
            });
        }
    }

    updateBadge(count) {
        /**
         * Atualiza o badge de notificações não lidas no navbar
         */
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.style.display = 'block';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    async fetchUnreadCount() {
        /**
         * Busca a contagem de notificações não lidas
         */
        try {
            const response = await fetch('/notifications/api/unread-count');
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.updateBadge(data.unread_count);
                }
            }
        } catch (error) {
            console.log('[Notifications] Erro ao buscar contagem:', error);
        }
    }
}

// Inicializar quando o DOM estiver pronto
let notificationManager;
document.addEventListener('DOMContentLoaded', () => {
    notificationManager = new NotificationManager();

    // Buscar contagem inicial de notificações não lidas
    if (notificationManager.socket) {
        notificationManager.socket.on('connect', () => {
            notificationManager.fetchUnreadCount();
        });
    }

    // Atualizar contagem a cada 60 segundos
    setInterval(() => {
        notificationManager.fetchUnreadCount();
    }, 60000);
});
