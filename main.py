from fastapi import FastAPI, HTTPException, Header, Body, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
import re
import random

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

def get_risk_manager_reply(scammer_text: str, turn: int) -> str:
    text_lower = scammer_text.lower()
    
    # HIGH RISK - EVASIVE RESPONSES (Never shares details)
    if any(word in text_lower for word in ['account', 'ac', 'number']):
        return random.choice([
            "I don't share account details over SMS. Please call SBI customer care.",
            "Bank never asks for account numbers via SMS as per RBI guidelines.",
            "This seems like a phishing attempt. I'll report to cybercrime portal."
        ])
    
    if any(word in text_lower for word in ['otp', 'one time', 'code']):
        return random.choice([
            "SBI never asks for OTP via SMS. This violates RBI security policy.",
            "Never share OTP with anyone. Forwarding this to SBI fraud team.",
            "RBI mandated - OTPs are never requested through unsolicited messages."
        ])
    
    if any(word in text_lower for word in ['gpay', 'upi', 'phonepe']):
        return random.choice([
            "Legitimate banks don't ask for UPI IDs via SMS. Please verify.",
            "NPCI guidelines prohibit UPI sharing through unknown numbers.",
            "This UPI request looks suspicious. Checking with SBI branch."
        ])
    
    if 'link' in text_lower or 'http' in text_lower:
        return random.choice([
            "I never click unknown links. Please provide official SBI link.",
            "Phishing links detected. Reporting to CERT-In immediately.",
            "SBI verification never uses third-party links per policy."
        ])
    
    # RISK MANAGER FALLBACK - Always suspicious
    risk_replies = [
        "This message format doesn't match SBI official communication.",
        "SBI customer care number is 1800-11-2211. Why this number?",
        "Urgent account issues are handled through official SBI app only.",
        "Multiple red flags detected. Escalating to SBI security team.",
        "RBI banned such communication methods. Please identify yourself."
    ]
    
    return random.choice(risk_replies)

@app.get('/health')
async def health():
    return {'status': 'healthy'}

@app.post('/webhook')
async def webhook(request: Request = Body(...), api_key: str = Depends(verify_key)):
    sid = request.sessionId
    text = request.message.text
    
    if sid not in sessions:
        sessions[sid] = {'turns': 0, 'risk_score': 0}
    
    sessions[sid]['turns'] += 1
    sessions[sid]['risk_score'] += 1  # Every message increases suspicion
    
    reply = get_risk_manager_reply(text, sessions[sid]['turns'])
    
    print(f"Scammer: {text}")
    print(f"Risk Manager: {reply}")
    print(f"Risk Score: {sessions[sid]['risk_score']}")
    print("---")
    
    return Response(status='success', reply=reply)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
