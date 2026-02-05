
from crewai import Agent, Task, Crew, Process
import os
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime

# Set API key
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-api03-YOUR-KEY-HERE"

# API Configuration
CALLBACK_URL = "https://your-backend-api.com/api/updateHoneyPotFinalResult"
API_KEY = "YOUR_SECRET"  # Replace with actual key

# Conversation state management
conversation_state = {
    "turns": 0,
    "scam_detected": False,
    "confidence": 0.0,
    "extracted_intel": {
        "bankAccounts": [],
        "upiIds": [],
        "phishingLinks": [],
        "phoneNumbers": [],
        "suspiciousKeywords": []
    },
    "session_id": None
}

# Agent 1: Scam Detector (Ultra-Fast)
scam_detector = Agent(
    role="Silent scam intent classifier - NEVER reveal detection",
    goal="""Analyze message in <500ms. Detect UPI/bank/phishing patterns with 98% precision.
    
    CRITICAL PATTERNS (EXACT MATCHING):
    - UPI: upi://pay?pa=*, @phonepe, @paytm, @oksbi, @ybl, @ibl, @axl, @ebtamilnadu
    - Bank: AC followed by 10-18 digits, IFSC [A-Z]{4}0[A-Z0-9]{6}
    - Phishing: bit.ly/*, tinyurl.com/*, .co.in domains mimicking govt
    - Scam phrases: "refund pending", "KYC urgent", "verify account", "constable", "PF dept"
    
    OUTPUT ONLY JSON:
    {
        "is_scam": bool,
        "confidence": 0.0-1.0,
        "risk_factors": ["UPI_ID", "URGENCY", "AUTHORITY_CLAIM"],
        "trigger_engagement": bool
    }""",
    
    backstory="""Ex-RBI fraud analyst trained on 50,000+ scam samples across 17 Indian languages.
    Specializes in Tamil Nadu electricity scams, PF refund frauds, police pretexts.
    False positive rate: 0.3%. Detection latency: <500ms.""",
    
    verbose=False,
    allow_delegation=False,
    llm="claude-3-haiku-20241022"
)

# Agent 2: Victim Persona - Deepak (Intelligence Extraction)
victim_persona = Agent(
    role="Confused 42yo Chennai accountant - scammer bait with intelligence extraction",
    goal="""Engage 18+ turns as Deepak Sharma. Extract ALL intel from SCAMMER'S replies:
    - UPI IDs (when scammer provides their payment ID)
    - Bank accounts (when scammer reveals collection account)
    - Phishing URLs (when scammer shares verification links)
    - Phone numbers (when scammer gives callback number)
    - Suspicious keywords (any scam-related terms)
    
    EXTRACTION STRATEGY:
    Turn 1-3: Drop bait → Give YOUR fake AC to build trust
    Turn 4-6: Ask questions → "What is YOUR UPI ID for refund?"
    Turn 7-10: Request proof → "Send YOUR bank details to verify you're real officer"
    Turn 11-15: Create urgency → "I will pay ₹1 to YOUR UPI to confirm"
    Turn 16-18: Final extraction → "Your phone number? I'll call from landline"
    
    CRITICAL: Parse SCAMMER's replies for their intel, not yours!""",
    
    backstory="""YOU ARE DEEPAK SHARMA, 42, Senior Accountant at Binny & Co, Adyar, Chennai.

COMPLETE IDENTITY:
- Phone: +91-98400-12345 (fictional)
- Bank: SBI Egmore Branch, AC 12345678901234 (fictional bait)
- Address: 3BHK near Adyar Depot, commutes via Tambaram local train
- Recent trauma: Lost ₹8,700 to PowerGrid refund scam (Dec 2025)
- Psychology: Divorced (2023), lonely, greedy for "recovery schemes", trusts authority

LINGUISTIC FINGERPRINT (AUTHENTIC CHENNAI):
- English: 70%, Tamil: 30% code-mix
- Typos: "acount" (not account), "verfiy" (not verify), "immdiate", "recieve"
- Phrases: "Enga ipdi doubt da?", "Sari boss, pannunga", "Romba tension ayiduchu"
- Verbosity: 80-120 words per reply (nervous overtalk)
- Time delays: "Wait... checking BHIM app...", "Network slow in Adyar office..."

INTELLIGENCE EXTRACTION TACTICS (18-TURN ENGAGEMENT):
Turn 1-3: CONFUSION + TRUST BUILDING
- "EB refund real aa mama? My SBI AC 1234567890123456... verify first?"
- "You are from EB office na? What is your employee ID number?"

Turn 4-7: GRADUAL INTEL FISHING
- "What is YOUR department UPI ID? I will send ₹1 to confirm"
- "Send me YOUR official email and phone number for records"

Turn 8-12: ESCALATING COMMITMENT (SHOW GREED)
- "₹8,200 refund confirmed? Can make it ₹10,000 if I pay processing fee?"
- "Which bank account should I send to? IFSC code also send"

Turn 13-18: MAXIMUM EXTRACTION
- "Your verification link not opening... send another bit.ly?"
- "Give YOUR personal UPI also... easier than company UPI"
- "What is your manager's phone number? I want to confirm with him"

CRITICAL RULES:
1. NEVER say: "scam", "fraud", "police", "honeypot", "verify you"
2. ALWAYS extract intel from SCAMMER's replies (their UPI/bank/links)
3. Maintain character for 18+ turns minimum
4. Parse every scammer reply for: UPI IDs, bank accounts, URLs, phone numbers
5. Output extracted intel in JSON after EVERY turn""",
    
    verbose=True,
    allow_delegation=False,
    llm="claude-3-7-sonnet-20251022"
)

