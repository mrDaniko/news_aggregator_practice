async function fetchNews() {
    try {
        // Крок 1: Отримання токена
        const tokenResponse = await fetch('http://127.0.0.1:8000/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'username=Shakhvaladov_ba40560e&password=password123'
        });
        if (!tokenResponse.ok) {
            throw new Error('Failed to get token');
        }
        const tokenData = await tokenResponse.json();
        const token = tokenData.access_token;

        // Крок 2: Запит до /fetch із токеном
        const response = await fetch('http://127.0.0.1:8000/fetch/Shakhvaladov_ba40560e', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (!response.ok) {
            throw new Error('Failed to fetch news');
        }
        const data = await response.json();
        console.log(`Fetched ${data.fetched} articles`);

        // Крок 3: Отримання новин
        const newsResponse = await fetch('http://127.0.0.1:8000/news/Shakhvaladov_ba40560e');
        const newsData = await newsResponse.json();
        updateTable(newsData.articles);

        // Крок 4: Аналіз тональності
        const analyzeResponse = await fetch('http://127.0.0.1:8000/analyze/Shakhvaladov_ba40560e', {
            method: 'POST'
        });
        const analyzeData = await analyzeResponse.json();
        updateChart(analyzeData.articles);
    } catch (error) {
        console.error('Error:', error);
    }
}

function updateTable(articles) {
    const table = document.getElementById('news-table').getElementsByTagName('tbody')[0];
    table.innerHTML = '';
    articles.forEach(article => {
        const row = table.insertRow();
        row.insertCell(0).textContent = article.title;
        row.insertCell(1).textContent = article.published;
        row.insertCell(2).textContent = article.sentiment || 'N/A';
    });
}

function updateChart(articles) {
    const ctx = document.getElementById('sentiment-chart').getContext('2d');
    const sentiments = { positive: 0, neutral: 0, negative: 0 };
    articles.forEach(article => {
        sentiments[article.sentiment]++;
    });
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [{
                label: 'Sentiment Distribution',
                data: [sentiments.positive, sentiments.neutral, sentiments.negative],
                backgroundColor: ['#4caf50', '#ffeb3b', '#f44336']
            }]
        }
    });
}

document.getElementById('fetch-button').addEventListener('click', fetchNews);