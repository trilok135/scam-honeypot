from fastapi import FastAPI, HTTPException, Header, Body, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
import re

app = FastAPI(title="Enterprise Scam Honeypot")

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

def extract_intel(text: str):
    intel = {}
    # UPI extraction
    upi = re.findall(r'[@](\\w+)', text)
    if upi: intel['upi'] = upi
    
    # Account numbers
    ac = re.findall(r'\\b\\d{10,18}\\b', text)
    if ac: intel['accounts'] = ac
    
    # Links
    links = re.findall(r'https?://[^\\s]+', text)
    if links: intel['links'] = links
    
    return intel

@app.get('/health')
async def health():
    return {'status': 'healthy'}

@app.post('/webhook')
async def webhook(request: Request = Body(...), api_key: str = Depends(verify_key)):
    sid = request.sessionId
    text = request.message.text
    
    if sid not in sessions:
        sessions[sid] = {'turns': 0, 'intel': {}}
    
    sessions[sid]['turns'] += 1
    intel = extract_intel(text)
    if intel: sessions[sid]['intel'].update(intel)
    
    # PROFESSIONAL RESPONSES - Government/Business scams
    replies = [
        "Income Tax Department here. Please provide PAN number for verification.",
        "RBI Compliance Officer. Share your registered mobile number for OTP.",
        "UIDAI Aadhaar Helpdesk. Confirm your Aadhaar number ending with XXXX.",
        "EPFO Regional Office. Provide your UAN and last 4 digits of Aadhaar.",
        "IRDAI Insurance Authority. Submit policy number for claim processing.",
        "MCA Corporate Affairs. Company CIN number required for ROC compliance.",
        "PF Commissioner Office. UAN and bank account for PF settlement.",
        "GSTN Portal Admin. GSTIN number needed for input tax credit verification.",
        "SEBI Investor Protection. Demat account number for KYC updation.",
        "NPCI UPI Security. Virtual payment address required for transaction reversal."
    ]
    
    reply_idx = (sessions[sid]['turns'] - 1) % len(replies)
    reply = replies[reply_idx]
    
    print(f"Session {sid}: Turn {sessions[sid]['turns']} - Intel: {intel}")
    
    return Response(status='success', reply=reply)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
