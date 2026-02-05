
import json
import re
import time
import random

def extract_json(response_text):
    """
    Extracts a JSON object from a string, handling potential markdown code blocks.
    """
    try:
        # Match JSON block between ```json and ``` or just {}
        match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        
        match = re.search(r'(\{.*?\})', response_text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
            
        return None
    except json.JSONDecodeError:
        return None

def simulate_latency(min_seconds=0.5, max_seconds=1.5):
    """
    Simulates processing latency.
    """
    time.sleep(random.uniform(min_seconds, max_seconds))
