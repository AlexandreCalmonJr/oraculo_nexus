
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
