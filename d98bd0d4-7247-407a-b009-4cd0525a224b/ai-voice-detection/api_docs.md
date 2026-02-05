
# API Endpoint Documentation

## POST /detect-voice
Analyze an audio file to determine if it is AI-generated or human.

### Request Headers
- `x-api-key`: Your secret API key (Required)
- `Content-Type`: `application/json`

### Request Body
```json
{
  "language": "en",        // ISO Code: en, ta, hi, te, ml, kn, mr, bn
  "audioFormat": "mp3",    // mp3, wav, m4a
  "audioBase64": "..."     // Base64 encoded audio string
}
```

### Response
```json
{
  "status": "success",
  "prediction": "AI_GENERATED",
  "confidence": 0.98,
  "language": "en",
  "audioFormat": "mp3",
  "processingTime": "0.12s",
  "metadata": {
    "duration": 4.5,
    "sampleRate": 44100,
    "spectralAnomalies": 2,
    "topIndicators": [
      "Unnatural prosody",
      "Spectral flatness anomaly",
      "Pitch consistency"
    ]
  }
}
```

### Error Codes
- **400**: Check audio format or Base64 string.
- **401**: Invalid API Key.
- **422**: Validation Error (missing fields).
- **500**: Internal Server Error.

## GET /health
Check API status.
- **Response**: `{"status": "healthy", ...}`
