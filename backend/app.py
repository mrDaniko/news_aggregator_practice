import config
from config import STUDENT_ID
import feedparser
from fastapi import FastAPI, HTTPException
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from fastapi.middleware.cors import CORSMiddleware

analyzer = SentimentIntensityAnalyzer()
app = FastAPI()

# Налаштування CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8001", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Тестова база користувачів для /token
fake_users_db = {
    STUDENT_ID: {
        "username": STUDENT_ID,
        "full_name": STUDENT_ID,
        "hashed_password": "password123",  # нерекомендовано зберігати так на проді
        "disabled": False,
    }
}

# Пам'ять для статей
news_store = {STUDENT_ID: []}

@app.post("/fetch/{student_id}")
def fetch_news(student_id: str):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")
    news_store[student_id].clear()
    fetched = 0
    for url in config.SOURCES:
        feed = feedparser.parse(url)
        for entry in getattr(feed, "entries", []):
            news_store[student_id].append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", "")
            })
            fetched += 1
    print(f"Fetched {fetched} articles for student_id: {student_id}")
    return {"fetched": fetched}

@app.get("/news/{student_id}")
def get_news(student_id: str):
    if student_id not in news_store:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"articles": news_store[student_id]}

@app.post("/analyze/{student_id}")
def analyze_tone(student_id: str):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")
    articles = news_store.get(student_id, [])
    result = []
    for art in articles:
        text = art.get("title", "")
        scores = analyzer.polarity_scores(text)
        comp = scores["compound"]
        if comp >= 0.05:
            label = "positive"
        elif comp <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        result.append({**art, "sentiment": label, "scores": scores})
    return {"analyzed": len(result), "articles": result}