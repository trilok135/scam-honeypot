
import re
import random
from .utils import simulate_latency
from .prompts import PHASE_1_SYSTEM_PROMPT

class ScamDetector:
    def __init__(self):
        self.risk_patterns = [
            r"urgent", r"immediately", r"blocked", r"suspended",
            r"click here", r"bit\.ly", r"verify", r"kyc",
            r"sbi", r"hdfc", r"icici",  # Common banks
            r"lottery", r"won", r"prize"
        ]
        
    def assess_threat(self, message):
        """
        Analyzes the message for scam indicators with weighted scoring.
        Returns a JSON-compatible dict.
        """
        simulate_latency()
        
        message_lower = message.lower()
        score = 0.0
        matches = []
        
        # Weighted Keywords
        # 1. Financial/Official Scams
        critical_keywords = [r"urgent", r"immediately", r"blocked", r"suspended", r"kyc", r"sbi", r"hdfc", r"otp"]
        
        # 2. Emergency/Distress Scams (New Category)
        emergency_keywords = [r"wedding", r"hospital", r"bounced", r"sister", r"emergency", r"help needed", r"stuck", r"god bless"]
        
        # 3. Payment/Action Scams
        payment_keywords = [r"gpay", r"paytm", r"phonepe", r"transfer", r"rupees", r"account details", r"send money"]
        
        suspicious_keywords = [r"click here", r"bit\.ly", r"verify", r"lottery", r"won", r"prize", r"refund"]
        
        for pattern in critical_keywords:
            if re.search(pattern, message_lower):
                score += 0.3
                matches.append(pattern)

        for pattern in emergency_keywords:
            if re.search(pattern, message_lower):
                score += 0.3  # High risk for emotional manipulation
                matches.append(pattern)

        for pattern in payment_keywords:
            if re.search(pattern, message_lower):
                score += 0.2
                matches.append(pattern)
                
        for pattern in suspicious_keywords:
            if re.search(pattern, message_lower):
                score += 0.15
                matches.append(pattern)
        
        # Check for URLs or UPIs (Strong indicators)
        if re.search(r"http|www\.|bit\.ly", message_lower):
            score += 0.2
            matches.append("contains_url")
            
        if re.search(r"[a-zA-Z0-9.\-_]+@[a-zA-Z]+", message):  # Simple UPI check
            score += 0.2
            matches.append("contains_upi")
        
        # Normalize Score
        is_scam = score > 0.3
        confidence = min(score, 0.99) if is_scam else 0.1
        
        return {
            "is_scam": is_scam,
            "confidence": round(confidence, 2),
            "type": "financial_scam" if is_scam else "safe",
            "reason": f"Detected indicators: {matches}" if matches else "No suspicious patterns found."
        }
