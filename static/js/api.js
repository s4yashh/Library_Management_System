/**
 * API client for the LibraryDesk backend.
 * All calls return {success, data, error} objects.
 */
const API_BASE = '';

async function apiRequest(path, options = {}) {
    const url = `${API_BASE}/api${path}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        ...options,
    };

    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }

    try {
        const response = await fetch(url, config);
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            return {
                success: false,
                error: data.error || `HTTP ${response.status}`,
                status: response.status,
            };
        }

        return {
            success: data.success !== false,
            data: data.data,
            message: data.message,
            error: data.error,
        };
    } catch (err) {
        return {
            success: false,
            error: err.message || 'Network error',
            network: true,
        };
    }
}

const api = {
    health: () => apiRequest('/health'),
    status: () => apiRequest('/status'),

    dashboard: {
        stats: () => apiRequest('/dashboard/stats'),
        recentIssues: () => apiRequest('/dashboard/recent-issues'),
        overdue: () => apiRequest('/dashboard/overdue'),
    },

    books: {
        list: (params = {}) => {
            const query = new URLSearchParams(params).toString();
            return apiRequest(`/books?${query}`);
        },
        get: (id) => apiRequest(`/books/${id}`),
        create: (data) => apiRequest('/books', { method: 'POST', body: data }),
        update: (id, data) => apiRequest(`/books/${id}`, { method: 'PUT', body: data }),
        delete: (id) => apiRequest(`/books/${id}`, { method: 'DELETE' }),
    },

    members: {
        list: (params = {}) => {
            const query = new URLSearchParams(params).toString();
            return apiRequest(`/members?${query}`);
        },
        get: (id) => apiRequest(`/members/${id}`),
        create: (data) => apiRequest('/members', { method: 'POST', body: data }),
        update: (id, data) => apiRequest(`/members/${id}`, { method: 'PUT', body: data }),
        delete: (id) => apiRequest(`/members/${id}`, { method: 'DELETE' }),
        history: (id) => apiRequest(`/members/${id}/history`),
    },

    authors: {
        list: () => apiRequest('/authors'),
        create: (data) => apiRequest('/authors', { method: 'POST', body: data }),
        update: (id, data) => apiRequest(`/authors/${id}`, { method: 'PUT', body: data }),
        delete: (id) => apiRequest(`/authors/${id}`, { method: 'DELETE' }),
    },

    categories: {
        list: () => apiRequest('/categories'),
        create: (data) => apiRequest('/categories', { method: 'POST', body: data }),
        update: (id, data) => apiRequest(`/categories/${id}`, { method: 'PUT', body: data }),
        delete: (id) => apiRequest(`/categories/${id}`, { method: 'DELETE' }),
    },

    staff: {
        list: () => apiRequest('/staff'),
    },

    issues: {
        list: (params = {}) => {
            const query = new URLSearchParams(params).toString();
            return apiRequest(`/issues?${query}`);
        },
        get: (id) => apiRequest(`/issues/${id}`),
        create: (data) => apiRequest('/issues', { method: 'POST', body: data }),
        return: (id) => apiRequest(`/issues/${id}/return`, { method: 'POST' }),
    },

    fines: {
        list: (params = {}) => {
            const query = new URLSearchParams(params).toString();
            return apiRequest(`/fines?${query}`);
        },
        summary: () => apiRequest('/fines/summary'),
        updatePayment: (id, status) => apiRequest(`/fines/${id}/payment-status`, {
            method: 'PUT',
            body: { paid_status: status },
        }),
    },

    reports: {
        get: (name) => apiRequest(`/reports/${name}`),
    },

    databaseLogic: {
        objects: () => apiRequest('/database-logic/objects'),
        overdueDemo: () => apiRequest('/database-logic/overdue-demonstration', { method: 'POST' }),
    },
};
