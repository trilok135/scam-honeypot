
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from honeypot_crew import webhook_handler

app = FastAPI(title="Scam Honeypot API")

class MessageObject(BaseModel):
    sender: str
    text: str
    timestamp: int

class WebhookRequest(BaseModel):
    sessionId: str
    message: MessageObject
    conversationHistory: Optional[List[Dict]] = []
    metadata: Optional[Dict] = {}

@app.post("/webhook")
async def webhook(
    request: WebhookRequest,
    x_api_key: str = Header(None)
):
    """
    Webhook endpoint for scam detection
    Authentication: x-api-key header
    """
    
    # Validate API key
    if x_api_key != "YOUR_SECRET":
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Process through honeypot crew
    result = webhook_handler(request.dict())
    
    return result

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "honeypot"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