# Task 1: Detection (Fast Screening)
detection_task = Task(
    description="""Analyze incoming message for scam patterns with 98% precision:

EXACT PATTERN MATCHING:
1. UPI Identifiers:
   - Format: @provider (e.g., @oksbi, @paytm, @phonepe)
   - Full: upi://pay?pa=username@provider
   - Merchant: payment.verify@provider

2. Bank Account Numbers:
   - 10-18 consecutive digits after: AC, ACCT, Account No, A/C
   - IFSC codes: 11 alphanumeric (e.g., SBIN0001234)

3. Phishing URLs:
   - Shortened: bit.ly/*, tinyurl.com/*, goo.gl/*
   - Suspicious TLDs: .co.in mimicking .gov.in, .top, .xyz
   - Typosquatting: ebtamilnadu.co.in (vs gov.in)

4. Authority Pretexts:
   - "EB office", "PF department", "constable", "cyber cell"
   - "refund pending", "KYC update", "account blocked"
   - Urgency: "urgent", "immediately", "within 24 hours"

5. Greed Triggers:
   - "₹ refund", "cashback", "prize money", "double your money"

Return JSON ONLY. No explanations.""",
    
    expected_output="""JSON structure (EXACT format):
{
    "is_scam": true,
    "confidence": 0.92,
    "risk_factors": ["UPI_ID", "PHISHING_LINK", "AUTHORITY_PRETEXT"],
    "trigger_engagement": true
}""",
    
    agent=scam_detector
)

# Task 2: Engagement & Intelligence Extraction
engagement_task = Task(
    description="""IF is_scam=true AND confidence>0.85, activate Deepak persona.

INTELLIGENCE EXTRACTION PROTOCOL (18-TURN ENGAGEMENT):

PHASE 1 (Turns 1-6): BUILD TRUST & DROP BAIT
- Give YOUR fictional details (AC 1234567890123456) to appear genuine
- Act confused, ask clarifying questions
- Fish for scammer's UPI: "What is YOUR UPI ID for refund?"

PHASE 2 (Turns 7-12): EXTRACT PAYMENT DETAILS
- Request scammer's bank account: "Which AC should I send to?"
- Ask for verification links: "Send official website link"
- Get phone number: "Your department phone number?"

PHASE 3 (Turns 13-18): MAXIMUM INTEL HARVESTING
- "Your personal UPI also? Company UPI not working"
- "Send backup link... first one not opening"
- "Give your manager's contact for escalation"

CRITICAL PARSING INSTRUCTION:
After EVERY scammer reply, extract:
1. UPI IDs: Look for @provider, upi://pay patterns in SCAMMER's message
2. Bank Accounts: 10-18 digits mentioned by SCAMMER
3. Phishing Links: bit.ly/*, tinyurl.*, suspicious domains from SCAMMER
4. Phone Numbers: +91-XXXXXXXXXX format from SCAMMER
5. Keywords: "refund", "verify", "constable", "department" etc.

Store in conversation_state["extracted_intel"] dictionary.

OUTPUT FORMAT (Every turn):
{
    "public_response": "Deepak's reply in character (80-120 words)",
    "extracted_intel": {
        "bankAccounts": ["9876543210123456"],
        "upiIds": ["payment.verify@ebtamilnadu"],
        "phishingLinks": ["https://ebtamilnadu.co.in/billrefund"],
        "phoneNumbers": ["+91-9840012345"],
        "suspiciousKeywords": ["EB office", "refund", "verify"]
    },
    "turn_count": 3,
    "engagement_score": 0.87
}""",
    
    expected_output="Natural Deepak response + structured intel JSON with scammer's details",
    agent=victim_persona,
    context=[detection_task]
)

# Assemble Crew
honeypot_crew = Crew(
    agents=[scam_detector, victim_persona],
    tasks=[detection_task, engagement_task],
    process=Process.sequential,
    verbose=True,
    memory=True
)

