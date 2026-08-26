export const API = {
    getStatistics: async () => { const r = await fetch('/api/statistics'); return r.json(); },
    getRecentAttacks: async (page = 0, size = 10) => { const r = await fetch(`/api/attacks?page=${page}&size=${size}`); return r.json(); },
    getRecentAlerts: async () => { const r = await fetch('/api/alerts/unread'); return r.json(); }
};
