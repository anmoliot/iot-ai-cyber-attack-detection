import { API } from './api.js';
let attackChart, trafficChart, protocolChart, severityChart;
export async function renderCharts() {
    const stats = await API.getStatistics();
    const attackCtx = document.getElementById('attack-distribution-chart').getContext('2d');
    attackChart && attackChart.destroy();
    attackChart = new Chart(attackCtx, { type:'doughnut', data:{ labels:Object.keys(stats.attackDistribution), datasets:[{ data:Object.values(stats.attackDistribution), backgroundColor:['#3b82f6','#06b6d4','#8b5cf6','#10b981','#f97316','#ef4444','#eab308'], borderWidth:0 }]}, options:{ plugins:{ legend:{ position:'right' } } });
    const protoCtx = document.getElementById('protocol-distribution-chart').getContext('2d');
    protocolChart && protocolChart.destroy();
    protocolChart = new Chart(protoCtx, { type:'pie', data:{ labels:Object.keys(stats.protocolDistribution), datasets:[{ data:Object.values(stats.protocolDistribution), backgroundColor:['#3b82f6','#ef4444','#06b6d4'] }] } );
    const sevCtx = document.getElementById('severity-distribution-chart').getContext('2d');
    severityChart && severityChart.destroy();
    severityChart = new Chart(sevCtx, { type:'bar', data:{ labels:Object.keys(stats.severityDistribution), datasets:[{ label:'Attacks', data:Object.values(stats.severityDistribution), backgroundColor:'#f97316' }] } );
    const trafficCtx = document.getElementById('traffic-timeline-chart').getContext('2d');
    trafficChart && trafficChart.destroy();
    trafficChart = new Chart(trafficCtx, { type:'line', data:{ labels:Array.from({length:12},(_,i)=>`Jan ${i+1}`), datasets:[{ label:'Traffic', data:Array.from({length:12},()=>Math.floor(Math.random()*2000)+500), borderColor:'#10b981', fill:false }] } );
}
