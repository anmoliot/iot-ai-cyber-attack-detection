import { API } from './api.js';
import { renderCharts } from './charts.js';
import { initWebSocket } from './websocket.js';
(async function init() { await renderCharts(); initWebSocket(); loadCards(); loadAttackTable(); })();
async function loadCards() { const stats = await API.getStatistics(); document.querySelectorAll('.stat-card .stat-value').forEach(el => { const key = el.dataset.key; if (stats[key] !== undefined) { el.textContent = stats[key]; } }); }
let currentPage = 0;
async function loadAttackTable(page = 0) {
    const data = await API.getRecentAttacks(page, 10);
    const tbody = document.getElementById('attack-table-body');
    tbody.innerHTML = '';
    data.content.forEach(a => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${new Date(a.timestamp).toLocaleString()}</td><td>${a.srcIp}</td><td>${a.dstIp}</td><td>${a.protocol}</td><td>${a.attackType}</td><td>${a.severity}</td><td>${(a.confidence*100).toFixed(1)}%</td><td>${a.action}</td><td>${a.status}</td>`;
        tbody.appendChild(tr);
    });
    const pagination = document.getElementById('attack-pagination');
    pagination.innerHTML = '';
    const prev = document.createElement('button'); prev.textContent = 'Prev'; prev.disabled = page === 0; prev.onclick = () => loadAttackTable(page-1);
    const next = document.createElement('button'); next.textContent = 'Next'; next.disabled = !data.last; next.onclick = () => loadAttackTable(page+1);
    pagination.append(prev, next);
}
