const metricsUrl = '/api/metrics';
const chatUrl = '/api/chat';
const resetChatUrl = '/api/chat/reset';

const state = {
    cpuData: [],
    memoryData: [],
    networkSentData: [],
    networkRecvData: [],
    labels: [],
};

let cpuChart;
let memoryChart;
let networkChart;

function formatPercent(value, fraction = 1) {
    return `${value.toFixed(fraction)}%`;
}

function formatMbps(value) {
    return `${value.toFixed(3)} Mb/s`;
}

function addDataPoint(chart, label, value) {
    chart.data.labels.push(label);
    chart.data.datasets[0].data.push(value);
    if (chart.data.labels.length > 25) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }
    chart.update('none');
}

async function fetchMetrics() {
    try {
        const response = await fetch(metricsUrl);
        if (!response.ok) throw new Error('Nie udało się pobrać metryk.');
        const data = await response.json();
        updateMetricCards(data);
        updateCharts(data);
    } catch (error) {
        console.error(error);
    }
}

function updateMetricCards(data) {
    document.getElementById('cpu-value').textContent = formatPercent(data.cpu_percent);
    document.getElementById('memory-value').textContent = formatPercent(data.memory_percent);
    document.getElementById('disk-value').textContent = formatPercent(data.disk_percent);
    document.getElementById('net-sent-value').textContent = formatMbps(data.network_sent_mbps);
    document.getElementById('net-recv-value').textContent = formatMbps(data.network_recv_mbps);
    document.getElementById('load-value').textContent = data.load_average.map(v => v.toFixed(2)).join(' / ');
    document.getElementById('timestamp').textContent = `Ostatnia aktualizacja: ${data.readable_timestamp}`;
}

function updateCharts(data) {
    const label = new Date(data.timestamp * 1000).toLocaleTimeString();
    addDataPoint(cpuChart, label, data.cpu_percent);
    addDataPoint(memoryChart, label, data.memory_percent);
    addDataPoint(networkChart, label, data.network_sent_mbps);
    networkChart.data.datasets[1].data.push(data.network_recv_mbps);
    if (networkChart.data.datasets[1].data.length > 25) {
        networkChart.data.datasets[1].data.shift();
    }
    networkChart.update('none');
}

async function loadChatHistory() {
    try {
        const response = await fetch(chatUrl);
        if (!response.ok) throw new Error('Nie udało się pobrać historii czatu.');
        const data = await response.json();
        renderChatHistory(data.messages);
        updateCostTable(data.usage, data.cost, data.cost);
    } catch (error) {
        console.error(error);
    }
}

function renderChatHistory(messages) {
    const container = document.getElementById('chat-window');
    container.innerHTML = '';
    let timestamp = new Date();
    messages.forEach((message, index) => {
        const bubble = document.createElement('div');
        bubble.classList.add('chat-message', message.role);
        bubble.innerHTML = `<div>${message.content.replace(/\n/g, '<br>')}</div>`;
        const timeEl = document.createElement('time');
        timeEl.textContent = timestamp.toLocaleTimeString();
        bubble.appendChild(timeEl);
        container.appendChild(bubble);
        if (index % 2 === 1) {
            timestamp = new Date();
        }
    });
    container.scrollTop = container.scrollHeight;
}

function updateCostTable(usage, cost, totalCost) {
    const body = document.getElementById('cost-table-body');
    const rows = body.querySelectorAll('tr');
    const promptTokens = usage.prompt_tokens || 0;
    const completionTokens = usage.completion_tokens || 0;

    rows[0].children[1].textContent = promptTokens;
    rows[0].children[2].textContent = cost.prompt.toFixed(6);
    rows[1].children[1].textContent = completionTokens;
    rows[1].children[2].textContent = cost.completion.toFixed(6);
    rows[2].children[1].textContent = promptTokens + completionTokens;
    rows[2].children[2].textContent = totalCost.total.toFixed(6);
    document.getElementById('total-cost').textContent = `Łączny koszt: ${totalCost.total.toFixed(6)} ${totalCost.currency}`;
}

async function sendMessage(message) {
    const response = await fetch(chatUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Błąd wysyłania wiadomości.');
    }
    return response.json();
}

function appendNewMessages(messages) {
    const container = document.getElementById('chat-window');
    messages.forEach(({ role, content }) => {
        const bubble = document.createElement('div');
        bubble.classList.add('chat-message', role);
        bubble.innerHTML = `<div>${content.replace(/\n/g, '<br>')}</div>`;
        const timeEl = document.createElement('time');
        timeEl.textContent = new Date().toLocaleTimeString();
        bubble.appendChild(timeEl);
        container.appendChild(bubble);
    });
    container.scrollTop = container.scrollHeight;
}

async function handleChatSubmit(event) {
    event.preventDefault();
    const textarea = document.getElementById('chat-input');
    const message = textarea.value.trim();
    if (!message) {
        return;
    }
    textarea.value = '';
    try {
        const result = await sendMessage(message);
        appendNewMessages(result.messages);
        updateCostTable(result.total_usage, result.cost, result.total_cost);
    } catch (error) {
        alert(error.message);
    }
}

async function resetChat() {
    const response = await fetch(resetChatUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    });
    if (response.ok) {
        await loadChatHistory();
    }
}

function createChart(ctx, label, color, stacked = false) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label,
                    borderColor: color,
                    backgroundColor: color,
                    fill: false,
                    tension: 0.3,
                    data: [],
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(148, 163, 184, 0.1)' },
                },
                y: {
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(148, 163, 184, 0.1)' },
                },
            },
            plugins: {
                legend: {
                    labels: { color: '#e2e8f0' },
                },
            },
        },
    });
}

function createNetworkChart(ctx) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Wysyłanie',
                    borderColor: '#22d3ee',
                    backgroundColor: '#22d3ee',
                    fill: false,
                    tension: 0.3,
                    data: [],
                },
                {
                    label: 'Pobieranie',
                    borderColor: '#a855f7',
                    backgroundColor: '#a855f7',
                    fill: false,
                    tension: 0.3,
                    data: [],
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(148, 163, 184, 0.1)' },
                },
                y: {
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(148, 163, 184, 0.1)' },
                },
            },
            plugins: {
                legend: {
                    labels: { color: '#e2e8f0' },
                },
            },
        },
    });
}

function initCharts() {
    const cpuCtx = document.getElementById('cpu-chart').getContext('2d');
    const memoryCtx = document.getElementById('memory-chart').getContext('2d');
    const networkCtx = document.getElementById('network-chart').getContext('2d');
    cpuChart = createChart(cpuCtx, 'CPU %', '#38bdf8');
    memoryChart = createChart(memoryCtx, 'Pamięć %', '#f97316');
    networkChart = createNetworkChart(networkCtx);
}

function initEventListeners() {
    document.getElementById('chat-form').addEventListener('submit', handleChatSubmit);
    document.getElementById('reset-chat').addEventListener('click', resetChat);
}

function startMetricPolling() {
    fetchMetrics();
    setInterval(fetchMetrics, window.dashboardConfig.refreshSeconds * 1000);
}

document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    initEventListeners();
    startMetricPolling();
    loadChatHistory();
});
