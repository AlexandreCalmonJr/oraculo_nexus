// Sidebar Toggle Fix
console.log('[SIDEBAR FIX] Loading...');

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');

    if (!sidebar || !sidebarToggle) {
        console.error('[SIDEBAR FIX] Elements not found!', { sidebar, sidebarToggle });
        return;
    }

    console.log('[SIDEBAR FIX] Elements found, adding click handler');

    // Remover listeners antigos clonando o botão
    const newToggle = sidebarToggle.cloneNode(true);
    sidebarToggle.parentNode.replaceChild(newToggle, sidebarToggle);

    // Adicionar novo listener
    newToggle.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();

        console.log('[SIDEBAR FIX] Button clicked!');

        const isMobile = window.innerWidth < 768;

        if (isMobile) {
            sidebar.classList.toggle('mobile-open');
            const overlay = document.getElementById('sidebar-overlay');
            if (overlay) overlay.classList.toggle('active');
        } else {
            sidebar.classList.toggle('collapsed');
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
            console.log('[SIDEBAR FIX] Toggled! Collapsed:', isCollapsed);
        }
    });

    console.log('[SIDEBAR FIX] Click handler added successfully');
});
