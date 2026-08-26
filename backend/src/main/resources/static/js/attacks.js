import { API } from './api.js';

export async function loadAttackTable(page = 0) {
    const data = await API.getRecentAttacks(page, 10);
    const tbody = document.getElementById('attack-table-body');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    data.content.forEach(a => {
        const tr = document.createElement('tr');
        
        // Map severity to badge colors
        let severityClass = 'info';
        if (a.severity.toUpperCase() === 'CRITICAL') severityClass = 'critical';
        else if (a.severity.toUpperCase() === 'HIGH') severityClass = 'warning'; // Using warning for high
        else if (a.severity.toUpperCase() === 'LOW') severityClass = 'low';

        // Map status to dot colors
        let statusDot = a.status === 'BLOCKED' ? 'status-red' : 'status-green';

        tr.innerHTML = `
            <td>${new Date(a.timestamp).toLocaleString()}</td>
            <td>${a.srcIp}</td>
            <td>${a.dstIp}</td>
            <td><span class="badge badge-info">${a.protocol}</span></td>
            <td><span class="badge badge-warning">${a.attackType}</span></td>
            <td><span class="badge badge-${severityClass}">${a.severity}</span></td>
            <td>${(a.confidence * 100).toFixed(1)}%</td>
            <td>${a.action}</td>
            <td><span class="status-dot ${statusDot}"></span> ${a.status}</td>
        `;
        tbody.appendChild(tr);
    });

    const pagination = document.getElementById('attack-pagination');
    if (pagination) {
        pagination.innerHTML = '';
        const prev = document.createElement('button'); 
        prev.className = 'btn-paginate'; 
        prev.textContent = 'Prev'; 
        prev.disabled = page === 0; 
        prev.onclick = () => loadAttackTable(page - 1);
        
        const next = document.createElement('button'); 
        next.className = 'btn-paginate'; 
        next.textContent = 'Next'; 
        next.disabled = !data.last; 
        next.onclick = () => loadAttackTable(page + 1);
        
        pagination.append(prev, next);
    }
}