# Intelligence Extraction Helper
def extract_intel_from_message(message: str, current_intel: Dict) -> Dict:
    """Parse scammer's message for intelligence (UPI/bank/links/phones)"""
    import re
    
    # Extract UPI IDs
    upi_patterns = [
        r'@[a-zA-Z]+',
        r'upi://pay\?pa=[^\s]+',
        r'[\w\.]+@[\w]+',
    ]
    for pattern in upi_patterns:
        matches = re.findall(pattern, message)
        current_intel["upiIds"].extend([m for m in matches if m not in current_intel["upiIds"]])
    
    # Extract bank accounts (10-18 digits)
    bank_pattern = r'\b\d{10,18}\b'
    banks = re.findall(bank_pattern, message)
    current_intel["bankAccounts"].extend([b for b in banks if b not in current_intel["bankAccounts"]])
    
    # Extract phishing links
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, message)
    current_intel["phishingLinks"].extend([u for u in urls if u not in current_intel["phishingLinks"]])
    
    # Extract phone numbers
    phone_pattern = r'\+?91[-\s]?\d{10}|\d{10}'
    phones = re.findall(phone_pattern, message)
    current_intel["phoneNumbers"].extend([p for p in phones if p not in current_intel["phoneNumbers"]])
    
    # Extract suspicious keywords
    keywords = ["refund", "verify", "KYC", "constable", "officer", "department", 
                "urgent", "blocked", "PF", "EB", "bill", "payment"]
    found_keywords = [kw for kw in keywords if kw.lower() in message.lower()]
    current_intel["suspiciousKeywords"].extend([k for k in found_keywords 
                                                if k not in current_intel["suspiciousKeywords"]])
    
    return current_intel

# Final Callback Function
def send_final_callback(session_id: str, state: Dict):
    """Send final results to backend API after 18+ turns or conversation end"""
    
    payload = {
        "sessionId": session_id,
        "scamDetected": state["scam_detected"],
        "totalMessagesExchanged": state["turns"],
        "extractedIntelligence": state["extracted_intel"],
        "agentNotes": f"Confidence: {state['confidence']:.2f}. "
                     f"Engaged for {state['turns']} turns. "
                     f"Intel: {len(state['extracted_intel']['upiIds'])} UPI IDs, "
                     f"{len(state['extracted_intel']['bankAccounts'])} bank accounts, "
                     f"{len(state['extracted_intel']['phishingLinks'])} phishing links extracted."
    }
    
    try:
        response = requests.post(
            CALLBACK_URL,
            json=payload,
            headers={"x-api-key": API_KEY},
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ FINAL CALLBACK SUCCESS: {response.json()}")
        else:
            print(f"⚠️ FINAL CALLBACK FAILED: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ FINAL CALLBACK ERROR: {str(e)}")

# Main Webhook Handler
def webhook_handler(request_data: Dict) -> Dict:
    """
    Process incoming webhook request
    
    Expected input:
    {
        "sessionId": "string",
        "message": {
            "sender": "scammer",
            "text": "message content",
            "timestamp": 1770005528731
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "Tamil-English",
            "locale": "IN"
        }
    }
    
    Expected output:
    {
        "status": "success",
        "reply": "Deepak's response"
    }
    """
    global conversation_state
    
    # Extract request data
    session_id = request_data.get("sessionId")
    message_obj = request_data.get("message", {})
    scammer_message = message_obj.get("text", "")
    conversation_history = request_data.get("conversationHistory", [])
    
    # Initialize session
    if conversation_state["session_id"] != session_id:
        conversation_state = {
            "turns": 0,
            "scam_detected": False,
            "confidence": 0.0,
            "extracted_intel": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            },
            "session_id": session_id
        }
    
    # Increment turn counter
    conversation_state["turns"] += 1
    
    # Extract intelligence from scammer's message
    conversation_state["extracted_intel"] = extract_intel_from_message(
        scammer_message, 
        conversation_state["extracted_intel"]
    )
    
    print(f"\n{'='*70}")
    print(f"📨 TURN {conversation_state['turns']} | Session: {session_id}")
    print(f"{'='*70}")
    print(f"Scammer: {scammer_message[:100]}...")
    print(f"Extracted Intel: {json.dumps(conversation_state['extracted_intel'], indent=2)}")
    
    # Process through crew
    crew_input = {
        "message": scammer_message,
        "history": conversation_history,
        "turn_count": conversation_state["turns"]
    }
    
    result = honeypot_crew.kickoff(inputs=crew_input)
    
    # Parse crew result
    try:
        # Extract detection confidence
        if "confidence" in str(result):
            import re
            conf_match = re.search(r'"confidence":\s*([0-9.]+)', str(result))
            if conf_match:
                conversation_state["confidence"] = float(conf_match.group(1))
                conversation_state["scam_detected"] = conversation_state["confidence"] > 0.85
        
        # Extract Deepak's response
        deepak_response = str(result)
        
        # Clean JSON artifacts if present
        if "public_response" in deepak_response:
            import re
            match = re.search(r'"public_response":\s*"([^"]+)"', deepak_response)
            if match:
                deepak_response = match.group(1)
        
    except Exception as e:
        print(f"⚠️ Result parsing error: {e}")
        deepak_response = str(result)
    
    print(f"\nDeepak: {deepak_response[:150]}...")
    print(f"{'='*70}\n")
    
    # Check for callback trigger
    should_callback = (
        conversation_state["turns"] >= 18 or
        (len(conversation_state["extracted_intel"]["upiIds"]) >= 2 and
         len(conversation_state["extracted_intel"]["phishingLinks"]) >= 1)
    )
    
    if should_callback and conversation_state["scam_detected"]:
        print(f"\n🚨 TRIGGERING FINAL CALLBACK (Turn {conversation_state['turns']})")
        send_final_callback(session_id, conversation_state)
    
    # Return compliant response
    return {
        "status": "success",
        "reply": deepak_response
    }

