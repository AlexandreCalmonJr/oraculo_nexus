/**
 * Backup Manager
 * Gerencia interface de backups
 */

class BackupManager {
    constructor() {
        this.currentRestoreId = null;
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadBackups();
    }

    setupEventListeners() {
        document.getElementById('createBackupBtn')?.addEventListener('click', () => {
            this.createBackup();
        });

        document.getElementById('cleanupBtn')?.addEventListener('click', () => {
            this.cleanupBackups();
        });
    }

    async loadBackups() {
        try {
            const response = await fetch('/admin/backup/api/list');
            const data = await response.json();

            if (data.success) {
                this.renderStats(data.stats);
                this.renderBackups(data.backups);
            }
        } catch (error) {
            console.error('Erro ao carregar backups:', error);
        }
    }

    renderStats(stats) {
        document.getElementById('totalBackups').textContent = stats.total_backups;
        document.getElementById('totalSize').textContent = stats.total_size_mb + ' MB';

        if (stats.latest_backup) {
            const date = new Date(stats.latest_backup.created_at);
            document.getElementById('lastBackup').textContent = date.toLocaleString('pt-BR');
        } else {
            document.getElementById('lastBackup').textContent = 'Nunca';
        }
    }

    renderBackups(backups) {
        const tbody = document.getElementById('backupsTableBody');

        if (backups.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-cell">Nenhum backup encontrado</td></tr>';
            return;
        }

        tbody.innerHTML = backups.map(backup => `
            <tr>
                <td>${this.formatDate(backup.created_at)}</td>
                <td><span class="type-badge type-${backup.backup_type}">${backup.backup_type}</span></td>
                <td>${backup.size_mb} MB</td>
                <td>${backup.creator_name}</td>
                <td><span class="status-badge status-${backup.is_valid ? 'valid' : 'invalid'}">${backup.is_valid ? 'Valido' : 'Invalido'}</span></td>
                <td>
                    <button class="action-btn" onclick="backupManager.validateBackup(${backup.id})" title="Validar">
                        <i class="fas fa-check-circle"></i>
                    </button>
                    <button class="action-btn" onclick="backupManager.downloadBackup(${backup.id})" title="Download">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="action-btn" onclick="backupManager.showRestoreModal(${backup.id}, '${backup.filename}')" title="Restaurar">
                        <i class="fas fa-undo"></i>
                    </button>
                    <button class="action-btn" onclick="backupManager.deleteBackup(${backup.id})" title="Deletar">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleString('pt-BR');
    }

    async createBackup() {
        const notes = prompt('Notas sobre este backup (opcional):');

        const btn = document.getElementById('createBackupBtn');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Criando...';

        try {
            const response = await fetch('/admin/backup/api/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ notes: notes || '' })
            });

            const data = await response.json();

            if (data.success) {
                alert('Backup criado com sucesso!');
                await this.loadBackups();
            } else {
                alert('Erro ao criar backup: ' + data.error);
            }
        } catch (error) {
            alert('Erro ao criar backup: ' + error.message);
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-plus"></i> Criar Backup';
        }
    }

    async validateBackup(backupId) {
        try {
            const response = await fetch(`/admin/backup/api/validate/${backupId}`);
            const data = await response.json();

            if (data.success) {
                const validation = data.validation;
                if (validation.is_valid) {
                    alert('✓ Backup valido!');
                } else {
                    alert('✗ Backup invalido: ' + validation.message);
                }
                await this.loadBackups();
            }
        } catch (error) {
            alert('Erro ao validar backup: ' + error.message);
        }
    }

    downloadBackup(backupId) {
        window.location.href = `/admin/backup/api/download/${backupId}`;
    }

    showRestoreModal(backupId, filename) {
        this.currentRestoreId = backupId;
        document.getElementById('restoreBackupName').textContent = filename;
        document.getElementById('restoreModal').style.display = 'flex';
    }

    async confirmRestore() {
        if (!this.currentRestoreId) return;

        closeRestoreModal();

        try {
            const response = await fetch(`/admin/backup/api/restore/${this.currentRestoreId}`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                alert('✓ Banco de dados restaurado com sucesso!\n\nA aplicacao sera recarregada.');
                setTimeout(() => window.location.reload(), 2000);
            } else {
                alert('✗ Erro ao restaurar backup: ' + data.message);
            }
        } catch (error) {
            alert('Erro ao restaurar backup: ' + error.message);
        }
    }

    async deleteBackup(backupId) {
        if (!confirm('Tem certeza que deseja deletar este backup?')) return;

        try {
            const response = await fetch(`/admin/backup/api/delete/${backupId}`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                alert('Backup removido com sucesso!');
                await this.loadBackups();
            } else {
                alert('Erro ao remover backup: ' + data.error);
            }
        } catch (error) {
            alert('Erro ao remover backup: ' + error.message);
        }
    }

    async cleanupBackups() {
        const keepCount = prompt('Quantos backups recentes manter?', '10');
        const keepDays = prompt('Manter backups dos ultimos quantos dias?', '30');

        if (!keepCount || !keepDays) return;

        try {
            const response = await fetch('/admin/backup/api/cleanup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    keep_count: parseInt(keepCount),
                    keep_days: parseInt(keepDays)
                })
            });

            const data = await response.json();

            if (data.success) {
                alert(`${data.removed_count} backups removidos!`);
                await this.loadBackups();
            } else {
                alert('Erro ao limpar backups: ' + data.error);
            }
        } catch (error) {
            alert('Erro ao limpar backups: ' + error.message);
        }
    }
}

function closeRestoreModal() {
    document.getElementById('restoreModal').style.display = 'none';
}

function confirmRestore() {
    backupManager.confirmRestore();
}

// Inicializar
let backupManager;
document.addEventListener('DOMContentLoaded', () => {
    backupManager = new BackupManager();
});
