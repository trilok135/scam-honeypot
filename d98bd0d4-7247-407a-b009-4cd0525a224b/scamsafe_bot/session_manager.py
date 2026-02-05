
import json
import time
from datetime import datetime

class SessionManager:
    def __init__(self, log_file="session_logs.json"):
        self.log_file = log_file
        self.session_data = {
            "session_id": str(int(time.time())),
            "start_time": datetime.now().isoformat(),
            "interactions": [],
            "status": "active"
        }
    
    def log_interaction(self, role, content, metadata=None):
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        self.session_data["interactions"].append(interaction)
        self._save()
        
    def _save(self):
        try:
            with open(self.log_file, "w") as f:
                json.dump(self.session_data, f, indent=2)
        except Exception as e:
            print(f"Error saving session log: {e}")

    def get_history(self):
        return self.session_data["interactions"]
