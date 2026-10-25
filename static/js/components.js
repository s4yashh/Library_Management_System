/**
 * Reusable UI components for LibraryDesk.
 */

// Convert snake_case or lowercase keys to readable labels.
function formatLabel(key) {
    return String(key)
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatDate(value) {
    if (!value) return '—';
    const d = new Date(value);
    if (isNaN(d.getTime())) return value;
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

function formatCurrency(value) {
    if (value === null || value === undefined) return '—';
    const num = Number(value);
    if (Number.isNaN(num)) return value;
    return `₹${num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function statusBadge(status) {
    const map = {
        'Issued': 'badge-info',
        'Returned': 'badge-success',
        'Paid': 'badge-success',
        'Unpaid': 'badge-warning',
        'Student': 'badge-secondary',
        'Faculty': 'badge-secondary',
        'General': 'badge-secondary',
    };
    const cls = map[status] || 'badge-secondary';
    return `<span class="badge ${cls}">${escapeHtml(status)}</span>`;
}

function renderTable(headers, rows, options = {}) {
    if (!rows || rows.length === 0) {
        return renderEmpty(options.emptyMessage || 'No records found');
    }

    const headerHtml = headers.map((h) => {
        const label = typeof h === 'string' ? formatLabel(h) : h.label;
        const key = typeof h === 'string' ? h : h.key;
        return `<th data-key="${key}">${escapeHtml(label)}</th>`;
    }).join('');

    const rowsHtml = rows.map((row, idx) => {
        const cells = headers.map((h) => {
            const key = typeof h === 'string' ? h : h.key;
            const formatter = typeof h === 'object' ? h.format : null;
            let value = row[key];
            if (formatter) value = formatter(value, row, idx);
            else value = value === null || value === undefined ? '—' : escapeHtml(String(value));
            return `<td>${value}</td>`;
        }).join('');
        const rowAttrs = options.rowAttrs ? options.rowAttrs(row, idx) : '';
        return `<tr ${rowAttrs}>${cells}</tr>`;
    }).join('');

    return `
        <div class="table-container">
            <table class="data-table">
                <thead><tr>${headerHtml}</tr></thead>
                <tbody>${rowsHtml}</tbody>
            </table>
        </div>
    `;
}

function renderEmpty(message = 'No records found') {
    return `
        <div class="empty-state">
            <i data-lucide="inbox"></i>
            <div class="empty-state-title">Nothing to show</div>
            <p>${escapeHtml(message)}</p>
        </div>
    `;
}

function renderLoading(message = 'Loading...') {
    return `
        <div class="loading">
            <div class="spinner"></div>
            <span>${escapeHtml(message)}</span>
        </div>
    `;
}

let retryButtonId = 0;

function renderError(message, onRetry) {
    const id = `retry-action-${++retryButtonId}`;
    const retryBtn = onRetry
        ? `<button class="btn btn-secondary btn-sm" id="${id}">Retry</button>`
        : '';
    if (onRetry) {
        queueMicrotask(() => document.getElementById(id)?.addEventListener('click', onRetry));
    }
    return `
        <div class="alert alert-error">
            <i data-lucide="alert-circle"></i>
            <div>
                <strong>Error</strong>
                <p class="mt-0">${escapeHtml(message)}</p>
                ${retryBtn}
            </div>
        </div>
    `;
}

function renderFormField(field) {
    const id = `field-${field.name}`;
    const label = `<label class="form-label" for="${id}">${escapeHtml(field.label)}${field.required ? ' <span class="text-muted">*</span>' : ''}</label>`;
    let input = '';

    const attrs = [
        `id="${id}"`,
        `name="${field.name}"`,
        `class="${field.type === 'textarea' ? 'form-textarea' : field.type === 'select' ? 'form-select' : 'form-input'}"`,
        field.required ? 'required' : '',
        field.placeholder ? `placeholder="${escapeHtml(field.placeholder)}"` : '',
        field.value ? `value="${escapeHtml(field.value)}"` : '',
    ].join(' ');

    if (field.type === 'select') {
        const options = field.options.map((opt) => {
            const selected = String(opt.value) === String(field.value) ? 'selected' : '';
            return `<option value="${escapeHtml(String(opt.value))}" ${selected}>${escapeHtml(opt.label)}</option>`;
        }).join('');
        input = `<select ${attrs}>${options}</select>`;
    } else if (field.type === 'textarea') {
        input = `<textarea ${attrs} rows="3">${field.value ? escapeHtml(field.value) : ''}</textarea>`;
    } else {
        input = `<input type="${field.type || 'text'}" ${attrs}>`;
    }

    const hint = field.hint ? `<div class="form-hint">${escapeHtml(field.hint)}</div>` : '';
    return `<div class="form-group">${label}${input}${hint}</div>`;
}

function buildForm(fields, submitLabel = 'Save', options = {}) {
    const fieldsHtml = fields.map(renderFormField).join('');
    const cancelBtn = options.showCancel !== false
        ? `<button type="button" class="btn btn-secondary" data-close-modal>Cancel</button>`
        : '';
    return `
        <form id="${options.id || 'modal-form'}">
            ${fieldsHtml}
            <div class="modal-footer">
                ${cancelBtn}
                <button type="submit" class="btn btn-primary">${escapeHtml(submitLabel)}</button>
            </div>
        </form>
    `;
}

function getFormData(form) {
    const data = {};
    const formData = new FormData(form);
    formData.forEach((value, key) => {
        data[key] = value;
    });
    return data;
}

// Toast notifications
function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i data-lucide="${type === 'success' ? 'check-circle' : type === 'error' ? 'x-circle' : type === 'warning' ? 'alert-triangle' : 'info'}"></i>
        <span>${escapeHtml(message)}</span>
    `;
    container.appendChild(toast);
    lucide.createIcons({ nodes: [toast] });

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        toast.style.transition = 'opacity 0.2s, transform 0.2s';
        setTimeout(() => toast.remove(), 200);
    }, duration);
}

