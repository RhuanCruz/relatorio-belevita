// Main Dashboard Logic
let dashboardData = {};
let currentFilters = {
    dateRange: null,
    sentiment: 'all',
    status: 'all'
};

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', async function () {
    console.log('Initializing Belevita ROI Dashboard...');

    try {
        await loadAllData();
        initializeFilters();
        renderDashboard();
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showError('Erro ao carregar dados. Verifique se os arquivos JSON foram gerados.');
    }
});

// Load all JSON data files
async function loadAllData() {
    console.log('Loading data...');

    const dataFiles = [
        '../output/data/summary.json',
        '../output/data/daily_metrics.json',
        '../output/data/sentiment_analysis.json',
        '../output/data/error_analysis.json',
        '../output/data/conversation_samples.json',
        '../output/data/products_analysis.json'
    ];

    const results = await Promise.all(
        dataFiles.map(file => fetch(file).then(r => r.json()).catch(() => null))
    );

    dashboardData = {
        summary: results[0],
        metrics: results[1],
        sentiment: results[2],
        errors: results[3],
        samples: results[4],
        products: results[5]
    };

    console.log('Data loaded successfully:', dashboardData);
}

// Initialize filters
function initializeFilters() {
    // Date range picker
    const dateFilter = flatpickr("#date-filter", {
        mode: "range",
        dateFormat: "Y-m-d",
        locale: "pt",
        onChange: function (selectedDates) {
            currentFilters.dateRange = selectedDates;
            applyFilters();
        }
    });

    // Sentiment filter
    document.getElementById('sentiment-filter').addEventListener('change', function (e) {
        currentFilters.sentiment = e.target.value;
        applyFilters();
    });

    // Status filter
    document.getElementById('status-filter').addEventListener('change', function (e) {
        currentFilters.status = e.target.value;
        applyFilters();
    });

    // Reset filters button
    document.getElementById('reset-filters').addEventListener('click', function () {
        currentFilters = {
            dateRange: null,
            sentiment: 'all',
            status: 'all'
        };
        document.getElementById('sentiment-filter').value = 'all';
        document.getElementById('status-filter').value = 'all';
        dateFilter.clear();
        applyFilters();
    });
}

// Apply filters and re-render
function applyFilters() {
    console.log('Applying filters:', currentFilters);
    renderDashboard();
}

// Main render function
function renderDashboard() {
    updateHeader();
    updateKeyMetrics();
    renderCharts();
    renderErrorSection();
    renderIntentSection();
    renderProductsSection();
    renderDemandsSection();
}

// Update header with date range
function updateHeader() {
    const { date_range } = dashboardData.summary.overview;
    const start = new Date(date_range.start).toLocaleDateString('pt-BR');
    const end = new Date(date_range.end).toLocaleDateString('pt-BR');

    document.getElementById('date-range').textContent = `${start} - ${end}`;
}

// Update key metrics cards
function updateKeyMetrics() {
    const { key_metrics } = dashboardData.summary;

    document.getElementById('total-sessions').textContent =
        key_metrics.total_sessions.toLocaleString('pt-BR');

    document.getElementById('unique-leads').textContent =
        key_metrics.unique_leads.toLocaleString('pt-BR');

    document.getElementById('resolution-rate').textContent =
        `${key_metrics.resolution_rate}%`;

    document.getElementById('positive-sentiment').textContent =
        `${key_metrics.positive_sentiment_rate.toFixed(1)}%`;

    // Trend for sessions
    const avgPerDay = key_metrics.avg_sessions_per_day;
    document.getElementById('sessions-trend').innerHTML =
        `<span class="trend-up">↑ ${avgPerDay} por dia</span>`;
}

// Render all charts
function renderCharts() {
    renderVolumeChart();
    renderResponseTimeChart();
    renderResolutionChart();
    renderSentimentChart();
    renderErrorCategoriesChart();
}

// Render error analysis section
function renderErrorSection() {
    const { error_summary } = dashboardData.summary;

    document.getElementById('high-confidence-errors').textContent =
        error_summary.high_confidence_errors;

    document.getElementById('medium-confidence-errors').textContent =
        error_summary.medium_confidence_errors;

    document.getElementById('error-rate').textContent =
        `${error_summary.error_rate}%`;

    renderErrorConversations();
}

// Render top error conversations
function renderErrorConversations() {
    const container = document.getElementById('error-conversations-list');

    // Get top 20 conversations with highest error scores
    const topErrors = dashboardData.samples
        .filter(s => s.error_confidence >= 40)
        .sort((a, b) => b.error_confidence - a.error_confidence)
        .slice(0, 20);

    container.innerHTML = topErrors.map(conv => `
        <div class="conversation-item" onclick="showConversationModal(${conv.session_id})">
            <div class="conversation-header">
                <div class="conversation-id">Sessão #${conv.session_id}</div>
                <div class="confidence-badge ${conv.error_level}">
                    ${conv.error_confidence.toFixed(1)}% confiança
                </div>
            </div>
            <div class="conversation-meta">
                <span>👤 ${conv.lead.name}</span>
                <span>📅 ${new Date(conv.started_at).toLocaleDateString('pt-BR')}</span>
                <span>😊 ${conv.sentiment || 'N/A'}</span>
                <span>💬 ${conv.messages.length} mensagens</span>
            </div>
        </div>
    `).join('');
}

