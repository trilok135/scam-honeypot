
import pytest
from fastapi.testclient import TestClient
from voice_detection_api import app
import base64

client = TestClient(app)

MOCK_API_KEY = "your-secret-123"
VALID_HEADERS = {"x-api-key": MOCK_API_KEY}
MOCK_AUDIO = base64.b64encode(b"fake_audio_content").decode("utf-8")

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_authentication_success():
    payload = {
        "language": "en",
        "audioFormat": "mp3",
        "audioBase64": MOCK_AUDIO
    }
    response = client.post("/detect-voice", json=payload, headers=VALID_HEADERS)
    assert response.status_code == 200

def test_authentication_failure():
    payload = {
        "language": "en",
        "audioFormat": "mp3",
        "audioBase64": MOCK_AUDIO
    }
    response = client.post("/detect-voice", json=payload, headers={"x-api-key": "wrong-key"})
    assert response.status_code == 401

def test_missing_api_key():
    payload = {
        "language": "en",
        "audioFormat": "mp3",
        "audioBase64": MOCK_AUDIO
    }
    response = client.post("/detect-voice", json=payload)
    assert response.status_code == 422 # FastAPI returns 422 for missing header if not handled manually

def test_invalid_request_format():
    # Missing audioBase64
    payload = {
        "language": "en",
        "audioFormat": "mp3"
    }
    response = client.post("/detect-voice", json=payload, headers=VALID_HEADERS)
    assert response.status_code == 422

def test_response_schema():
    payload = {
        "language": "ta",
        "audioFormat": "wav",
        "audioBase64": MOCK_AUDIO
    }
    response = client.post("/detect-voice", json=payload, headers=VALID_HEADERS)
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "prediction" in data
    assert data["prediction"] in ["AI_GENERATED", "HUMAN"]
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["language"] == "ta"
    assert "metadata" in data

def test_multi_language_support():
    for lang in ["en", "ta", "hi", "te"]:
        payload = {
            "language": lang,
            "audioFormat": "mp3",
            "audioBase64": MOCK_AUDIO
        }
        response = client.post("/detect-voice", json=payload, headers=VALID_HEADERS)
        assert response.status_code == 200
        assert response.json()["language"] == lang
