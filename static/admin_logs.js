/**
 * Admin Logs Manager
 * Gerencia a interface de logs de auditoria
 */

class AdminLogsManager {
    constructor() {
        this.currentPage = 1;
        this.perPage = 50;
        this.totalPages = 1;
        this.filters = {};

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadLogs();
    }

    setupEventListeners() {
        // Botoes de filtro
        document.getElementById('applyFilters')?.addEventListener('click', () => {
            this.applyFilters();
        });

        document.getElementById('clearFilters')?.addEventListener('click', () => {
            this.clearFilters();
        });

        // Exportar
        document.getElementById('exportBtn')?.addEventListener('click', () => {
            this.exportLogs();
        });

        // Paginacao
        document.getElementById('prevPage')?.addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadLogs();
            }
        });

        document.getElementById('nextPage')?.addEventListener('click', () => {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
                this.loadLogs();
            }
        });
    }

    applyFilters() {
        this.filters = {};

        const adminId = document.getElementById('filterAdmin').value;
        if (adminId) this.filters.admin_id = adminId;

        const action = document.getElementById('filterAction').value;
        if (action) this.filters.action = action;

        const resourceType = document.getElementById('filterResource').value;
        if (resourceType) this.filters.resource_type = resourceType;

        this.currentPage = 1;
        this.loadLogs();
    }

    clearFilters() {
        this.filters = {};
        document.getElementById('filterAdmin').value = '';
        document.getElementById('filterAction').value = '';
        document.getElementById('filterResource').value = '';
        this.currentPage = 1;
        this.loadLogs();
    }

    async loadLogs() {
        const tbody = document.getElementById('logsTableBody');
        tbody.innerHTML = '<tr><td colspan="7" class="loading-cell"><i class="fas fa-spinner fa-spin"></i> Carregando logs...</td></tr>';

        try {
            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: this.perPage,
                ...this.filters
            });

            const response = await fetch(`/admin/logs/api/list?${params}`);
            const data = await response.json();

            if (data.success) {
                this.renderLogs(data.logs);
                this.updatePagination(data);
            }
        } catch (error) {
            console.error('Erro ao carregar logs:', error);
            tbody.innerHTML = '<tr><td colspan="7" class="error-cell">Erro ao carregar logs</td></tr>';
        }
    }

    renderLogs(logs) {
        const tbody = document.getElementById('logsTableBody');

        if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="empty-cell">Nenhum log encontrado</td></tr>';
            return;
        }

        tbody.innerHTML = logs.map(log => `
            <tr>
                <td>${this.formatDate(log.created_at)}</td>
                <td>${log.admin_name}</td>
                <td><span class="action-badge action-${log.action}">${log.action}</span></td>
                <td>${log.resource_type}</td>
                <td>${log.description}</td>
                <td>${log.ip_address || '-'}</td>
                <td>
                    <button class="btn-details" onclick="adminLogsManager.showDetails(${log.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleString('pt-BR');
    }

    updatePagination(data) {
        this.totalPages = data.total_pages;
        this.currentPage = data.page;

        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');
        const info = document.getElementById('paginationInfo');

        if (prevBtn) prevBtn.disabled = this.currentPage <= 1;
        if (nextBtn) nextBtn.disabled = this.currentPage >= this.totalPages;
        if (info) info.textContent = `Pagina ${this.currentPage} de ${this.totalPages}`;
    }

    async showDetails(logId) {
        try {
            const response = await fetch(`/admin/logs/api/${logId}`);
            const data = await response.json();

            if (data.success) {
                this.renderDetails(data.log);
                document.getElementById('logDetailsModal').style.display = 'flex';
            }
        } catch (error) {
            console.error('Erro ao carregar detalhes:', error);
        }
    }

    renderDetails(log) {
        const body = document.getElementById('logDetailsBody');

        let changesHtml = '';
        if (log.changes && Object.keys(log.changes).length > 0) {
            changesHtml = '<h3>Mudancas:</h3><pre>' + JSON.stringify(log.changes, null, 2) + '</pre>';
        }

        body.innerHTML = `
            <div class="log-details">
                <p><strong>ID:</strong> ${log.id}</p>
                <p><strong>Admin:</strong> ${log.admin_name}</p>
                <p><strong>Acao:</strong> <span class="action-badge action-${log.action}">${log.action}</span></p>
                <p><strong>Recurso:</strong> ${log.resource_type} ${log.resource_id ? '#' + log.resource_id : ''}</p>
                <p><strong>Descricao:</strong> ${log.description}</p>
                <p><strong>Data/Hora:</strong> ${this.formatDate(log.created_at)}</p>
                <p><strong>IP:</strong> ${log.ip_address || 'N/A'}</p>
                <p><strong>User Agent:</strong> ${log.user_agent || 'N/A'}</p>
                ${changesHtml}
            </div>
        `;
    }

    exportLogs() {
        const params = new URLSearchParams(this.filters);
        window.location.href = `/admin/logs/api/export?${params}`;
    }
}

function closeLogDetails() {
    document.getElementById('logDetailsModal').style.display = 'none';
}

// Inicializar
let adminLogsManager;
document.addEventListener('DOMContentLoaded', () => {
    adminLogsManager = new AdminLogsManager();
});
