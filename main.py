# DELETE broken main.py → Create working honeypot
@"
from fastapi import FastAPI, HTTPException, Header, Body, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict

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

@app.get('/health')
async def health():
    return {'status': 'healthy'}

@app.post('/webhook')
async def webhook(request: Request = Body(...), api_key: str = Depends(verify_key)):
    sid = request.sessionId
    if sid not in sessions:
        sessions[sid] = {'turns': 0}
    
    sessions[sid]['turns'] += 1
    
    replies = [
        'Anna evening la irukenga?',
        'SBI Egmore account issue aa?',
        'AC 1234567890123456 enna sir?',
        'GPay ID share pannunga',
        'Link forward pannunga check pannuren'
    ]
    
    reply = replies[sessions[sid]['turns'] % 5]
    return Response(status='success', reply=reply)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
"@ | Out-File main.py -Encoding utf8

# FIXED requirements.txt (NO audio deps)
@"
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
"@ | Out-File requirements.txt -Encoding utf8
