/**
 * LibraryDesk SPA bootstrap and router.
 */

const state = {
    currentPage: 'dashboard',
    demoMode: false,
    dbConnected: false,
};

const navItems = [
    { page: 'dashboard', label: 'Dashboard', icon: 'layout-dashboard' },
    { page: 'books', label: 'Books', icon: 'book' },
    { page: 'members', label: 'Members', icon: 'users' },
    { page: 'authors', label: 'Authors', icon: 'pen-tool' },
    { page: 'categories', label: 'Categories', icon: 'layers' },
    { section: 'Transactions' },
    { page: 'issue', label: 'Issue Book', icon: 'book-plus' },
    { page: 'return', label: 'Return Book', icon: 'rotate-ccw' },
    { page: 'issues', label: 'Issue History', icon: 'history' },
    { page: 'fines', label: 'Fine Management', icon: 'credit-card' },
    { section: 'Reporting' },
    { page: 'reports', label: 'Reports', icon: 'file-text' },
    { page: 'databaseLogic', label: 'Database Logic', icon: 'database' },
];

function renderSidebar() {
    const nav = document.getElementById('sidebar-nav');
    let html = '';

    navItems.forEach((item) => {
        if (item.section) {
            html += `<div class="nav-section-title">${escapeHtml(item.section)}</div>`;
            return;
        }
        const active = state.currentPage === item.page ? 'active' : '';
        html += `
            <button class="nav-item ${active}" data-page="${item.page}" aria-current="${active ? 'page' : 'false'}">
                <i data-lucide="${item.icon}"></i>
                <span>${escapeHtml(item.label)}</span>
            </button>
        `;
    });

    nav.innerHTML = html;
    lucide.createIcons({ nodes: [nav] });

    nav.querySelectorAll('.nav-item').forEach((btn) => {
        btn.addEventListener('click', () => {
            navigateTo(btn.dataset.page);
            if (window.innerWidth <= 768) {
                document.getElementById('sidebar').classList.remove('open');
            }
        });
    });
}

function updateDbStatus() {
    const statusEl = document.getElementById('db-status');
    const textEl = statusEl.querySelector('.db-status-text');

    statusEl.classList.remove('connected', 'disconnected', 'demo');

    if (state.demoMode) {
        statusEl.classList.add('demo');
        textEl.textContent = 'Demo mode (no database)';
    } else if (state.dbConnected) {
        statusEl.classList.add('connected');
        textEl.textContent = 'Oracle connected';
    } else {
        statusEl.classList.add('disconnected');
        textEl.textContent = 'Oracle not connected';
    }
}

async function checkStatus() {
    const res = await api.status();
    state.dbConnected = res.success && res.data?.connected;
    state.demoMode = res.data?.demo_mode === true;
    updateDbStatus();
}

function navigateTo(page) {
    if (!Pages[page]) return;
    state.currentPage = page;

    // Update URL hash for basic history support
    window.location.hash = page;

    renderSidebar();

    const pageDef = Pages[page];
    document.getElementById('page-title').textContent = pageDef.title || formatLabel(page);
    document.getElementById('page-breadcrumb').textContent = pageDef.breadcrumb || '';

    const content = document.getElementById('content');
    pageDef.render(content).then(() => {
        lucide.createIcons();
        if (pageDef.afterRender) pageDef.afterRender();
    });
}

function handleHash() {
    const hash = window.location.hash.replace('#', '');
    if (Pages[hash]) {
        navigateTo(hash);
    } else {
        navigateTo('dashboard');
    }
}

async function init() {
    Modal.init();

    document.getElementById('menu-toggle').addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('open');
    });

    document.getElementById('refresh-btn').addEventListener('click', () => {
        navigateTo(state.currentPage);
    });

    // Close modal on cancel buttons inside modals
    document.addEventListener('click', (e) => {
        if (e.target.matches('[data-close-modal]')) {
            Modal.close();
        }
    });

    window.addEventListener('hashchange', handleHash);

    await checkStatus();
    handleHash();
}

document.addEventListener('DOMContentLoaded', init);
