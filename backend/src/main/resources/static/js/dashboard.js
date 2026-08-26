import { API } from './api.js';
import { renderCharts } from './charts.js';
import { initWebSocket } from './websocket.js';
import { loadAttackTable } from './attacks.js';
import { loadCards } from './traffic.js';

(async function init() { 
    await renderCharts(); 
    initWebSocket(); 
    loadCards(); 
    loadAttackTable(); 
})();
