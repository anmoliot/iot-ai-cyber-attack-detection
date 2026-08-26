import { appendAlert } from './alerts.js';

export function initWebSocket() {
    const socket = new SockJS('/ws');
    const stomp = Stomp.over(socket);
    stomp.connect({}, () => {
        stomp.subscribe('/topic/alerts', msg => { 
            const alert = JSON.parse(msg.body); 
            appendAlert(alert); 
        });
    });
}
