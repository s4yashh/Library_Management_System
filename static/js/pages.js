/**
 * Page renderers for LibraryDesk.
 * Each function returns an HTML string and optionally attaches listeners via afterRender().
 */

const Pages = {};

// State held by the current page (filters, selections, etc.)
let pageState = {};

// ---------- Dashboard ----------

Pages.dashboard = {
    title: 'Dashboard',
    breadcrumb: 'Overview',

    async render(container) {
        container.innerHTML = renderLoading('Loading dashboard...');

        const [statsRes, recentRes, overdueRes] = await Promise.all([
            api.dashboard.stats(),
            api.dashboard.recentIssues(),
            api.dashboard.overdue(),
        ]);

        if (!statsRes.success) {
            container.innerHTML = renderError(statsRes.error, () => this.render(container));
            return;
        }

        const s = statsRes.data || {};
        const recent = recentRes.data || [];
        const overdue = overdueRes.data || [];

        container.innerHTML = `
            ${state.demoMode ? `<div class="demo-banner"><i data-lucide="info"></i><span>Demo mode is active. Data is simulated and write operations are not persisted.</span></div>` : ''}
            <div class="quick-actions">
                <button class="btn btn-primary" data-nav="issue"><i data-lucide="plus-circle"></i> Issue Book</button>
                <button class="btn btn-secondary" data-nav="return"><i data-lucide="rotate-ccw"></i> Return Book</button>
                <button class="btn btn-secondary" data-nav="members"><i data-lucide="user-plus"></i> Add Member</button>
                <button class="btn btn-secondary" data-nav="reports"><i data-lucide="file-text"></i> View Reports</button>
            </div>
            <div class="stats-grid">
                ${statCard('book', 'Total Titles', s.total_books || 0, `${s.total_copies || 0} total copies`)}
                ${statCard('copy', 'Available Copies', s.available_copies || 0, 'ready to issue')}
                ${statCard('bookmark', 'Currently Issued', s.issued_transactions || 0, 'active transactions')}
                ${statCard('users', 'Members', s.registered_members || 0, 'registered borrowers')}
                ${statCard('alert-circle', 'Overdue Issues', s.overdue_issues || 0, 'need attention')}
                ${statCard('indian-rupee', 'Unpaid Fines', formatCurrency(s.total_unpaid_fines || 0), `paid: ${formatCurrency(s.total_paid_fines || 0)}`)}
            </div>
            <div class="dashboard-grid">
                <div class="dashboard-column">
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">Recent Transactions</h3>
                            <button class="btn btn-ghost btn-sm" data-nav="issues">View All</button>
                        </div>
                        <div class="card-body no-padding">
                            ${renderTable([
                                { key: 'issue_id', label: 'Issue ID' },
                                { key: 'book_title', label: 'Book' },
                                { key: 'member_name', label: 'Member' },
                                { key: 'issue_date', label: 'Issue Date', format: formatDate },
                                { key: 'status', label: 'Status', format: statusBadge },
                            ], recent, { emptyMessage: 'No recent transactions' })}
                        </div>
                    </div>
                </div>
                <div class="dashboard-column">
                    <div class="card">
                        <div class="card-header">
                            <h3 class="card-title">Overdue Preview</h3>
                            <button class="btn btn-ghost btn-sm" data-nav="issues" data-filter-overdue="true">View All</button>
                        </div>
                        <div class="card-body no-padding">
                            ${renderTable([
                                { key: 'issue_id', label: 'Issue' },
                                { key: 'member_name', label: 'Member' },
                                { key: 'book_title', label: 'Book' },
                                { key: 'due_date', label: 'Due', format: formatDate },
                            ], overdue, { emptyMessage: 'No overdue books' })}
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    afterRender() {
        document.querySelectorAll('[data-nav]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const page = btn.dataset.nav;
                const overdue = btn.dataset.filterOverdue === 'true';
                if (overdue) pageState.issuesOverdue = true;
                navigateTo(page);
            });
        });
    },
};

function statCard(icon, label, value, sublabel) {
    return `
        <div class="stat-card">
            <div class="stat-icon"><i data-lucide="${icon}"></i></div>
            <div class="stat-content">
                <div class="stat-label">${escapeHtml(label)}</div>
                <div class="stat-value">${escapeHtml(String(value))}</div>
                <div class="stat-sublabel">${escapeHtml(sublabel)}</div>
            </div>
        </div>
    `;
}

// ---------- Books ----------

Pages.books = {
    title: 'Books',
    breadcrumb: 'Catalog Management',
    filters: {},

    async render(container) {
        container.innerHTML = renderLoading('Loading books...');
        const [booksRes, categoriesRes, authorsRes] = await Promise.all([
            api.books.list(this.filters),
            api.categories.list(),
            api.authors.list(),
        ]);

        if (!booksRes.success) {
            container.innerHTML = renderError(booksRes.error, () => this.render(container));
            return;
        }

        const books = booksRes.data || [];
        const categories = categoriesRes.data || [];
        const authors = authorsRes.data || [];

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Books Catalog</h3>
                    <button class="btn btn-primary" id="add-book-btn"><i data-lucide="plus"></i> Add Book</button>
                </div>
                <div class="card-body">
                    <div class="toolbar">
                        <div class="search-box">
                            <i data-lucide="search"></i>
                            <input type="text" class="form-input" id="book-search" placeholder="Search by title..." value="${escapeHtml(this.filters.search || '')}">
                        </div>
                        <select class="form-select" id="book-category-filter" style="width: 180px;">
                            <option value="">All Categories</option>
                            ${categories.map((c) => `<option value="${c.category_id}" ${String(this.filters.category_id) === String(c.category_id) ? 'selected' : ''}>${escapeHtml(c.category_name)}</option>`).join('')}
                        </select>
                        <select class="form-select" id="book-availability-filter" style="width: 160px;">
                            <option value="">All Availability</option>
                            <option value="available" ${this.filters.availability === 'available' ? 'selected' : ''}>Available</option>
                            <option value="unavailable" ${this.filters.availability === 'unavailable' ? 'selected' : ''}>Out of Stock</option>
                        </select>
                    </div>
                    ${renderTable([
                        { key: 'book_id', label: 'ID' },
                        { key: 'title', label: 'Title' },
                        { key: 'author_name', label: 'Author' },
                        { key: 'category_name', label: 'Category' },
                        { key: 'price', label: 'Price', format: formatCurrency },
                        { key: 'total_copies', label: 'Total' },
                        { key: 'available_copies', label: 'Available' },
                        { key: 'actions', label: 'Actions', format: (_, row) => `
                            <button class="btn btn-ghost btn-sm edit-book" data-id="${row.book_id}"><i data-lucide="edit-2"></i></button>
                            <button class="btn btn-ghost btn-sm delete-book" data-id="${row.book_id}" ${row.available_copies < row.total_copies ? 'disabled title="Has active issues"' : ''}><i data-lucide="trash-2"></i></button>
                        ` },
                    ], books)}
                </div>
            </div>
        `;

        this._authors = authors;
        this._categories = categories;
    },

    afterRender() {
        const search = document.getElementById('book-search');
        const category = document.getElementById('book-category-filter');
        const availability = document.getElementById('book-availability-filter');

        const applyFilters = debounce(() => {
            this.filters = {
                search: search.value.trim(),
                category_id: category.value,
                availability: availability.value,
            };
            navigateTo('books');
        });

        search.addEventListener('input', applyFilters);
        category.addEventListener('change', applyFilters);
        availability.addEventListener('change', applyFilters);

        document.getElementById('add-book-btn').addEventListener('click', () => this.openForm());

        document.querySelectorAll('.edit-book').forEach((btn) => {
            btn.addEventListener('click', () => this.openForm(Number(btn.dataset.id)));
        });

        document.querySelectorAll('.delete-book').forEach((btn) => {
            btn.addEventListener('click', () => this.deleteBook(Number(btn.dataset.id)));
        });
    },

    openForm(bookId = null) {
        const isEdit = !!bookId;
        const book = isEdit ? pageState.books?.find((b) => b.book_id === bookId) : null;

        const fields = [
            { name: 'title', label: 'Title', type: 'text', required: true, value: book?.title || '' },
            { name: 'author_id', label: 'Author', type: 'select', required: true, value: book?.author_id || '', options: this._authors.map((a) => ({ value: a.author_id, label: a.author_name })) },
            { name: 'category_id', label: 'Category', type: 'select', required: true, value: book?.category_id || '', options: this._categories.map((c) => ({ value: c.category_id, label: c.category_name })) },
            { name: 'price', label: 'Price (INR)', type: 'number', step: '0.01', required: true, value: book?.price || '' },
            { name: 'total_copies', label: 'Total Copies', type: 'number', required: true, value: book?.total_copies || 1, hint: isEdit ? 'Cannot be less than available copies' : '' },
        ];

        Modal.open(isEdit ? 'Edit Book' : 'Add Book', buildForm(fields, isEdit ? 'Update Book' : 'Add Book'));

        document.getElementById('modal-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = getFormData(e.target);
            const payload = {
                title: data.title,
                author_id: Number(data.author_id),
                category_id: Number(data.category_id),
                price: Number(data.price),
                total_copies: Number(data.total_copies),
            };

            const res = isEdit
                ? await api.books.update(bookId, payload)
                : await api.books.create(payload);

            if (res.success) {
                showToast(res.message || 'Book saved', 'success');
                Modal.close();
                navigateTo('books');
            } else {
                showToast(res.error || 'Failed to save book', 'error');
            }
        });
    },

    async deleteBook(bookId) {
        confirmAction('Are you sure you want to delete this book? This cannot be undone.', async () => {
            const res = await api.books.delete(bookId);
            if (res.success) {
                showToast('Book deleted', 'success');
                navigateTo('books');
            } else {
                showToast(res.error || 'Failed to delete book', 'error');
            }
        }, { danger: true, title: 'Delete Book' });
    },
};

