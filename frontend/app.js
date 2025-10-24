const API_BASE_URL = 'http://localhost:8000';
let token = localStorage.getItem('token');

// 登录表单处理
document.getElementById('login').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                username,
                password,
            }),
        });

        if (response.ok) {
            const data = await response.json();
            token = data.access_token;
            localStorage.setItem('token', token);
            showAnalysisContent();
            initWebSocket();
        } else {
            alert('登录失败，请检查用户名和密码');
        }
    } catch (error) {
        console.error('登录错误:', error);
        alert('登录过程中发生错误');
    }
});

function showAnalysisContent() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('analysisContent').style.display = 'block';
    document.getElementById('loginBtn').textContent = '退出';
}

// WebSocket连接
function initWebSocket() {
    const ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);

    ws.onmessage = (event) => {
        const analysis = JSON.parse(event.data);
        displayAnalysis(analysis);
    };

    ws.onclose = () => {
        setTimeout(initWebSocket, 5000); // 断开连接后尝试重连
    };
}

function displayAnalysis(analysis) {
    const newsListElement = document.getElementById('newsList');
    const newsItem = document.createElement('div');
    newsItem.className = `news-item impact-${analysis.impact_level.toLowerCase()}`;

    newsItem.innerHTML = `
        <h6 class="mb-2">${analysis.news_title}</h6>
        <p class="mb-2">${analysis.news_content}</p>
        <div class="affected-sectors">
            <strong>影响板块：</strong> ${analysis.affected_sectors.join(', ')}
        </div>
        <div class="stock-recommendations">
            <strong>推荐股票：</strong>
            ${analysis.recommended_stocks.map(stock => `
                <div class="stock-recommendation">
                    <span class="stock-code">${stock.code}</span>
                    ${stock.name}
                    <span class="stock-action action-${stock.action.toLowerCase()}">${stock.action}</span>
                    <div class="mt-1">${stock.reason}</div>
                </div>
            `).join('')}
        </div>
        <small class="text-muted">分析时间：${analysis.analysis_time}</small>
    `;

    newsListElement.insertBefore(newsItem, newsListElement.firstChild);
}

// 检查是否已登录
if (token) {
    showAnalysisContent();
    initWebSocket();
}