"""
Runs against the mock inference path (no trained model required), so these
pass in CI before any model has been trained. Once a real checkpoint exists,
set ALLOW_MOCK=false to test against the real path instead.
"""
import io
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("ALLOW_MOCK", "true")
os.environ.setdefault("TREATMENTS_PATH", str(
    __import__("pathlib").Path(__file__).resolve().parents[2] / "data" / "treatments.json"
))

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


@pytest.fixture(scope="module")
def client():
    # Using TestClient as a context manager triggers FastAPI's startup event
    # (which creates the DB tables) — without it, init_db() never runs.
    with TestClient(app) as c:
        yield c


def _sample_image_bytes() -> bytes:
    img = Image.new("RGB", (224, 224), color=(60, 120, 60))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["mock_mode"] is True


def test_diagnose_rejects_non_image(client):
    response = client.post(
        "/api/diagnose",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_diagnose_returns_full_contract(client):
    response = client.post(
        "/api/diagnose",
        files={"file": ("leaf.jpg", _sample_image_bytes(), "image/jpeg")},
    )
    assert response.status_code == 200
    body = response.json()

    assert "disease" in body
    assert 0.0 <= body["confidence"] <= 1.0
    assert len(body["heatmap_base64"]) > 0
    assert set(body["treatment"].keys()) == {"organic", "chemical", "prevention"}


def test_diagnose_is_logged_to_history(client):
    client.post(
        "/api/diagnose",
        files={"file": ("leaf.jpg", _sample_image_bytes(), "image/jpeg")},
    )
    response = client.get("/api/history?limit=5")
    assert response.status_code == 200
    history = response.json()
    assert len(history) >= 1
    assert "disease" in history[0]