// ---------- Members ----------

Pages.members = {
    title: 'Members',
    breadcrumb: 'Borrower Management',
    filters: {},

    async render(container) {
        container.innerHTML = renderLoading('Loading members...');
        const res = await api.members.list(this.filters);
        if (!res.success) {
            container.innerHTML = renderError(res.error, () => this.render(container));
            return;
        }
        const members = res.data || [];
        pageState.members = members;

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Registered Members</h3>
                    <button class="btn btn-primary" id="add-member-btn"><i data-lucide="plus"></i> Register Member</button>
                </div>
                <div class="card-body">
                    <div class="toolbar">
                        <div class="search-box">
                            <i data-lucide="search"></i>
                            <input type="text" class="form-input" id="member-search" placeholder="Search by name, email or ID..." value="${escapeHtml(this.filters.search || '')}">
                        </div>
                    </div>
                    ${renderTable([
                        { key: 'member_id', label: 'ID' },
                        { key: 'name', label: 'Name' },
                        { key: 'email', label: 'Email' },
                        { key: 'phone', label: 'Phone' },
                        { key: 'join_date', label: 'Joined', format: formatDate },
                        { key: 'membership_type', label: 'Type', format: statusBadge },
                        { key: 'actions', label: 'Actions', format: (_, row) => `
                            <button class="btn btn-ghost btn-sm view-member" data-id="${row.member_id}"><i data-lucide="eye"></i></button>
                            <button class="btn btn-ghost btn-sm edit-member" data-id="${row.member_id}"><i data-lucide="edit-2"></i></button>
                            <button class="btn btn-ghost btn-sm delete-member" data-id="${row.member_id}"><i data-lucide="trash-2"></i></button>
                        ` },
                    ], members)}
                </div>
            </div>
        `;
    },

    afterRender() {
        const search = document.getElementById('member-search');
        search.addEventListener('input', debounce(() => {
            this.filters = { search: search.value.trim() };
            navigateTo('members');
        }));

        document.getElementById('add-member-btn').addEventListener('click', () => this.openForm());

        document.querySelectorAll('.edit-member').forEach((btn) => {
            btn.addEventListener('click', () => this.openForm(Number(btn.dataset.id)));
        });

        document.querySelectorAll('.delete-member').forEach((btn) => {
            btn.addEventListener('click', () => this.deleteMember(Number(btn.dataset.id)));
        });

        document.querySelectorAll('.view-member').forEach((btn) => {
            btn.addEventListener('click', () => this.viewMember(Number(btn.dataset.id)));
        });
    },

    openForm(memberId = null) {
        const isEdit = !!memberId;
        const member = isEdit ? pageState.members?.find((m) => m.member_id === memberId) : null;

        const fields = [
            { name: 'name', label: 'Full Name', type: 'text', required: true, value: member?.name || '' },
            { name: 'email', label: 'Email', type: 'email', required: true, value: member?.email || '' },
            { name: 'phone', label: 'Phone', type: 'text', value: member?.phone || '' },
            { name: 'membership_type', label: 'Membership Type', type: 'select', required: true, value: member?.membership_type || 'Student', options: [
                { value: 'Student', label: 'Student' },
                { value: 'Faculty', label: 'Faculty' },
                { value: 'General', label: 'General' },
            ]},
        ];

        Modal.open(isEdit ? 'Edit Member' : 'Register Member', buildForm(fields, isEdit ? 'Update Member' : 'Register Member'));

        document.getElementById('modal-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = getFormData(e.target);
            const payload = {
                name: data.name,
                email: data.email,
                phone: data.phone,
                membership_type: data.membership_type,
            };

            const res = isEdit
                ? await api.members.update(memberId, payload)
                : await api.members.create(payload);

            if (res.success) {
                showToast(res.message || 'Member saved', 'success');
                Modal.close();
                navigateTo('members');
            } else {
                showToast(res.error || 'Failed to save member', 'error');
            }
        });
    },

    async viewMember(memberId) {
        const [memberRes, historyRes] = await Promise.all([
            api.members.get(memberId),
            api.members.history(memberId),
        ]);

        const member = memberRes.data || {};
        const history = historyRes.data || [];

        const content = `
            <div class="form-row">
                <div><strong>Member ID</strong><p>${member.member_id}</p></div>
                <div><strong>Email</strong><p>${escapeHtml(member.email)}</p></div>
                <div><strong>Phone</strong><p>${escapeHtml(member.phone || '—')}</p></div>
                <div><strong>Type</strong><p>${statusBadge(member.membership_type)}</p></div>
            </div>
            <h4 class="card-title" style="margin: 20px 0 12px;">Borrowing History</h4>
            ${renderTable([
                { key: 'issue_id', label: 'Issue ID' },
                { key: 'book_title', label: 'Book' },
                { key: 'issue_date', label: 'Issued', format: formatDate },
                { key: 'due_date', label: 'Due', format: formatDate },
                { key: 'return_date', label: 'Returned', format: formatDate },
                { key: 'status', label: 'Status', format: statusBadge },
            ], history, { emptyMessage: 'No borrowing history' })}
        `;
        Modal.open(`Member: ${escapeHtml(member.name)}`, content);
    },

    async deleteMember(memberId) {
        confirmAction('Delete this member? This cannot be undone if they have no issue records.', async () => {
            const res = await api.members.delete(memberId);
            if (res.success) {
                showToast('Member deleted', 'success');
                navigateTo('members');
            } else {
                showToast(res.error || 'Failed to delete member', 'error');
            }
        }, { danger: true, title: 'Delete Member' });
    },
};

// ---------- Authors ----------

Pages.authors = {
    title: 'Authors',
    breadcrumb: 'Catalog Management',

    async render(container) {
        container.innerHTML = renderLoading('Loading authors...');
        const res = await api.authors.list();
        if (!res.success) {
            container.innerHTML = renderError(res.error, () => this.render(container));
            return;
        }
        const authors = res.data || [];
        pageState.authors = authors;

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Authors</h3>
                    <button class="btn btn-primary" id="add-author-btn"><i data-lucide="plus"></i> Add Author</button>
                </div>
                <div class="card-body no-padding">
                    ${renderTable([
                        { key: 'author_id', label: 'ID' },
                        { key: 'author_name', label: 'Name' },
                        { key: 'country', label: 'Country' },
                        { key: 'book_count', label: 'Books' },
                        { key: 'actions', label: 'Actions', format: (_, row) => `
                            <button class="btn btn-ghost btn-sm edit-author" data-id="${row.author_id}"><i data-lucide="edit-2"></i></button>
                            <button class="btn btn-ghost btn-sm delete-author" data-id="${row.author_id}" ${row.book_count > 0 ? 'disabled title="Has linked books"' : ''}><i data-lucide="trash-2"></i></button>
                        ` },
                    ], authors)}
                </div>
            </div>
        `;
    },

    afterRender() {
        document.getElementById('add-author-btn').addEventListener('click', () => this.openForm());
        document.querySelectorAll('.edit-author').forEach((btn) => {
            btn.addEventListener('click', () => this.openForm(Number(btn.dataset.id)));
        });
        document.querySelectorAll('.delete-author').forEach((btn) => {
            btn.addEventListener('click', () => this.deleteAuthor(Number(btn.dataset.id)));
        });
    },

    openForm(authorId = null) {
        const isEdit = !!authorId;
        const author = isEdit ? pageState.authors?.find((a) => a.author_id === authorId) : null;
        const fields = [
            { name: 'author_name', label: 'Author Name', type: 'text', required: true, value: author?.author_name || '' },
            { name: 'country', label: 'Country', type: 'text', value: author?.country || 'India' },
        ];
        Modal.open(isEdit ? 'Edit Author' : 'Add Author', buildForm(fields, isEdit ? 'Update Author' : 'Add Author'));

        document.getElementById('modal-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = getFormData(e.target);
            const res = isEdit
                ? await api.authors.update(authorId, data)
                : await api.authors.create(data);
            if (res.success) {
                showToast(res.message || 'Author saved', 'success');
                Modal.close();
                navigateTo('authors');
            } else {
                showToast(res.error || 'Failed to save author', 'error');
            }
        });
    },

    async deleteAuthor(authorId) {
        confirmAction('Delete this author?', async () => {
            const res = await api.authors.delete(authorId);
            if (res.success) {
                showToast('Author deleted', 'success');
                navigateTo('authors');
            } else {
                showToast(res.error || 'Failed to delete author', 'error');
            }
        }, { danger: true, title: 'Delete Author' });
    },
};

