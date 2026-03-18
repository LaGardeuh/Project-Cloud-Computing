import pytest
from unittest.mock import patch
from app.main import app

# Données fictives pour les tests
MOCK_EVENTS = [{"id": 1, "title": "Conférence IA", "date": "2026-04-15"}]
MOCK_NEWS   = [{"id": 1, "title": "Lancement", "content": "En ligne."}]
MOCK_FAQ    = [{"question": "Comment ?", "answer": "Via /api/"}]

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# --- Health checks ---

def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.get_json()["status"] == "healthy"

def test_readyz(client):
    with patch("app.main.load_blob", return_value=MOCK_EVENTS):
        r = client.get("/readyz")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ready"

# --- Endpoints API ---

def test_events(client):
    with patch("app.main.load_blob", return_value=MOCK_EVENTS):
        r = client.get("/api/events")
    assert r.status_code == 200
    body = r.get_json()
    assert "items" in body
    assert isinstance(body["items"], list)

def test_news(client):
    with patch("app.main.load_blob", return_value=MOCK_NEWS):
        r = client.get("/api/news")
    assert r.status_code == 200
    body = r.get_json()
    assert "items" in body
    assert isinstance(body["items"], list)

def test_faq(client):
    with patch("app.main.load_blob", return_value=MOCK_FAQ):
        r = client.get("/api/faq")
    assert r.status_code == 200
    body = r.get_json()
    assert "items" in body
    assert isinstance(body["items"], list)