// Modal system
const Modal = {
    overlay: null,
    body: null,
    title: null,

    init() {
        this.overlay = document.getElementById('modal-overlay');
        this.body = document.getElementById('modal-body');
        this.title = document.getElementById('modal-title');

        document.getElementById('modal-close').addEventListener('click', () => this.close());
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) this.close();
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.overlay.hidden) this.close();
        });
    },

    open(title, contentHtml) {
        this.title.textContent = title;
        this.body.innerHTML = contentHtml;
        this.overlay.hidden = false;
        lucide.createIcons({ nodes: [this.body] });

        // Auto-focus first input
        const firstInput = this.body.querySelector('input, select, textarea');
        if (firstInput) firstInput.focus();
    },

    close() {
        this.overlay.hidden = true;
        this.body.innerHTML = '';
    },

    setContent(contentHtml) {
        this.body.innerHTML = contentHtml;
        lucide.createIcons({ nodes: [this.body] });
    },
};

// Confirm dialog
function confirmAction(message, onConfirm, options = {}) {
    const content = `
        <p>${escapeHtml(message)}</p>
        <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-close-modal>Cancel</button>
            <button type="button" id="confirm-btn" class="btn ${options.danger ? 'btn-danger' : 'btn-primary'}">${escapeHtml(options.confirmLabel || 'Confirm')}</button>
        </div>
    `;
    Modal.open(options.title || 'Confirm', content);
    document.getElementById('confirm-btn').addEventListener('click', () => {
        Modal.close();
        onConfirm();
    });
}

// CSV export helper
function downloadCsv(filename, headers, rows) {
    const escapeCsv = (value) => {
        const str = value === null || value === undefined ? '' : String(value);
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
            return `"${str.replace(/"/g, '""')}"`;
        }
        return str;
    };

    const csvRows = [headers.map((h) => escapeCsv(typeof h === 'string' ? formatLabel(h) : h.label))];
    rows.forEach((row) => {
        csvRows.push(headers.map((h) => {
            const key = typeof h === 'string' ? h : h.key;
            const formatter = typeof h === 'object' ? h.format : null;
            let value = row[key];
            if (formatter) value = formatter(value, row);
            else value = value === null || value === undefined ? '' : String(value);
            return escapeCsv(value);
        }));
    });

    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    URL.revokeObjectURL(link.href);
}

// Debounce helper
function debounce(fn, delay = 300) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn(...args), delay);
    };
}

// Export current visible table to CSV
function exportTable(filename, headers, rows) {
    downloadCsv(filename, headers, rows);
}
