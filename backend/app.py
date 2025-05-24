from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import config

app = FastAPI()

# Налаштування CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STUDENT_ID = "Shakhvaladov_ba40560e"
news_store = {STUDENT_ID: []}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Налаштування автентифікації
fake_users_db = {
    "Shakhvaladov_ba40560e": {
        "username": "Shakhvaladov_ba40560e",
        "full_name": "Shakhvaladov_ba40560e",
        "hashed_password": "password123",
        "disabled": False,
    }
}

def verify_password(plain_password, hashed_password):
    return plain_password == hashed_password

def get_user(db, username: str):
    if username in db:
        return db[username]
    return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = get_user(fake_users_db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user["disabled"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

@app.get("/info")
async def get_info():
    return {"student_id": STUDENT_ID}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(fake_users_db, form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user["username"], "token_type": "bearer"}

@app.post("/fetch/{student_id}")
async def fetch_news(student_id: str, current_user: dict = Depends(get_current_user)):
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
async def get_news(student_id: str):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"articles": news_store.get(student_id, [])}

@app.post("/analyze/{student_id}")
async def analyze_news(student_id: str):
    if student_id != STUDENT_ID:
        raise HTTPException(status_code=404, detail="Student not found")
    analyzer = SentimentIntensityAnalyzer()
    articles = news_store.get(student_id, [])
    for article in articles:
        sentiment = analyzer.polarity_scores(article["title"])
        if sentiment["compound"] > 0.05:
            article["sentiment"] = "positive"
        elif sentiment["compound"] < -0.05:
            article["sentiment"] = "negative"
        else:
            article["sentiment"] = "neutral"
    return {"articles": articles}