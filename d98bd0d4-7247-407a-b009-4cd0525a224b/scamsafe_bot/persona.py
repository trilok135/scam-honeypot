
import random
from .utils import simulate_latency
from .prompts import PHASE_2_PERSONA_PROMPT

class PersonaEngine:
    def __init__(self):
        self.turns = 0
        self.responses = [
            "My account is blocked? Aiyoh, really? I have EMI deducted tomorrow! What should I do sir?",
            "Sir, I am trying to open the link but it is not working. My network is slow. Can you send again?",
            "I have clicked it. It is asking for password. Should I give? I am scared.",
            "Sir, why you need my PIN? My son said never share PIN. But I need to unlock account no?",
            "Okay okay, I am entering details. Wait... it says 'Invalid Request'. Are you sure this is SBI?",
            "Sir, can I just Google Pay you the penalty? Accessing bank site is too hard for me."
        ]
        
    def engage(self, user_message):
        """
        Generates a response as Deepak Sharma.
        """
        simulate_latency(1.0, 2.0)
        
        # Simple turn-based logic for the mockup
        if self.turns < len(self.responses):
            response_text = self.responses[self.turns]
        else:
            response_text = "Sir? Are you there? I am waiting."
            
        self.turns += 1
        
        # Extract Actual Intel using Regex
        extracted_intel = {}
        
        # 1. UPI Extraction (e.g., username@bank)
        upi_pattern = r"[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}"
        upis = re.findall(upi_pattern, user_message)
        if upis:
            extracted_intel["upi_ids"] = upis

        # 2. URL Extraction (http/https/bit.ly)
        # Matches http/s protocols or common shorteners like bit.ly even without protocol
        url_pattern = r"(?:https?://|www\.)\S+|bit\.ly/\S+"
        urls = re.findall(url_pattern, user_message)
        if urls:
            extracted_intel["phishing_urls"] = urls

        # 3. Phone Number Extraction (Indian mobile focus: +91 or starting with 6-9)
        # Matches patterns like +91 9876543210, 98765 43210, or just 10 digits
        phone_pattern = r"(?:\+91[\-\s]?)?[6789]\d{9}"
        phones = re.findall(phone_pattern, user_message)
        if phones:
            extracted_intel["phone_numbers"] = phones

        return {
            "message": response_text,
            "extracted_intel": extracted_intel,
            "status": "engaged" if self.turns < 10 else "terminating"
        }
import re
