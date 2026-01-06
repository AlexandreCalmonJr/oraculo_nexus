# Script para corrigir sidebar mobile

import os

css_file = r'c:\Users\Administrator\oraculo_nexus\static\sidebar.css'

with open(css_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Melhorar responsividade mobile
old_mobile = '''/* ===== RESPONSIVIDADE ===== */
@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
        width: 240px;
    }

    .sidebar.mobile-open {
        transform: translateX(0);
    }

    .sidebar.collapsed {
        transform: translateX(-100%);
        width: 240px;
    }

    .topbar {
        left: 0;
    }

    .main-content {
        margin-left: 0;
        padding: 1rem;
    }

    .main-footer {
        margin-left: 0;
    }
}'''

new_mobile = '''/* ===== RESPONSIVIDADE ===== */
@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
        width: 280px;
        z-index: 2000;
    }

    .sidebar.mobile-open {
        transform: translateX(0);
        box-shadow: 2px 0 20px rgba(0, 0, 0, 0.3);
    }

    .sidebar.collapsed {
        transform: translateX(-100%);
        width: 280px;
    }

    /* Botao hamburger visivel no mobile */
    .sidebar-toggle {
        position: fixed;
        top: 1rem;
        left: 1rem;
        right: auto;
        z-index: 1500;
        background: var(--primary-500);
        color: white;
    }

    .sidebar.mobile-open .sidebar-toggle {
        left: auto;
        right: 1rem;
        background: var(--bg-tertiary);
        color: var(--text-primary);
    }

    .topbar {
        left: 0;
        padding-left: 4rem;
    }

    .main-content {
        margin-left: 0;
        padding: 1rem;
    }

    .main-footer {
        margin-left: 0;
    }

    /* Overlay para fechar sidebar */
    .sidebar-overlay {
        display: none;
    }

    .sidebar.mobile-open ~ .sidebar-overlay {
        display: block;
    }
}'''

content = content.replace(old_mobile, new_mobile)
print("OK: CSS mobile atualizado")

with open(css_file, 'w', encoding='utf-8') as f:
    f.write(content)

# Adicionar JavaScript para toggle mobile
js_code = '''
// Script para sidebar mobile
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const overlay = document.querySelector('.sidebar-overlay');

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            // No mobile, adiciona classe mobile-open
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('mobile-open');
            } else {
                // No desktop, toggle collapsed
                sidebar.classList.toggle('collapsed');
            }
        });
    }

    // Fechar sidebar ao clicar no overlay (mobile)
    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('mobile-open');
        });
    }

    // Fechar sidebar ao clicar em um link (mobile)
    const sidebarLinks = document.querySelectorAll('.sidebar-item');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('mobile-open');
            }
        });
    });
});
'''

js_file = r'c:\Users\Administrator\oraculo_nexus\static\sidebar_mobile.js'
with open(js_file, 'w', encoding='utf-8') as f:
    f.write(js_code)
print("OK: JavaScript mobile criado")

# Adicionar script nos templates
print("\nOK: Otimizacoes mobile aplicadas!")
print("\nPROXIMOS PASSOS:")
print("1. Adicione <script src=\"{{ url_for('static', filename='sidebar_mobile.js') }}\"></script>")
print("   nos templates admin_base.html e base_user.html")
print("2. Faca commit e push")
print("\nFuncionalidades mobile:")
print("- Botao hamburger sempre visivel")
print("- Sidebar desliza da esquerda")
print("- Overlay escuro ao abrir")
print("- Fecha ao clicar fora ou em um link")
