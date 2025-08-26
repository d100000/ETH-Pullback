// 全局变量
let currentData = null;
let updateInterval = null;
let currentPeriod = '1m';
let chart = null;

// API基础URL
const API_BASE = '/api/crypto';

// 初始化应用
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    startDataUpdates();
});

// 初始化应用
function initializeApp() {
    showLoading();
    updateStatus('connecting', '连接中...');
    loadInitialData();
}

// 设置事件监听器
function setupEventListeners() {
    // 时间周期选择器
    document.querySelectorAll('.time-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentPeriod = this.dataset.period;
            loadKlineData();
        });
    });

    // 图表选项复选框
    document.getElementById('showMA').addEventListener('change', updateChart);
    document.getElementById('showFib').addEventListener('change', updateChart);
}

// 加载初始数据
async function loadInitialData() {
    try {
        const response = await fetch(`${API_BASE}/latest`);
        const result = await response.json();
        
        if (result.success) {
            currentData = result.data;
            updateAllDisplays();
            updateStatus('connected', '已连接');
            hideLoading();
        } else {
            throw new Error(result.error || '获取数据失败');
        }
    } catch (error) {
        console.error('加载初始数据失败:', error);
        updateStatus('error', '连接失败');
        showError('无法加载数据: ' + error.message);
        hideLoading();
    }
}

// 加载K线数据
async function loadKlineData() {
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/klines?granularity=${currentPeriod}&limit=100`);
        const result = await response.json();
        
        if (result.success) {
            currentData.klines = result.data;
            updateChart();
            hideLoading();
        } else {
            throw new Error(result.error || '获取K线数据失败');
        }
    } catch (error) {
        console.error('加载K线数据失败:', error);
        showError('无法加载K线数据: ' + error.message);
        hideLoading();
    }
}

// 开始数据更新
function startDataUpdates() {
    // 每秒更新一次数据
    updateInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/latest`);
            const result = await response.json();
            
            if (result.success) {
                const oldPrice = currentData ? currentData.current_price : 0;
                currentData = result.data;
                updatePriceDisplay(oldPrice);
                updateAnalysisDisplays();
                updateChart();
                updateStatus('connected', '实时更新中...');
            }
        } catch (error) {
            console.error('更新数据失败:', error);
            updateStatus('error', '更新失败');
        }
    }, 1000);
}

// 更新所有显示
function updateAllDisplays() {
    if (!currentData) return;
    
    updatePriceDisplay();
    updateAnalysisDisplays();
    updateChart();
    updateLastUpdateTime();
}

// 更新价格显示
function updatePriceDisplay(oldPrice = null) {
    if (!currentData) return;
    
    const currentPrice = currentData.current_price;
    const priceElement = document.getElementById('currentPrice');
    const changeElement = document.getElementById('priceChange');
    
    // 更新价格
    priceElement.textContent = formatPrice(currentPrice);
    
    // 计算价格变化
    if (oldPrice && oldPrice !== currentPrice) {
        const change = currentPrice - oldPrice;
        const changePercent = (change / oldPrice) * 100;
        
        changeElement.innerHTML = `
            <span class="change-value">${change >= 0 ? '+' : ''}${formatPrice(change)}</span>
            <span class="change-percent">${change >= 0 ? '+' : ''}${changePercent.toFixed(2)}%</span>
        `;
        
        changeElement.className = `price-change ${change >= 0 ? 'positive' : 'negative'}`;
        
        // 价格闪烁效果
        priceElement.style.color = change >= 0 ? '#10b981' : '#ef4444';
        setTimeout(() => {
            priceElement.style.color = '#1f2937';
        }, 1000);
    }
}

// 更新分析显示
function updateAnalysisDisplays() {
    if (!currentData || !currentData.analysis) return;
    
    updateMovingAverages();
    updateFibonacciLevels();
    updatePivotPoints();
    updateTrendLines();
    updateSupportResistance();
    updateOptimizedLevels();
}

