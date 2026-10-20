import os
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_home_endpoint() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "StudyMate AI is running"


def test_health_endpoint_does_not_return_api_key() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "GROQ_API_KEY" not in response.json()


def test_analyze_rejects_text_that_is_too_short() -> None:
    response = client.post(
        "/analyze",
        json={"text": "Teks terlalu pendek", "prompt_version": "C"},
    )
    assert response.status_code == 422


def test_analyze_rejects_unknown_prompt_version() -> None:
    response = client.post(
        "/analyze",
        json={
            "text": (
                "Machine learning mempelajari pola dari data untuk membantu "
                "komputer membuat prediksi."
            ),
            "prompt_version": "D",
        },
    )
    assert response.status_code == 422


def test_analyze_returns_clear_error_when_api_key_is_missing() -> None:
    with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
        response = client.post(
            "/analyze",
            json={
                "text": (
                    "Machine learning mempelajari pola dari data untuk membantu "
                    "komputer membuat prediksi."
                ),
                "prompt_version": "C",
            },
        )

    assert response.status_code == 503
    assert "GROQ_API_KEY" in response.json()["detail"]
