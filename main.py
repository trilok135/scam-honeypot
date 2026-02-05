from fastapi import FastAPI, HTTPException, Header, Body, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
import re

app = FastAPI()

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class Request(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Message] = []
    metadata: Optional[Dict] = {}

class Response(BaseModel):
    status: str
    reply: str

sessions = {}
API_KEY = 'secret123'

def verify_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(401, 'Invalid key')

def get_smart_reply(scammer_text: str, turn: int) -> str:
    text_lower = scammer_text.lower()
    
    # PRIORITY 1: Direct response to scammer's request
    if any(word in text_lower for word in ['account', 'ac', 'number']):
        return "Okay sir, my account number is 1234567890123456. What's yours for verification?"
    
    if any(word in text_lower for word in ['otp', 'one time', 'code']):
        return "Got the OTP sir. It's 258391. What should I do next?"
    
    if any(word in text_lower for word in ['gpay', 'phonepe', 'upi', 'payment']):
        return "My GPay ID is deepak.work@oksbi. Please share yours for verification."
    
    if 'link' in text_lower or 'http' in text_lower:
        return "Clicked the link sir. What are the next steps?"
    
    if any(word in text_lower for word in ['blocked', 'locked', 'suspend', 'frozen']):
        return "My account got locked? How do I unlock it sir?"
    
    # PRIORITY 2: Professional fallback sequence
    replies = [
        "Good evening sir. What's the issue with my SBI account?",
        "I'm an SBI Egmore customer. Is there an account problem?",
        "Please share your account details. We can do mutual verification.",
        "Share your payment ID for verification please.",
        "Please send the verification link. I'll check it immediately."
    ]
    
    return replies[turn % 5]

@app.get('/health')
async def health():
    return {'status': 'healthy'}

@app.post('/webhook')
async def webhook(request: Request = Body(...), api_key: str = Depends(verify_key)):
    sid = request.sessionId
    text = request.message.text
    
    if sid not in sessions:
        sessions[sid] = {'turns': 0}
    
    sessions[sid]['turns'] += 1
    reply = get_smart_reply(text, sessions[sid]['turns'])
    
    print(f"Scammer: {text}")
    print(f"Honeypot: {reply}")
    print("---")
    
    return Response(status='success', reply=reply)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