// Show conversation modal
function showConversationModal(sessionId) {
    const conversation = dashboardData.samples.find(s => s.session_id === sessionId);

    if (!conversation) {
        console.error('Conversation not found:', sessionId);
        return;
    }

    const modal = document.getElementById('conversation-modal');
    const details = document.getElementById('conversation-details');

    const messagesHtml = conversation.messages.map(msg => {
        const msgData = msg.message;
        const type = msgData.type || 'unknown';
        const content = msgData.content || '';

        return `
            <div class="message ${type}">
                <div class="message-header">${type === 'human' ? 'Cliente' : 'IA (Juliana)'}</div>
                <div class="message-content">${content}</div>
            </div>
        `;
    }).join('');

    details.innerHTML = `
        <div style="margin-bottom: 20px;">
            <h3>Sessão #${sessionId}</h3>
            <p><strong>Cliente:</strong> ${conversation.lead.name}</p>
            <p><strong>Data:</strong> ${new Date(conversation.started_at).toLocaleString('pt-BR')}</p>
            <p><strong>Status:</strong> ${conversation.status}</p>
            <p><strong>Sentimento:</strong> ${conversation.sentiment || 'N/A'}</p>
            <p><strong>Score de Erro:</strong> ${conversation.error_confidence.toFixed(1)}% (${conversation.error_level})</p>
        </div>
        <div style="border-top: 2px solid #e5e7eb; padding-top: 20px;">
            <h4 style="margin-bottom: 15px;">Conversa Completa</h4>
            ${messagesHtml}
        </div>
    `;

    modal.style.display = 'block';
}

// Close modal
document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('conversation-modal');
    const closeBtn = document.querySelector('.modal-close');

    closeBtn.onclick = function () {
        modal.style.display = 'none';
    };

    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };
});

// Show error message
function showError(message) {
    document.body.innerHTML = `
        <div style="text-align: center; padding: 50px; color: white;">
            <h1>❌ Erro</h1>
            <p>${message}</p>
            <p style="margin-top: 20px;">
                <a href="javascript:location.reload()" style="color: white; text-decoration: underline;">
                    Recarregar página
                </a>
            </p>
        </div>
    `;
}

// Update generated timestamp
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(() => {
        if (dashboardData.summary) {
            const timestamp = new Date(dashboardData.summary.overview.generated_at).toLocaleString('pt-BR');
            document.getElementById('generated-at').textContent = timestamp;
        }
    }, 1000);
});

// Render intent section
function renderIntentSection() {
    console.log('Rendering intent section...');
    console.log('dashboardData.errors:', dashboardData.errors);

    if (!dashboardData.errors || !dashboardData.errors.intent_distribution) {
        console.log('No intent data available');
        return;
    }

    const intents = dashboardData.errors.intent_distribution;
    console.log('Intent distribution:', intents);

    document.getElementById('intent-rastreio').textContent =
        (intents['Rastreio'] || 0).toLocaleString('pt-BR');
    document.getElementById('intent-troca').textContent =
        (intents['Troca'] || 0).toLocaleString('pt-BR');
    document.getElementById('intent-cancelamento').textContent =
        (intents['Cancelamento'] || 0).toLocaleString('pt-BR');
    document.getElementById('intent-duvida').textContent =
        (intents['Dúvida'] || 0).toLocaleString('pt-BR');

    console.log('Intent section rendered successfully');
}

// Render products section
function renderProductsSection() {
    if (!dashboardData.products) {
        console.log('No products data available');
        return;
    }

    const mentioned = dashboardData.products.produtos_mais_mencionados || {};
    const issues = dashboardData.products.produtos_com_problemas || {};

    // Products mentioned
    const mentionedContainer = document.getElementById('products-mentioned-list');
    mentionedContainer.innerHTML = Object.entries(mentioned)
        .slice(0, 8)
        .map(([name, count]) => `
            <div class="product-item">
                <span class="product-name">${name}</span>
                <span class="product-count">${count.toLocaleString('pt-BR')}</span>
            </div>
        `).join('');

    // Products with issues
    const issuesContainer = document.getElementById('products-issues-list');
    issuesContainer.innerHTML = Object.entries(issues)
        .slice(0, 8)
        .map(([name, count]) => `
            <div class="product-item issue">
                <span class="product-name">${name}</span>
                <span class="product-count">${count.toLocaleString('pt-BR')}</span>
            </div>
        `).join('');
}

// Render demands section
function renderDemandsSection() {
    if (!dashboardData.products) {
        console.log('No demands data available');
        return;
    }

    const demands = dashboardData.products.demandas_nao_atendidas || [];

    document.getElementById('unmet-demands-count').textContent =
        demands.length.toLocaleString('pt-BR');

    const demandsContainer = document.getElementById('unmet-demands-list');
    demandsContainer.innerHTML = demands
        .slice(0, 15)
        .map(demand => `
            <div class="demand-item">
                <span class="demand-context">"${demand.context.substring(0, 150)}${demand.context.length > 150 ? '...' : ''}"</span>
            </div>
        `).join('');
}
