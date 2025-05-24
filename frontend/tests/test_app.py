import pytest
from fastapi.testclient import TestClient
from backend.app import app, news_store, sources_store
import feedparser

client = TestClient(app)

STUDENT_ID = "Shakhvaladov_ba40560e"

def test_fetch_custom_feed(monkeypatch):
    news_store.clear()
    sources_store.clear()

    client.post(f"/sources/{STUDENT_ID}", json={"url": "http://test.com/rss"})

    class DummyFeed:
        entries = [{"title": "X", "link": "L", "published": "2025-04-28"}]

    monkeypatch.setattr(feedparser, "parse", lambda _: DummyFeed)

    r = client.post(f"/fetch/{STUDENT_ID}")
    assert r.json() == {"fetched": 1}