// 更新移动平均线
function updateMovingAverages() {
    const maData = currentData.analysis.moving_averages;
    const container = document.getElementById('maLevels');
    
    if (!maData) {
        container.innerHTML = '<p class="text-gray-500">暂无数据</p>';
        return;
    }
    
    let html = '';
    Object.entries(maData).forEach(([key, data]) => {
        const distance = Math.abs(data.distance_percent);
        const type = data.support_resistance;
        
        html += `
            <div class="level-item ${type}">
                <span class="level-name">${key}</span>
                <div>
                    <span class="level-value">${formatPrice(data.value)}</span>
                    <span class="level-distance">${distance.toFixed(2)}%</span>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// 更新斐波那契回撤
function updateFibonacciLevels() {
    const fibData = currentData.analysis.fibonacci_retracements;
    const container = document.getElementById('fibLevels');
    
    if (!fibData || !fibData.levels) {
        container.innerHTML = '<p class="text-gray-500">暂无数据</p>';
        return;
    }
    
    let html = '';
    Object.entries(fibData.levels).forEach(([key, data]) => {
        const currentPrice = currentData.current_price;
        const distance = Math.abs((data.price - currentPrice) / currentPrice * 100);
        const type = data.price > currentPrice ? 'resistance' : 'support';
        
        html += `
            <div class="level-item ${type}">
                <span class="level-name">${key}</span>
                <div>
                    <span class="level-value">${formatPrice(data.price)}</span>
                    <span class="level-distance">${distance.toFixed(2)}%</span>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// 更新枢轴点
function updatePivotPoints() {
    const pivotData = currentData.analysis.pivot_points;
    const container = document.getElementById('pivotLevels');
    
    if (!pivotData) {
        container.innerHTML = '<p class="text-gray-500">暂无数据</p>';
        return;
    }
    
    let html = '';
    const currentPrice = currentData.current_price;
    
    // 枢轴点
    if (pivotData.pivot) {
        const distance = Math.abs((pivotData.pivot - currentPrice) / currentPrice * 100);
        html += `
            <div class="level-item">
                <span class="level-name">枢轴点</span>
                <div>
                    <span class="level-value">${formatPrice(pivotData.pivot)}</span>
                    <span class="level-distance">${distance.toFixed(2)}%</span>
                </div>
            </div>
        `;
    }
    
    // 阻力位
    if (pivotData.resistance_levels) {
        Object.entries(pivotData.resistance_levels).forEach(([key, value]) => {
            const distance = Math.abs((value - currentPrice) / currentPrice * 100);
            html += `
                <div class="level-item resistance">
                    <span class="level-name">${key}</span>
                    <div>
                        <span class="level-value">${formatPrice(value)}</span>
                        <span class="level-distance">${distance.toFixed(2)}%</span>
                    </div>
                </div>
            `;
        });
    }
    
    // 支撑位
    if (pivotData.support_levels) {
        Object.entries(pivotData.support_levels).forEach(([key, value]) => {
            const distance = Math.abs((value - currentPrice) / currentPrice * 100);
            html += `
                <div class="level-item support">
                    <span class="level-name">${key}</span>
                    <div>
                        <span class="level-value">${formatPrice(value)}</span>
                        <span class="level-distance">${distance.toFixed(2)}%</span>
                    </div>
                </div>
            `;
        });
    }
    
    container.innerHTML = html || '<p class="text-gray-500">暂无数据</p>';
}

// 更新趋势线
function updateTrendLines() {
    const trendData = currentData.analysis.trend_lines;
    const container = document.getElementById('trendLevels');
    
    if (!trendData) {
        container.innerHTML = '<p class="text-gray-500">暂无数据</p>';
        return;
    }
    
    let html = '';
    
    if (trendData.support_trend && !trendData.support_trend.error) {
        const trend = trendData.support_trend;
        html += `
            <div class="level-item support">
                <span class="level-name">支撑趋势线</span>
                <div>
                    <span class="level-value">${formatPrice(trend.current_price)}</span>
                    <span class="level-distance">${trend.trend_direction}</span>
                </div>
            </div>
        `;
    }
    
    if (trendData.resistance_trend && !trendData.resistance_trend.error) {
        const trend = trendData.resistance_trend;
        html += `
            <div class="level-item resistance">
                <span class="level-name">阻力趋势线</span>
                <div>
                    <span class="level-value">${formatPrice(trend.current_price)}</span>
                    <span class="level-distance">${trend.trend_direction}</span>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html || '<p class="text-gray-500">暂无数据</p>';
}

// 更新支撑阻力位
function updateSupportResistance() {
    const srData = currentData.analysis.support_resistance;
    
    if (!srData) return;
    
    // 更新阻力位
    const resistanceContainer = document.getElementById('resistanceLevels');
    let resistanceHtml = '';
    
    if (srData.resistance_levels && srData.resistance_levels.length > 0) {
        srData.resistance_levels.forEach(level => {
            const currentPrice = currentData.current_price;
            const distance = Math.abs((level.price - currentPrice) / currentPrice * 100);
            
            resistanceHtml += `
                <div class="level-item resistance">
                    <span class="level-name">阻力位 ${level.strength}</span>
                    <div>
                        <span class="level-value">${formatPrice(level.price)}</span>
                        <span class="level-distance">${distance.toFixed(2)}%</span>
                    </div>
                </div>
            `;
        });
    }
    
    resistanceContainer.innerHTML = resistanceHtml || '<p class="text-gray-500">暂无数据</p>';
    
    // 更新支撑位
    const supportContainer = document.getElementById('supportLevels');
    let supportHtml = '';
    
    if (srData.support_levels && srData.support_levels.length > 0) {
        srData.support_levels.forEach(level => {
            const currentPrice = currentData.current_price;
            const distance = Math.abs((level.price - currentPrice) / currentPrice * 100);
            
            supportHtml += `
                <div class="level-item support">
                    <span class="level-name">支撑位 ${level.strength}</span>
                    <div>
                        <span class="level-value">${formatPrice(level.price)}</span>
                        <span class="level-distance">${distance.toFixed(2)}%</span>
                    </div>
                </div>
            `;
        });
    }
    
    supportContainer.innerHTML = supportHtml || '<p class="text-gray-500">暂无数据</p>';
}

// 更新优化价位
function updateOptimizedLevels() {
    const optimizedData = currentData.analysis.optimized_levels;
    
    if (!optimizedData) return;
    
    // 更新心理价位
    const psychContainer = document.getElementById('psychologicalLevels');
    let psychHtml = '';
    
    if (optimizedData.psychological_levels && optimizedData.psychological_levels.length > 0) {
        optimizedData.psychological_levels.forEach(level => {
            psychHtml += `
                <div class="level-item">
                    <span class="level-name">心理价位</span>
                    <div>
                        <span class="level-value">${formatPrice(level.price)}</span>
                        <span class="level-distance">${level.distance_percent.toFixed(2)}%</span>
                    </div>
                </div>
            `;
        });
    }
    
    psychContainer.innerHTML = psychHtml || '<p class="text-gray-500">暂无数据</p>';
    
    // 更新整数价位
    const roundContainer = document.getElementById('roundNumberLevels');
    let roundHtml = '';
    
    if (optimizedData.round_numbers && optimizedData.round_numbers.length > 0) {
        optimizedData.round_numbers.forEach(level => {
            roundHtml += `
                <div class="level-item">
                    <span class="level-name">整数价位</span>
                    <div>
                        <span class="level-value">${formatPrice(level.price)}</span>
                        <span class="level-distance">${level.distance_percent.toFixed(2)}%</span>
                    </div>
                </div>
            `;
        });
    }
    
    roundContainer.innerHTML = roundHtml || '<p class="text-gray-500">暂无数据</p>';
}

// 更新图表
function updateChart() {
    if (!currentData || !currentData.klines) return;
    
    const klines = currentData.klines;
    const showMA = document.getElementById('showMA').checked;
    const showFib = document.getElementById('showFib').checked;
    
    // 准备K线数据
    const dates = klines.map(k => new Date(k[0]));
    const opens = klines.map(k => k[1]);
    const highs = klines.map(k => k[2]);
    const lows = klines.map(k => k[3]);
    const closes = klines.map(k => k[4]);
    
    const traces = [];
    
    // K线图
    traces.push({
        x: dates,
        open: opens,
        high: highs,
        low: lows,
        close: closes,
        type: 'candlestick',
        name: 'ETH/USDT',
        increasing: { line: { color: '#10b981' } },
        decreasing: { line: { color: '#ef4444' } }
    });
    
    // 移动平均线
    if (showMA && currentData.analysis && currentData.analysis.moving_averages) {
        const maData = currentData.analysis.moving_averages;
        Object.entries(maData).forEach(([key, data]) => {
            if (key === 'MA20' || key === 'MA50') {
                traces.push({
                    x: dates,
                    y: new Array(dates.length).fill(data.value),
                    type: 'scatter',
                    mode: 'lines',
                    name: key,
                    line: { 
                        color: key === 'MA20' ? '#667eea' : '#764ba2',
                        width: 2
                    }
                });
            }
        });
    }
    
    // 斐波那契回撤线
    if (showFib && currentData.analysis && currentData.analysis.fibonacci_retracements) {
        const fibData = currentData.analysis.fibonacci_retracements.levels;
        Object.entries(fibData).forEach(([key, data]) => {
            if (key.includes('Fib_')) {
                traces.push({
                    x: [dates[0], dates[dates.length - 1]],
                    y: [data.price, data.price],
                    type: 'scatter',
                    mode: 'lines',
                    name: key,
                    line: { 
                        color: '#fbbf24',
                        width: 1,
                        dash: 'dash'
                    }
                });
            }
        });
    }
    
    const layout = {
        title: {
            text: `ETH/USDT ${currentPeriod} K线图`,
            font: { size: 18, color: '#1f2937' }
        },
        xaxis: {
            title: '时间',
            rangeslider: { visible: false },
            gridcolor: '#f3f4f6'
        },
        yaxis: {
            title: '价格 (USDT)',
            gridcolor: '#f3f4f6'
        },
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
        font: { family: 'Inter, sans-serif' },
        margin: { t: 50, r: 50, b: 50, l: 80 },
        showlegend: true,
        legend: {
            x: 0,
            y: 1,
            bgcolor: 'rgba(255,255,255,0.8)'
        }
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        displaylogo: false
    };
    
    Plotly.newPlot('candlestickChart', traces, layout, config);
}

// 更新状态指示器
function updateStatus(status, text) {
    const dot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    dot.className = `status-dot ${status}`;
    statusText.textContent = text;
}

// 更新最后更新时间
function updateLastUpdateTime() {
    const lastUpdate = document.getElementById('lastUpdate');
    const now = new Date();
    lastUpdate.textContent = `最后更新: ${now.toLocaleTimeString()}`;
}

// 显示加载指示器
function showLoading() {
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

// 隐藏加载指示器
function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

// 显示错误提示
function showError(message) {
    const errorToast = document.getElementById('errorToast');
    const errorMessage = document.getElementById('errorMessage');
    
    errorMessage.textContent = message;
    errorToast.classList.add('show');
    
    // 5秒后自动隐藏
    setTimeout(() => {
        hideError();
    }, 5000);
}

// 隐藏错误提示
function hideError() {
    document.getElementById('errorToast').classList.remove('show');
}

// 格式化价格
function formatPrice(price) {
    if (typeof price !== 'number') return '--';
    return price.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});

