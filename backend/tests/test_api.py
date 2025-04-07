import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_sentiment_feed_empty(monkeypatch, client):
    class FakeConn:
        async def fetch(self, *args, **kwargs):
            return []

    class FakePool:
        async def acquire(self):
            class _Ctx:
                async def __aenter__(self):
                    return FakeConn()

                async def __aexit__(self, exc_type, exc, tb):
                    pass

            return _Ctx()

    import backend.main
    backend.main.db_pool = FakePool()

    resp = client.get("/sentiment-feed")
    assert resp.status_code == 200
    assert resp.json() == []