// ---------- Categories ----------

Pages.categories = {
    title: 'Categories',
    breadcrumb: 'Catalog Management',

    async render(container) {
        container.innerHTML = renderLoading('Loading categories...');
        const res = await api.categories.list();
        if (!res.success) {
            container.innerHTML = renderError(res.error, () => this.render(container));
            return;
        }
        const categories = res.data || [];
        pageState.categories = categories;

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Categories</h3>
                    <button class="btn btn-primary" id="add-category-btn"><i data-lucide="plus"></i> Add Category</button>
                </div>
                <div class="card-body no-padding">
                    ${renderTable([
                        { key: 'category_id', label: 'ID' },
                        { key: 'category_name', label: 'Name' },
                        { key: 'book_count', label: 'Titles' },
                        { key: 'available_copies', label: 'Available Copies' },
                        { key: 'actions', label: 'Actions', format: (_, row) => `
                            <button class="btn btn-ghost btn-sm edit-category" data-id="${row.category_id}"><i data-lucide="edit-2"></i></button>
                            <button class="btn btn-ghost btn-sm delete-category" data-id="${row.category_id}" ${row.book_count > 0 ? 'disabled title="Has linked books"' : ''}><i data-lucide="trash-2"></i></button>
                        ` },
                    ], categories)}
                </div>
            </div>
        `;
    },

    afterRender() {
        document.getElementById('add-category-btn').addEventListener('click', () => this.openForm());
        document.querySelectorAll('.edit-category').forEach((btn) => {
            btn.addEventListener('click', () => this.openForm(Number(btn.dataset.id)));
        });
        document.querySelectorAll('.delete-category').forEach((btn) => {
            btn.addEventListener('click', () => this.deleteCategory(Number(btn.dataset.id)));
        });
    },

    openForm(categoryId = null) {
        const isEdit = !!categoryId;
        const category = isEdit ? pageState.categories?.find((c) => c.category_id === categoryId) : null;
        const fields = [
            { name: 'category_name', label: 'Category Name', type: 'text', required: true, value: category?.category_name || '' },
        ];
        Modal.open(isEdit ? 'Edit Category' : 'Add Category', buildForm(fields, isEdit ? 'Update Category' : 'Add Category'));

        document.getElementById('modal-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = getFormData(e.target);
            const res = isEdit
                ? await api.categories.update(categoryId, data)
                : await api.categories.create(data);
            if (res.success) {
                showToast(res.message || 'Category saved', 'success');
                Modal.close();
                navigateTo('categories');
            } else {
                showToast(res.error || 'Failed to save category', 'error');
            }
        });
    },

    async deleteCategory(categoryId) {
        confirmAction('Delete this category?', async () => {
            const res = await api.categories.delete(categoryId);
            if (res.success) {
                showToast('Category deleted', 'success');
                navigateTo('categories');
            } else {
                showToast(res.error || 'Failed to delete category', 'error');
            }
        }, { danger: true, title: 'Delete Category' });
    },
};

// ---------- Issue Book ----------

Pages.issue = {
    title: 'Issue Book',
    breadcrumb: 'New Borrowing Transaction',

    async render(container) {
        container.innerHTML = renderLoading('Loading options...');
        const [membersRes, booksRes, staffRes] = await Promise.all([
            api.members.list(),
            api.books.list({ availability: 'available' }),
            api.staff.list(),
        ]);

        if (!membersRes.success || !booksRes.success || !staffRes.success) {
            container.innerHTML = renderError(
                membersRes.error || booksRes.error || staffRes.error,
                () => this.render(container)
            );
            return;
        }

        const members = membersRes.data || [];
        const books = booksRes.data || [];
        const staff = staffRes.data || [];

        pageState.issueBooks = books;

        const dueDate = new Date();
        dueDate.setDate(dueDate.getDate() + 14);
        const dueDefault = dueDate.toISOString().split('T')[0];

        container.innerHTML = `
            <div class="card" style="max-width: 640px;">
                <div class="card-header">
                    <h3 class="card-title">Issue a Book</h3>
                </div>
                <div class="card-body">
                    <form id="issue-form">
                        <div class="form-group">
                            <label class="form-label" for="issue-member">Member *</label>
                            <select class="form-select" id="issue-member" name="member_id" required>
                                <option value="">Select member</option>
                                ${members.map((m) => `<option value="${m.member_id}">${escapeHtml(m.name)} (${escapeHtml(m.email)})</option>`).join('')}
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="issue-book">Book *</label>
                            <select class="form-select" id="issue-book" name="book_id" required>
                                <option value="">Select book</option>
                                ${books.map((b) => `<option value="${b.book_id}" data-available="${b.available_copies}">${escapeHtml(b.title)} by ${escapeHtml(b.author_name)} — ${b.available_copies} available</option>`).join('')}
                            </select>
                            <div class="form-hint" id="book-availability-hint">Select a book to see availability</div>
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="issue-staff">Staff Member *</label>
                            <select class="form-select" id="issue-staff" name="staff_id" required>
                                <option value="">Select staff</option>
                                ${staff.map((s) => `<option value="${s.staff_id}">${escapeHtml(s.name)} — ${escapeHtml(s.role)}</option>`).join('')}
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="issue-due-date">Due Date *</label>
                            <input type="date" class="form-input" id="issue-due-date" name="due_date" required value="${dueDefault}">
                        </div>
                        <div class="modal-footer" style="padding: 16px 0 0 0; border-top: 1px solid var(--color-border-light);">
                            <button type="button" class="btn btn-secondary" data-nav="issues">Cancel</button>
                            <button type="submit" class="btn btn-primary" id="issue-submit-btn"><i data-lucide="book-plus"></i> Issue Book</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
    },

    afterRender() {
        const bookSelect = document.getElementById('issue-book');
        const hint = document.getElementById('book-availability-hint');
        bookSelect.addEventListener('change', () => {
            const option = bookSelect.options[bookSelect.selectedIndex];
            const available = option?.dataset.available;
            if (available !== undefined) {
                hint.textContent = `${available} copy/copies available for selected book.`;
            } else {
                hint.textContent = 'Select a book to see availability';
            }
        });

        document.querySelectorAll('[data-nav]').forEach((btn) => {
            btn.addEventListener('click', () => navigateTo(btn.dataset.nav));
        });

        document.getElementById('issue-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = getFormData(e.target);
            const submitBtn = document.getElementById('issue-submit-btn');
            submitBtn.disabled = true;

            const selectedBook = pageState.issueBooks?.find((b) => String(b.book_id) === String(data.book_id));
            if (!selectedBook || selectedBook.available_copies <= 0) {
                showToast('Selected book has no available copies', 'error');
                submitBtn.disabled = false;
                return;
            }

            const res = await api.issues.create({
                book_id: Number(data.book_id),
                member_id: Number(data.member_id),
                staff_id: Number(data.staff_id),
                due_date: data.due_date,
            });

            submitBtn.disabled = false;

            if (res.success) {
                showToast(`${res.message} (Issue ID: ${res.data?.issue_id})`, 'success');
                e.target.reset();
                navigateTo('issues');
            } else {
                showToast(res.error || 'Failed to issue book', 'error');
            }
        });
    },
};

