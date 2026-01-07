/**
 * Sidebar Controller - Oráculo Nexus
 * Script unificado para controle do sidebar em desktop e mobile
 * VERSÃO CORRIGIDA
 */

(function () {
    'use strict';

    console.log('[SIDEBAR] Initializing...');

    // Aguardar DOM estar pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSidebar);
    } else {
        initSidebar();
    }

    function initSidebar() {
        // Elementos do DOM
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebarOverlay = document.getElementById('sidebar-overlay');
        const sidebarLinks = document.querySelectorAll('.sidebar-item');

        // Validar elementos essenciais
        if (!sidebar || !sidebarToggle) {
            console.error('[SIDEBAR] Required elements not found!', {
                sidebar: !!sidebar,
                sidebarToggle: !!sidebarToggle
            });
            return;
        }

        console.log('[SIDEBAR] Elements found successfully');

        // Verificar se é mobile
        function isMobile() {
            return window.innerWidth <= 768;
        }

        // Garantir visibilidade do botão toggle
        function ensureToggleVisible() {
            if (sidebarToggle) {
                sidebarToggle.style.display = 'flex';
                console.log('[SIDEBAR] Toggle button visibility ensured');
            }
        }

        // Restaurar estado salvo (apenas desktop)
        function restoreSidebarState() {
            if (!isMobile()) {
                const savedState = localStorage.getItem('sidebarCollapsed');
                if (savedState === 'true') {
                    sidebar.classList.add('collapsed');
                    console.log('[SIDEBAR] Restored collapsed state from localStorage');
                }
            } else {
                // No mobile, garantir que sidebar está fechado e botão visível
                sidebar.classList.remove('mobile-open');
                sidebar.classList.remove('collapsed');
                ensureToggleVisible();
                console.log('[SIDEBAR] Mobile mode initialized - sidebar closed');
            }
        }

        // Toggle sidebar - Desktop
        function toggleDesktop() {
            sidebar.classList.toggle('collapsed');
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
            console.log('[SIDEBAR] Desktop toggle - Collapsed:', isCollapsed);
        }

        // Toggle sidebar - Mobile
        function toggleMobile() {
            const isOpen = sidebar.classList.toggle('mobile-open');

            if (sidebarOverlay) {
                if (isOpen) {
                    sidebarOverlay.classList.add('active');
                } else {
                    sidebarOverlay.classList.remove('active');
                }
            }

            console.log('[SIDEBAR] Mobile toggle - Open:', isOpen);
        }

        // Fechar sidebar mobile
        function closeMobileSidebar() {
            if (isMobile()) {
                sidebar.classList.remove('mobile-open');
                if (sidebarOverlay) {
                    sidebarOverlay.classList.remove('active');
                }
                console.log('[SIDEBAR] Mobile sidebar closed');
            }
        }

        // Handler principal do toggle
        function handleToggleClick(event) {
            event.preventDefault();
            event.stopPropagation();

            if (isMobile()) {
                toggleMobile();
            } else {
                toggleDesktop();
            }
        }

        // Configurar event listener do botão toggle
        sidebarToggle.addEventListener('click', handleToggleClick);
        ensureToggleVisible(); // Garantir que botão está visível
        console.log('[SIDEBAR] Toggle button listener attached');

        // Configurar overlay (mobile)
        if (sidebarOverlay) {
            sidebarOverlay.addEventListener('click', closeMobileSidebar);
            console.log('[SIDEBAR] Overlay listener attached');
        }

        // Fechar sidebar ao clicar em links (mobile)
        sidebarLinks.forEach(link => {
            link.addEventListener('click', closeMobileSidebar);
        });
        console.log('[SIDEBAR] Link listeners attached');

        // Ajustar ao redimensionar janela
        let resizeTimer;
        window.addEventListener('resize', function () {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function () {
                const currentlyMobile = isMobile();

                if (!currentlyMobile) {
                    // Desktop: remover classes mobile e restaurar estado salvo
                    sidebar.classList.remove('mobile-open');
                    if (sidebarOverlay) {
                        sidebarOverlay.classList.remove('active');
                    }

                    // Restaurar estado collapsed do localStorage
                    const savedState = localStorage.getItem('sidebarCollapsed');
                    if (savedState === 'true') {
                        sidebar.classList.add('collapsed');
                    }

                    console.log('[SIDEBAR] Switched to desktop mode');
                } else {
                    // Mobile: garantir que está fechado e botão visível
                    sidebar.classList.remove('mobile-open');
                    sidebar.classList.remove('collapsed');
                    if (sidebarOverlay) {
                        sidebarOverlay.classList.remove('active');
                    }
                    ensureToggleVisible();
                    console.log('[SIDEBAR] Switched to mobile mode');
                }
            }, 250);
        });

        // Restaurar estado inicial
        restoreSidebarState();

        console.log('[SIDEBAR] Initialized successfully');
    }
})();