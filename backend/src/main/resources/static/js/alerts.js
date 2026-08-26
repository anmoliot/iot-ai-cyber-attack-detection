export function appendAlert(alertData) {
    const list = document.getElementById('alert-list');
    if (!list) return;

    const li = document.createElement('li');
    let severityClass = 'info';
    if (alertData.severity) {
        severityClass = alertData.severity.toLowerCase();
    }
    
    li.className = `alert-item ${severityClass} animate-slide-in`;
    li.innerHTML = `
        <div class="alert-time">${new Date(alertData.timestamp || Date.now()).toLocaleTimeString()}</div>
        <div class="alert-content">
            <strong>${alertData.title || alertData.severity}</strong>
            <p>${alertData.description || alertData.message}</p>
        </div>
    `;
    
    list.prepend(li);
    
    // Keep max 20 alerts
    if (list.children.length > 20) {
        list.removeChild(list.lastChild);
    }
}