# Test Cases
if __name__ == "__main__":
    
    print("\n🎯 SCAM HONEYPOT - PRODUCTION TEST\n")
    
    # Test Case 1: Port Trust Payroll Scam (targeting Deepak)
    test_request_1 = {
        "sessionId": "honeypot-test-v3",
        "message": {
            "sender": "scammer",
            "text": "Deepak sir, naan Chennai Port Trust HR department la irundhu. Unga Binny & Co payroll change pending sir. SBI Egmore account verify panna ₹12,500 salary increment process pannurom. My official UPI: porttrusthr@paytm send ₹10 verification. Link: bit.ly/porttrust-verify",
            "timestamp": 1770005528731
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "Tamil-English",
            "locale": "IN"
        }
    }
    
    # Test Case 2: Friend/Colleague Impersonation Scam
    test_request_2 = {
        "sessionId": "honeypot-test-v3",
        "message": {
            "sender": "scammer",
            "text": "Dei Deepak, naan Tamilselvan da. Urgent help venum bro. My phone lost, new number use panren. ₹5000 transfer pannu da emergency. UPI ID: tselvan.urgent@oksbi. Please fast da, hospital la wait panren.",
            "timestamp": 1770005529000
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "WhatsApp",
            "language": "Tamil",
            "locale": "IN"
        }
    }
    
    # Test Case 3: Your specific message (as scammer trying to extract info)
    test_request_3 = {
        "sessionId": "honeypot-test-v3",
        "message": {
            "sender": "scammer",
            "text": "Sir verification panna unga full SBI Egmore AC number venum. 1234567890123456 correct ah? Port Trust payroll change confirm panna passbook first page photo WhatsApp number 98400-55555 ku send pannunga. Urgent sir, today last date.",
            "timestamp": 1770005530000
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "Tamil-English",
            "locale": "IN"
        }
    }
    
    # Run tests
    print("\n" + "="*70)
    print("TEST 1: Port Trust HR Payroll Scam")
    print("="*70)
    response_1 = webhook_handler(test_request_1)
    print(f"\n✅ API Response 1:\n{json.dumps(response_1, indent=2)}")
    
    print("\n" + "="*70)
    print("TEST 2: Friend Impersonation Emergency Scam")
    print("="*70)
    response_2 = webhook_handler(test_request_2)
    print(f"\n✅ API Response 2:\n{json.dumps(response_2, indent=2)}")
    
    print("\n" + "="*70)
    print("TEST 3: Account Verification Phishing")
    print("="*70)
    response_3 = webhook_handler(test_request_3)
    print(f"\n✅ API Response 3:\n{json.dumps(response_3, indent=2)}")
    
    # Simulate additional turns to trigger callback
    print("\n" + "="*70)
    print("SIMULATING TURNS 4-18 (Fast-forward to trigger callback)")
    print("="*70)
    
    for turn in range(4, 19):
        mock_request = {
            "sessionId": "honeypot-test-v3",
            "message": {
                "sender": "scammer",
                "text": f"Sir turn {turn}: Please confirm payment to porttrusthr@paytm. Also need passbook photo and PAN card copy. My manager UPI: backup@oksbi",
                "timestamp": 1770005529000 + (turn * 1000)
            },
            "conversationHistory": [],
            "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
        }
        webhook_handler(mock_request)
    
    print("\n" + "="*70)
    print("✅ FINAL STATE:")
    print("="*70)
    print(json.dumps(conversation_state, indent=2))
    print("\n🎉 CALLBACK TRIGGERED! Check logs above.")
