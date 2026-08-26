export function initWebSocket() {
    const socket = new SockJS('/ws');
    const stomp = Stomp.over(socket);
    stomp.connect({}, () => {
        stomp.subscribe('/topic/alerts', msg => { const alert = JSON.parse(msg.body); showAlert(alert); });
    });
}
function showAlert(alert) {
    const list = document.getElementById('alert-list');
    const li = document.createElement('li');
    li.className = alert.severity.toLowerCase();
    li.innerHTML = `<strong>${alert.severity}</strong> â€“ ${alert.message}<br><small>${new Date(alert.timestamp).toLocaleString()}</small>`;
    list.prepend(li);
    setTimeout(() => li.remove(), 10000);
}
