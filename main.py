from fastapi import FastAPI, HTTPException, Header, Body, Depends, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict
import base64
import io
import librosa
import numpy as np
import soundfile as sf
import re
from datetime import datetime

app = FastAPI(title="Voice+Text Honeypot")

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class TextRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = []
    metadata: Optional[Dict] = {}

class VoiceRequest(BaseModel):
    sessionId: str
    language: str
    audioFormat: str
    audioBase64: str
    conversationHistory: List[Message] = []

class Response(BaseModel):
    status: str
    reply: str
    prediction: Optional[str] = None
    confidence: Optional[float] = None

sessions = {}
API_KEY = "secret123"

def verify_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(401, "Invalid key")

# NO-TOOL Voice AI Detection (spectral + timing analysis)
def analyze_voice_audio(audio_base64: str, language: str) -> dict:
    try:
        # Decode base64
        audio_data = base64.b64decode(audio_base64)
        audio_bytes = io.BytesIO(audio_data)
        
        # Load with librosa (16kHz mono)
        audio, sr = librosa.load(audio_bytes, sr=16000, mono=True)
        
        # AI Detection Features (no ML models)
        duration = len(audio) / sr
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sr))
        zero_crossing = np.mean(librosa.feature.zero_crossing_rate(audio))
        rms = np.mean(librosa.feature.rms(y=audio))
        
        # AI Voice Signatures
        ai_score = 0.0
        
        # Perfect regularity (AI lacks natural variation)
        if np.std(rms) < 0.01: ai_score += 0.3
        if duration < 1.0 or duration > 60: ai_score += 0.2  # Suspicious length
        
        # Spectral anomalies
        if spectral_centroid < 800 or spectral_centroid > 5000: ai_score += 0.2
        if zero_crossing < 0.05 or zero_crossing > 0.25: ai_score += 0.2
        
        # Language-specific (Tamil/Indian voices higher pitch)
        if language in ["ta", "te", "ml", "hi"]:
            if spectral_centroid > 2500: ai_score += 0.1  # Western AI bias
        
        prediction = "AI_GENERATED" if ai_score > 0.5 else "HUMAN"
        confidence = min(ai_score, 1.0) if prediction == "AI_GENERATED" else 1-ai_score
        
        return {
            "prediction": prediction,
            "confidence": float(confidence),
            "duration": float(duration),
            "spectral_centroid": float(spectral_centroid),
            "features": {"ai_score": float(ai_score)}
        }
    except:
        return {"prediction": "ERROR", "confidence": 0.0}

# Text scam detection (existing logic)
def detect_scam(text: str) -> dict:
    text_lower = text.lower()
    signals = ["upi", "account", "verify", "refund", "police", "rbi"]
    matches = sum(1 for signal in signals if signal in text_lower)
    return {"is_scam": matches > 1, "confidence": matches / 6.0}

@app.get("/health")
async def health():
    return {"status": "healthy", "voice_support": True}

@app.post("/webhook")
async def text_webhook(request: TextRequest = Body(...), api_key: str = Depends(verify_key)):
    sid = request.session
