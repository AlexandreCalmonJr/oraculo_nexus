/**
 * Gerenciador de Página de Notificações
 * Gerencia a interface de notificações com filtros, paginação e ações
 */

class NotificationPageManager {
    constructor() {
        this.currentFilter = 'all';
        this.currentPage = 1;
        this.perPage = 20;
        this.totalPages = 1;
        this.csrfToken = document.querySelector('input[name="csrf_token"]')?.value || '';

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadNotifications();

        // Atualizar a cada 30 segundos
        setInterval(() => this.loadNotifications(), 30000);
    }

    setupEventListeners() {
        // Filtros
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setFilter(e.currentTarget.dataset.filter);
            });
        });

        // Ações em massa
        document.getElementById('markAllReadBtn')?.addEventListener('click', () => {
            this.markAllAsRead();
        });

        document.getElementById('clearReadBtn')?.addEventListener('click', () => {
            this.clearReadNotifications();
        });

        // Paginação
        document.getElementById('prevPage')?.addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadNotifications();
            }
        });

        document.getElementById('nextPage')?.addEventListener('click', () => {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
                this.loadNotifications();
            }
        });
    }

    setFilter(filter) {
        this.currentFilter = filter;
        this.currentPage = 1;

        // Atualizar UI dos filtros
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });

        this.loadNotifications();
    }

    async loadNotifications() {
        const listContainer = document.getElementById('notificationsList');
        const emptyState = document.getElementById('emptyState');
        const paginationContainer = document.getElementById('paginationContainer');

        // Mostrar loading
        listContainer.innerHTML = '<div class="loading-state"><i class="fas fa-spinner fa-spin"></i> Carregando notificações...</div>';
        emptyState.style.display = 'none';

        try {
            const response = await fetch(
                `/notifications/api/list?filter=${this.currentFilter}&page=${this.currentPage}&per_page=${this.perPage}`
            );

            if (!response.ok) throw new Error('Erro ao carregar notificações');

            const data = await response.json();

            if (data.success) {
                this.renderNotifications(data.notifications);
                this.updateCounts(data);
                this.updatePagination(data);

                // Mostrar/ocultar estados
                if (data.notifications.length === 0) {
                    listContainer.innerHTML = '';
                    emptyState.style.display = 'block';
                    paginationContainer.style.display = 'none';
                } else {
                    emptyState.style.display = 'none';
                    paginationContainer.style.display = 'flex';
                }
            }
        } catch (error) {
            console.error('Erro ao carregar notificações:', error);
            listContainer.innerHTML = '<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>Erro ao carregar notificações</p></div>';
        }
    }

    renderNotifications(notifications) {
        const listContainer = document.getElementById('notificationsList');

        if (notifications.length === 0) {
            listContainer.innerHTML = '';
            return;
        }

        listContainer.innerHTML = notifications.map(notification => {
            const iconClass = this.getIconClass(notification.category);
            const timeAgo = this.formatTimeAgo(notification.created_at);

            return `
                <div class="notification-item ${notification.is_read ? 'read' : 'unread'}" data-id="${notification.id}">
                    <div class="notification-icon ${notification.type}">
                        <i class="fas ${iconClass}"></i>
                    </div>
                    <div class="notification-content">
                        <p class="notification-message">${notification.message}</p>
                        <div class="notification-meta">
                            <span class="notification-time">${timeAgo}</span>
                            <span class="notification-category">${this.formatCategory(notification.category)}</span>
                        </div>
                    </div>
                    <div class="notification-actions">
                        ${notification.is_read
                    ? `<button class="notification-action-btn" onclick="notificationPageManager.markAsUnread(${notification.id})" title="Marcar como não lida">
                                <i class="fas fa-envelope"></i>
                               </button>`
                    : `<button class="notification-action-btn" onclick="notificationPageManager.markAsRead(${notification.id})" title="Marcar como lida">
                                <i class="fas fa-check"></i>
                               </button>`
                }
                        <button class="notification-action-btn delete" onclick="notificationPageManager.deleteNotification(${notification.id})" title="Excluir">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    getIconClass(category) {
        const icons = {
            welcome: 'fa-hand-sparkles',
            challenge: 'fa-trophy',
            level_up: 'fa-level-up-alt',
            boss: 'fa-dragon',
            team: 'fa-users',
            achievement: 'fa-medal',
            event: 'fa-calendar-star',
            system: 'fa-cog',
            admin: 'fa-shield-alt',
            user_registration: 'fa-user-plus',
            general: 'fa-bell'
        };
        return icons[category] || icons.general;
    }

    formatCategory(category) {
        const translations = {
            welcome: 'Boas-vindas',
            challenge: 'Desafio',
            level_up: 'Level Up',
            boss: 'Boss Fight',
            team: 'Time',
            achievement: 'Conquista',
            event: 'Evento',
            system: 'Sistema',
            admin: 'Admin',
            user_registration: 'Novo Usuário',
            general: 'Geral'
        };
        return translations[category] || category;
    }

    formatTimeAgo(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = Math.floor((now - date) / 1000); // segundos

        if (diff < 60) return 'Agora';
        if (diff < 3600) return `${Math.floor(diff / 60)}m atrás`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h atrás`;
        if (diff < 604800) return `${Math.floor(diff / 86400)}d atrás`;
        return date.toLocaleDateString('pt-BR');
    }

    updateCounts(data) {
        document.getElementById('count-all').textContent = data.total;
        document.getElementById('count-unread').textContent = data.unread_count;
        document.getElementById('count-read').textContent = data.total - data.unread_count;

        // Atualizar badge do navbar se existir
        if (window.notificationManager) {
            window.notificationManager.updateBadge(data.unread_count);
        }
    }

    updatePagination(data) {
        this.totalPages = data.total_pages;
        this.currentPage = data.page;

        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');
        const info = document.getElementById('paginationInfo');

        if (prevBtn) prevBtn.disabled = this.currentPage <= 1;
        if (nextBtn) nextBtn.disabled = this.currentPage >= this.totalPages;
        if (info) info.textContent = `Página ${this.currentPage} de ${this.totalPages}`;
    }

    async markAsRead(notificationId) {
        try {
            const response = await fetch(`/notifications/api/${notificationId}/read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (response.ok) {
                this.loadNotifications();
            }
        } catch (error) {
            console.error('Erro ao marcar como lida:', error);
        }
    }

    async markAsUnread(notificationId) {
        try {
            const response = await fetch(`/notifications/api/${notificationId}/unread`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (response.ok) {
                this.loadNotifications();
            }
        } catch (error) {
            console.error('Erro ao marcar como não lida:', error);
        }
    }

    async deleteNotification(notificationId) {
        if (!confirm('Tem certeza que deseja excluir esta notificação?')) {
            return;
        }

        try {
            const response = await fetch(`/notifications/api/${notificationId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (response.ok) {
                this.loadNotifications();
            }
        } catch (error) {
            console.error('Erro ao excluir notificação:', error);
        }
    }

    async markAllAsRead() {
        try {
            const response = await fetch('/notifications/api/mark-all-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (response.ok) {
                this.loadNotifications();
            }
        } catch (error) {
            console.error('Erro ao marcar todas como lidas:', error);
        }
    }

    async clearReadNotifications() {
        if (!confirm('Tem certeza que deseja excluir todas as notificações lidas?')) {
            return;
        }

        try {
            const response = await fetch('/notifications/api/clear-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (response.ok) {
                this.loadNotifications();
            }
        } catch (error) {
            console.error('Erro ao limpar notificações lidas:', error);
        }
    }
}

// Inicializar quando o DOM estiver pronto
let notificationPageManager;
document.addEventListener('DOMContentLoaded', () => {
    notificationPageManager = new NotificationPageManager();
});
