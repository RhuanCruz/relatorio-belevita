// Chart configurations and rendering functions for ApexCharts

// Volume Chart
function renderVolumeChart() {
    const dailyData = dashboardData.metrics.volume.daily;

    const options = {
        series: [
            {
                name: 'Sessões por Dia',
                type: 'column',
                data: dailyData.map(d => d.sessions_count)
            },
            {
                name: 'Média Móvel 7 Dias',
                type: 'line',
                data: dailyData.map(d => Math.round(d.ma_7day))
            }
        ],
        chart: {
            height: 350,
            type: 'line',
            toolbar: {
                show: true
            }
        },
        stroke: {
            width: [0, 3],
            curve: 'smooth'
        },
        plotOptions: {
            bar: {
                columnWidth: '50%'
            }
        },
        fill: {
            opacity: [0.85, 1]
        },
        labels: dailyData.map(d => d.date),
        xaxis: {
            type: 'datetime',
            labels: {
                datetimeFormatter: {
                    month: 'MMM',
                    day: 'dd MMM'
                }
            }
        },
        yaxis: {
            title: {
                text: 'Número de Sessões'
            }
        },
        colors: ['#667eea', '#10b981'],
        tooltip: {
            shared: true,
            intersect: false,
            y: {
                formatter: function (y) {
                    if (typeof y !== "undefined") {
                        return y.toFixed(0) + " sessões";
                    }
                    return y;
                }
            }
        }
    };

    const chart = new ApexCharts(document.querySelector("#volume-chart"), options);
    chart.render();
}

// Response Time Chart
function renderResponseTimeChart() {
    const dailyData = dashboardData.metrics.response_time.daily;

    const options = {
        series: [
            {
                name: 'Tempo Médio (s)',
                data: dailyData.map(d => Math.round(d.median_response_time))
            }
        ],
        chart: {
            height: 350,
            type: 'line',
            toolbar: {
                show: true
            }
        },
        stroke: {
            curve: 'smooth',
            width: 3
        },
        colors: ['#f59e0b'],
        xaxis: {
            categories: dailyData.map(d => d.date),
            type: 'datetime',
            labels: {
                datetimeFormatter: {
                    month: 'MMM',
                    day: 'dd MMM'
                }
            }
        },
        yaxis: {
            title: {
                text: 'Tempo de Resposta (segundos)'
            }
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return val + "s";
                }
            }
        },
        markers: {
            size: 4,
            colors: ['#f59e0b'],
            strokeColors: '#fff',
            strokeWidth: 2,
            hover: {
                size: 7
            }
        }
    };

    const chart = new ApexCharts(document.querySelector("#response-time-chart"), options);
    chart.render();
}

// Resolution Rate Chart
function renderResolutionChart() {
    const weeklyData = dashboardData.metrics.resolution_rate.weekly_trend;

    const options = {
        series: [
            {
                name: 'Taxa de Resolução',
                data: weeklyData.map(d => d.resolution_rate)
            }
        ],
        chart: {
            height: 350,
            type: 'area',
            toolbar: {
                show: true
            }
        },
        stroke: {
            curve: 'smooth',
            width: 2
        },
        fill: {
            type: 'gradient',
            gradient: {
                shadeIntensity: 1,
                opacityFrom: 0.7,
                opacityTo: 0.3
            }
        },
        colors: ['#10b981'],
        xaxis: {
            categories: weeklyData.map(d => d.week),
            labels: {
                rotate: -45
            }
        },
        yaxis: {
            title: {
                text: 'Taxa de Resolução (%)'
            },
            min: 0,
            max: 100
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return val.toFixed(1) + "%";
                }
            }
        },
        dataLabels: {
            enabled: false
        }
    };

    const chart = new ApexCharts(document.querySelector("#resolution-chart"), options);
    chart.render();
}

// Sentiment Donut Chart
function renderSentimentChart() {
    const sentimentData = dashboardData.sentiment;

    const series = [
        sentimentData.distribution.Positivo || 0,
        sentimentData.distribution.Neutro || 0,
        sentimentData.distribution.Negativo || 0
    ];

    const options = {
        series: series,
        chart: {
            type: 'donut',
            height: 350
        },
        labels: ['Positivo', 'Neutro', 'Negativo'],
        colors: ['#10b981', '#94a3b8', '#ef4444'],
        legend: {
            position: 'bottom'
        },
        plotOptions: {
            pie: {
                donut: {
                    size: '65%',
                    labels: {
                        show: true,
                        name: {
                            show: true,
                            fontSize: '18px'
                        },
                        value: {
                            show: true,
                            fontSize: '24px',
                            fontWeight: 600,
                            formatter: function (val) {
                                return parseInt(val);
                            }
                        },
                        total: {
                            show: true,
                            label: 'Total',
                            fontSize: '16px',
                            formatter: function (w) {
                                return w.globals.seriesTotals.reduce((a, b) => a + b, 0);
                            }
                        }
                    }
                }
            }
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    const total = series.reduce((a, b) => a + b, 0);
                    const percentage = ((val / total) * 100).toFixed(1);
                    return `${val} (${percentage}%)`;
                }
            }
        }
    };

    const chart = new ApexCharts(document.querySelector("#sentiment-chart"), options);
    chart.render();
}

// Error Categories Bar Chart
function renderErrorCategoriesChart() {
    const errorCategories = dashboardData.errors.error_categories || {};

    // Convert to array and sort by count
    const categoriesArray = Object.entries(errorCategories)
        .map(([name, count]) => ({
            name: formatCategoryName(name),
            count
        }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10); // Top 10

    const options = {
        series: [{
            name: 'Ocorrências',
            data: categoriesArray.map(c => c.count)
        }],
        chart: {
            type: 'bar',
            height: 350,
            toolbar: {
                show: true
            }
        },
        plotOptions: {
            bar: {
                borderRadius: 4,
                horizontal: true,
                distributed: true
            }
        },
        colors: ['#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16',
                 '#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9'],
        dataLabels: {
            enabled: true
        },
        xaxis: {
            categories: categoriesArray.map(c => c.name),
            title: {
                text: 'Número de Ocorrências'
            }
        },
        yaxis: {
            title: {
                text: 'Categoria de Erro'
            }
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return val + " ocorrências";
                }
            }
        },
        legend: {
            show: false
        }
    };

    const chart = new ApexCharts(document.querySelector("#error-categories-chart"), options);
    chart.render();
}

// Helper function to format category names
function formatCategoryName(name) {
    const nameMap = {
        'short_conversation': 'Conversa Curta',
        'rapid_abandonment': 'Abandono Rápido',
        'stuck_session': 'Sessão Travada',
        'repeated_messages': 'Mensagens Repetidas',
        'failed_session': 'Sessão Falhou',
        'no_sentiment_analysis': 'Sem Análise de Sentimento',
        'phrase_matches': 'Frases de Erro Detectadas'
    };

    return nameMap[name] || name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Helper function to format dates
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: 'short'
    });
}

// Export functions for use in dashboard.js
window.renderVolumeChart = renderVolumeChart;
window.renderResponseTimeChart = renderResponseTimeChart;
window.renderResolutionChart = renderResolutionChart;
window.renderSentimentChart = renderSentimentChart;
window.renderErrorCategoriesChart = renderErrorCategoriesChart;
