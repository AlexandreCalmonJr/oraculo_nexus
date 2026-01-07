/**
 * Mobile Bottom Navigation - Oráculo Nexus
 * Controla o menu mobile fixo na parte inferior
 */

(function () {
    'use strict';

    console.log('[MOBILE MENU] Initializing...');

    // Aguardar DOM estar pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileMenu);
    } else {
        initMobileMenu();
    }

    function initMobileMenu() {
        // Elementos do DOM
        const menuButton = document.getElementById('mobile-menu-button');
        const menuModal = document.getElementById('mobile-menu-modal');
        const menuClose = document.getElementById('mobile-menu-close');
        const navItems = document.querySelectorAll('.mobile-nav-item');
        const menuItems = document.querySelectorAll('.mobile-menu-item');

        // Verificar se estamos em mobile
        function isMobile() {
            return window.innerWidth <= 768;
        }

        // Só inicializar se estiver em mobile
        if (!isMobile()) {
            console.log('[MOBILE MENU] Desktop detected, skipping initialization');
            return;
        }

        if (!menuButton || !menuModal) {
            console.log('[MOBILE MENU] Elements not found, skipping');
            return;
        }

        console.log('[MOBILE MENU] Elements found successfully');

        // Abrir modal do menu
        function openMenu() {
            menuModal.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevenir scroll
            console.log('[MOBILE MENU] Menu opened');
        }

        // Fechar modal do menu
        function closeMenu() {
            menuModal.classList.remove('active');
            document.body.style.overflow = ''; // Restaurar scroll
            console.log('[MOBILE MENU] Menu closed');
        }

        // Highlight do item ativo baseado na URL atual
        function highlightActiveItem() {
            const currentPath = window.location.pathname;

            // Remover active de todos os itens
            navItems.forEach(item => item.classList.remove('active'));
            menuItems.forEach(item => item.classList.remove('active'));

            // Adicionar active ao item correspondente
            navItems.forEach(item => {
                const href = item.getAttribute('href');
                if (href && currentPath.includes(href) && href !== '/') {
                    item.classList.add('active');
                } else if (href === '/' && currentPath === '/') {
                    item.classList.add('active');
                }
            });

            menuItems.forEach(item => {
                const href = item.getAttribute('href');
                if (href && currentPath.includes(href) && href !== '/') {
                    item.classList.add('active');
                } else if (href === '/' && currentPath === '/') {
                    item.classList.add('active');
                }
            });

            console.log('[MOBILE MENU] Active item highlighted for path:', currentPath);
        }

        // Event listeners
        if (menuButton) {
            menuButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                openMenu();
            });
        }

        if (menuClose) {
            menuClose.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                closeMenu();
            });
        }

        // Fechar ao clicar fora do conteúdo
        if (menuModal) {
            menuModal.addEventListener('click', (e) => {
                if (e.target === menuModal) {
                    closeMenu();
                }
            });
        }

        // Fechar ao clicar em um item do menu
        menuItems.forEach(item => {
            item.addEventListener('click', () => {
                closeMenu();
            });
        });

        // Fechar com tecla ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && menuModal.classList.contains('active')) {
                closeMenu();
            }
        });

        // Highlight inicial
        highlightActiveItem();

        // Atualizar highlight quando a URL mudar (para SPAs)
        window.addEventListener('popstate', highlightActiveItem);

        console.log('[MOBILE MENU] Initialized successfully');
    }
})();
