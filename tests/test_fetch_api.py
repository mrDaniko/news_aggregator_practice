import pytest
from fastapi.testclient import TestClient
from backend.app import app, news_store
import feedparser

client = TestClient(app)

STUDENT_ID = "Shakhvaladov_ba40560e"

def get_token():
    response = client.post(
        "/token",
        data={"username": STUDENT_ID, "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()["access_token"]

class DummyFeed:
    entries = [
        {
            "title": "Dummy title",
            "link": "<https://example.com>",
            "published": "2025-04-25T12:00:00Z",
        }
    ]

def test_fetch_and_get(monkeypatch):
    token = get_token()
    monkeypatch.setattr("config.SOURCES", ["http://example.com/rss"])
    monkeypatch.setattr(feedparser, "parse", lambda url: DummyFeed)
    news_store[STUDENT_ID] = []
    res1 = client.post(
        f"/fetch/{STUDENT_ID}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res1.status_code == 200
    res2 = client.get(f"/news/{STUDENT_ID}")
    assert res2.status_code == 200
    assert len(res2.json()["articles"]) == 1
    assert res2.json()["articles"][0]["title"] == "Dummy title"