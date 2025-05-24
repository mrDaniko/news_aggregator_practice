console.log('main.js loaded');

async function loadData() {
    console.log('loadData called');
    try {
        const tokenResponse = await fetch('http://127.0.0.1:8000/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'username=Shakhvaladov_ba40560e&password=password123'
        });
        if (!tokenResponse.ok) {
            throw new Error(`Failed to get token: ${tokenResponse.status}`);
        }
        const tokenData = await tokenResponse.json();
        const token = tokenData.access_token;
        console.log('Token:', token);

        const fetchResponse = await fetch('http://127.0.0.1:8000/fetch/Shakhvaladov_ba40560e', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!fetchResponse.ok) {
            throw new Error(`Failed to fetch news: ${fetchResponse.status}`);
        }
        const fetchData = await fetchResponse.json();
        console.log(`Fetched ${fetchData.fetched} articles`);

        const analyzeResponse = await fetch('http://127.0.0.1:8000/analyze/Shakhvaladov_ba40560e', {
            method: 'POST'
        });
        if (!analyzeResponse.ok) {
            throw new Error(`Failed to analyze: ${analyzeResponse.status}`);
        }
        const analyzeData = await analyzeResponse.json();
        updateTable(analyzeData.articles);
        updateChart(analyzeData.articles);
    } catch (error) {
        console.error('Помилка під час завантаження даних:', error);
    }
}

function updateTable(articles) {
    console.log('Updating table with', articles.length, 'articles');
    const table = document.getElementById('news-table').getElementsByTagName('tbody')[0];
    table.innerHTML = '';
    articles.forEach(article => {
        const row = table.insertRow();
        row.insertCell(0).textContent = article.title;
        const linkCell = row.insertCell(1);
        const link = document.createElement('a');
        link.href = article.link;
        link.textContent = article.link;
        link.target = '_blank';
        linkCell.appendChild(link);
        row.insertCell(2).textContent = article.published;
        row.insertCell(3).textContent = article.sentiment || 'N/A';
    });
}

function updateChart(articles) {
    console.log('Updating chart');
    const ctx = document.getElementById('sentiment-chart').getContext('2d');
    const sentiments = { positive: 0, neutral: 0, negative: 0 };
    articles.forEach(article => {
        if (article.sentiment) sentiments[article.sentiment]++;
    });
    if (window.sentimentChart) window.sentimentChart.destroy();
    window.sentimentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                label: 'Sentiment Distribution',
                data: [sentiments.positive, sentiments.neutral, sentiments.neutral],
                backgroundColor: ['#4caf50', '#ffeb3b', '#f44336']
            }]
        }
    });
}

window.addEventListener('load', () => {
    console.log('Window loaded, starting loadData');
    loadData();
});