// ---------- Issue History ----------

Pages.issues = {
    title: 'Issue History',
    breadcrumb: 'Transactions',
    filters: {},

    async render(container) {
        container.innerHTML = renderLoading('Loading issues...');

        if (pageState.issuesOverdue) {
            this.filters.overdue = 'true';
            pageState.issuesOverdue = false;
        }

        const res = await api.issues.list(this.filters);
        if (!res.success) {
            container.innerHTML = renderError(res.error, () => this.render(container));
            return;
        }
        const issues = res.data || [];

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Issue History</h3>
                    <button class="btn btn-primary" data-nav="issue"><i data-lucide="plus"></i> Issue Book</button>
                </div>
                <div class="card-body">
                    <div class="toolbar">
                        <div class="search-box">
                            <i data-lucide="search"></i>
                            <input type="text" class="form-input" id="issue-search" placeholder="Search by book, member or ID..." value="${escapeHtml(this.filters.search || '')}">
                        </div>
                        <select class="form-select" id="issue-status-filter" style="width: 150px;">
                            <option value="">All Status</option>
                            <option value="Issued" ${this.filters.status === 'Issued' ? 'selected' : ''}>Issued</option>
                            <option value="Returned" ${this.filters.status === 'Returned' ? 'selected' : ''}>Returned</option>
                        </select>
                        <label class="btn btn-secondary btn-sm" style="cursor: pointer;">
                            <input type="checkbox" id="issue-overdue-filter" ${this.filters.overdue === 'true' ? 'checked' : ''} style="margin-right: 6px;">
                            Overdue only
                        </label>
                    </div>
                    ${renderTable([
                        { key: 'issue_id', label: 'ID' },
                        { key: 'book_title', label: 'Book' },
                        { key: 'member_name', label: 'Member' },
                        { key: 'staff_name', label: 'Staff' },
                        { key: 'issue_date', label: 'Issued', format: formatDate },
                        { key: 'due_date', label: 'Due', format: formatDate },
                        { key: 'return_date', label: 'Returned', format: formatDate },
                        { key: 'status', label: 'Status', format: statusBadge },
                    ], issues)}
                </div>
            </div>
        `;
    },

    afterRender() {
        const search = document.getElementById('issue-search');
        const status = document.getElementById('issue-status-filter');
        const overdue = document.getElementById('issue-overdue-filter');

        const apply = () => {
            this.filters = {
                search: search.value.trim(),
                status: status.value,
                overdue: overdue.checked ? 'true' : '',
            };
            navigateTo('issues');
        };

        search.addEventListener('input', debounce(apply));
        status.addEventListener('change', apply);
        overdue.addEventListener('change', apply);

        document.querySelectorAll('[data-nav]').forEach((btn) => {
            btn.addEventListener('click', () => navigateTo(btn.dataset.nav));
        });
    },
};

// ---------- Return Book ----------

Pages.return = {
    title: 'Return Book',
    breadcrumb: 'Process a Return',

    async render(container) {
        container.innerHTML = `
            <div class="card" style="max-width: 640px;">
                <div class="card-header">
                    <h3 class="card-title">Return a Book</h3>
                </div>
                <div class="card-body">
                    <div class="form-group">
                        <label class="form-label" for="return-search">Find Active Issue</label>
                        <div class="search-box">
                            <i data-lucide="search"></i>
                            <input type="text" class="form-input" id="return-search" placeholder="Search by issue ID, member name or book title...">
                        </div>
                    </div>
                    <div id="return-results"></div>
                </div>
            </div>
        `;

        this.loadActiveIssues('');
    },

    async loadActiveIssues(query) {
        const results = document.getElementById('return-results');
        results.innerHTML = renderLoading('Finding active issues...');

        const res = await api.issues.list({ status: 'Issued', search: query });
        if (!res.success) {
            results.innerHTML = renderError(res.error, () => this.loadActiveIssues(query));
            return;
        }

        const issues = res.data || [];
        results.innerHTML = renderTable([
            { key: 'issue_id', label: 'Issue ID' },
            { key: 'book_title', label: 'Book' },
            { key: 'member_name', label: 'Member' },
            { key: 'due_date', label: 'Due', format: formatDate },
            { key: 'actions', label: 'Actions', format: (_, row) => `
                <button class="btn btn-primary btn-sm return-book-btn" data-id="${row.issue_id}"><i data-lucide="rotate-ccw"></i> Return</button>
            ` },
        ], issues, { emptyMessage: 'No active issues found' });

        lucide.createIcons({ nodes: [results] });

        document.querySelectorAll('.return-book-btn').forEach((btn) => {
            btn.addEventListener('click', () => this.returnBook(Number(btn.dataset.id)));
        });
    },

    afterRender() {
        const search = document.getElementById('return-search');
        search.addEventListener('input', debounce(() => {
            this.loadActiveIssues(search.value.trim());
        }));
    },

    async returnBook(issueId) {
        confirmAction(`Return book for Issue ID ${issueId}? A fine will be created automatically if overdue.`, async () => {
            const res = await api.issues.return(issueId);
            if (res.success) {
                const fine = res.data?.fine;
                const msg = fine
                    ? `Book returned. Fine created: ${formatCurrency(fine.amount)}`
                    : 'Book returned successfully with no fine';
                showToast(msg, 'success');
                navigateTo('issues');
            } else {
                showToast(res.error || 'Failed to return book', 'error');
            }
        }, { title: 'Confirm Return' });
    },
};

// ---------- Fines ----------

Pages.fines = {
    title: 'Fine Management',
    breadcrumb: 'Payments',
    filters: {},

    async render(container) {
        container.innerHTML = renderLoading('Loading fines...');
        const [finesRes, summaryRes] = await Promise.all([
            api.fines.list(this.filters),
            api.fines.summary(),
        ]);

        if (!finesRes.success) {
            container.innerHTML = renderError(finesRes.error, () => this.render(container));
            return;
        }

        const fines = finesRes.data || [];
        const summary = summaryRes.data || { Paid: 0, Unpaid: 0 };

        container.innerHTML = `
            <div class="stats-grid">
                ${statCard('wallet', 'Total Paid', formatCurrency(summary.Paid || 0), 'collected')}
                ${statCard('alert-circle', 'Total Unpaid', formatCurrency(summary.Unpaid || 0), 'pending')}
            </div>
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">Fines</h3>
                    <select class="form-select" id="fine-status-filter" style="width: 160px;">
                        <option value="">All Fines</option>
                        <option value="Unpaid" ${this.filters.status === 'Unpaid' ? 'selected' : ''}>Unpaid</option>
                        <option value="Paid" ${this.filters.status === 'Paid' ? 'selected' : ''}>Paid</option>
                    </select>
                </div>
                <div class="card-body no-padding">
                    ${renderTable([
                        { key: 'fine_id', label: 'Fine ID' },
                        { key: 'member_name', label: 'Member' },
                        { key: 'book_title', label: 'Book' },
                        { key: 'amount', label: 'Amount', format: formatCurrency },
                        { key: 'paid_status', label: 'Status', format: statusBadge },
                        { key: 'actions', label: 'Actions', format: (_, row) => `
                            ${row.paid_status === 'Unpaid'
                                ? `<button class="btn btn-primary btn-sm pay-fine-btn" data-id="${row.fine_id}">Mark Paid</button>`
                                : '<span class="text-muted">—</span>'}
                        ` },
                    ], fines)}
                </div>
            </div>
        `;
    },

    afterRender() {
        const status = document.getElementById('fine-status-filter');
        status.addEventListener('change', () => {
            this.filters = { status: status.value };
            navigateTo('fines');
        });

        document.querySelectorAll('.pay-fine-btn').forEach((btn) => {
            btn.addEventListener('click', () => this.payFine(Number(btn.dataset.id)));
        });
    },

    async payFine(fineId) {
        confirmAction('Mark this fine as paid? This only records payment status; no real transaction is processed.', async () => {
            const res = await api.fines.updatePayment(fineId, 'Paid');
            if (res.success) {
                showToast('Fine marked as paid', 'success');
                navigateTo('fines');
            } else {
                showToast(res.error || 'Failed to update fine', 'error');
            }
        }, { title: 'Mark Fine Paid' });
    },
};

// ---------- Reports ----------

Pages.reports = {
    title: 'Reports',
    breadcrumb: 'Database Reports',

    reportDefinitions: [
        { key: 'available-books', name: 'Available Books', icon: 'book' },
        { key: 'books-by-category', name: 'Books by Category', icon: 'layers' },
        { key: 'current-issues', name: 'Current Issues', icon: 'bookmark' },
        { key: 'overdue', name: 'Overdue Issues', icon: 'alert-circle' },
        { key: 'issue-history', name: 'Complete Issue History', icon: 'history' },
        { key: 'borrowing-count', name: 'Borrowing Count per Member', icon: 'users' },
        { key: 'inactive-members', name: 'Inactive Members', icon: 'user-x' },
        { key: 'fine-summary', name: 'Fine Summary', icon: 'pie-chart' },
        { key: 'unpaid-fines', name: 'Unpaid Fines', icon: 'credit-card' },
        { key: 'staff-activity', name: 'Staff Activity', icon: 'briefcase' },
        { key: 'issued-books', name: 'Books with Issued Copies', icon: 'book-open' },
        { key: 'books-authors-categories', name: 'Books, Authors & Categories', icon: 'grid' },
    ],

    async render(container) {
        container.innerHTML = `
            <div class="report-grid">
                ${this.reportDefinitions.map((r) => `
                    <div class="card report-card" data-report="${r.key}">
                        <div class="card-body">
                            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                                <div class="stat-icon"><i data-lucide="${r.icon}"></i></div>
                                <h4 class="card-title mb-0">${escapeHtml(r.name)}</h4>
                            </div>
                            <p class="text-muted mt-0">Click to view report data and export as CSV.</p>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    afterRender() {
        document.querySelectorAll('.report-card').forEach((card) => {
            card.addEventListener('click', () => this.openReport(card.dataset.report));
        });
    },

    async openReport(reportKey) {
        const definition = this.reportDefinitions.find((r) => r.key === reportKey);
        Modal.open(definition.name, renderLoading('Generating report...'));

        const res = await api.reports.get(reportKey);
        if (!res.success) {
            Modal.setContent(renderError(res.error, () => this.openReport(reportKey)));
            return;
        }

        const rows = res.data || [];
        if (rows.length === 0) {
            Modal.setContent(renderEmpty('This report returned no rows'));
            return;
        }

        // Build headers dynamically from first row
        const headers = Object.keys(rows[0]).map((key) => ({
            key,
            label: formatLabel(key),
            format: (value) => {
                if (key.includes('date')) return formatDate(value);
                if (key === 'amount' || key === 'total' || key === 'price' || key.includes('fine')) return formatCurrency(value);
                return value === null || value === undefined ? '—' : escapeHtml(String(value));
            },
        }));

        const content = `
            <div style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                <span class="text-muted">${rows.length} row(s)</span>
                <button class="btn btn-secondary btn-sm" id="export-report-btn"><i data-lucide="download"></i> Export CSV</button>
            </div>
            ${renderTable(headers, rows)}
        `;
        Modal.setContent(content);

        document.getElementById('export-report-btn').addEventListener('click', () => {
            downloadCsv(`${reportKey}.csv`, headers, rows);
        });
    },
};

// ---------- Database Logic ----------

Pages.databaseLogic = {
    title: 'Database Logic',
    breadcrumb: 'PL/SQL Lab Demonstration',

    async render(container) {
        container.innerHTML = renderLoading('Loading database objects...');
        const res = await api.databaseLogic.objects();
        if (!res.success) {
            container.innerHTML = renderError(res.error, () => this.render(container));
            return;
        }

        const objects = res.data || [];

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">PL/SQL Objects</h3>
                    <button class="btn btn-primary" id="run-overdue-demo"><i data-lucide="play"></i> Run Overdue Cursor Demo</button>
                </div>
                <div class="card-body">
                    <div style="display: flex; flex-direction: column; gap: 16px;">
                        ${objects.map((obj) => {
                            const typeClass = obj.type === 'trigger' ? 'trigger' : obj.type === 'function' ? 'function' : obj.type === 'cursor' ? 'cursor' : '';
                            return `
                                <div class="card logic-card ${typeClass}">
                                    <div class="card-body">
                                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                                            <span class="badge badge-secondary">${escapeHtml(obj.type.toUpperCase())}</span>
                                            <h4 class="card-title mb-0">${escapeHtml(obj.name)}</h4>
                                        </div>
                                        <p>${escapeHtml(obj.purpose)}</p>
                                        <p class="text-muted mt-0"><strong>Tables:</strong> ${escapeHtml(obj.tables.join(', ') || 'N/A')}</p>
                                        <p class="text-muted mt-0"><strong>Invoked by:</strong> ${escapeHtml(obj.invoked_by)}</p>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>
            <div class="card" id="overdue-demo-result" style="display: none;">
                <div class="card-header"><h3 class="card-title">Overdue Cursor Output</h3></div>
                <div class="card-body no-padding" id="overdue-demo-body"></div>
            </div>
        `;
    },

    afterRender() {
        document.getElementById('run-overdue-demo').addEventListener('click', async () => {
            const resultCard = document.getElementById('overdue-demo-result');
            const body = document.getElementById('overdue-demo-body');
            resultCard.style.display = 'block';
            body.innerHTML = renderLoading('Running cursor...');

            const res = await api.databaseLogic.overdueDemo();
            if (!res.success) {
                body.innerHTML = renderError(res.error);
                return;
            }

            const rows = res.data || [];
            body.innerHTML = rows.length === 0
                ? renderEmpty('No overdue active issues')
                : renderTable([
                    { key: 'issue_id', label: 'Issue ID' },
                    { key: 'member_name', label: 'Member' },
                    { key: 'book_title', label: 'Book' },
                    { key: 'due_date', label: 'Due Date', format: formatDate },
                ], rows);
        });
    },
};
