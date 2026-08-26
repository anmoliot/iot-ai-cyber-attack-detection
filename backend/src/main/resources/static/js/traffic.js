import { API } from './api.js';

export async function loadCards() { 
    const stats = await API.getStatistics(); 
    document.querySelectorAll('.stat-card .stat-value').forEach(el => { 
        const key = el.dataset.key; 
        if (stats[key] !== undefined) { 
            animateValue(el, 0, stats[key], 1000);
        } 
    }); 
}

function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        // easeOut function for smoother finish
        const easeOut = 1 - Math.pow(1 - progress, 3);
        obj.innerHTML = Math.floor(easeOut * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            obj.innerHTML = end; // Ensure exact final value
        }
    };
    window.requestAnimationFrame(step);
}
