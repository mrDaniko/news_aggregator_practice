from fastapi.testclient import TestClient
from backend.app import app, sources_store

client = TestClient(app)

STUDENT_ID = "Shakhvaladov_ba40560e"

def get_token():
    response = client.post(
        "/token",
        data={"username": STUDENT_ID, "password": "password123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.json()["access_token"]

def test_get_empty_sources():
    sources_store.clear()
    res = client.get(f"/sources/{STUDENT_ID}")
    assert res.status_code == 200
    assert res.json() == {"sources": []}

def test_add_and_get_source():
    sources_store.clear()
    token = get_token()
    res1 = client.post(
        f"/sources/{STUDENT_ID}",
        json={"url": "https://example.com/rss"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res1.status_code == 200
    res2 = client.get(f"/sources/{STUDENT_ID}")
    assert res2.status_code == 200
    assert res2.json() == {"sources": ["https://example.com/rss"]}