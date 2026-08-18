import os
import json
import uuid
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
AUDIT_FILE = os.path.join(STORAGE_DIR, "audit_log.json")

class AuditRepository:
    def __init__(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        if not os.path.exists(AUDIT_FILE):
            with open(AUDIT_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)

    def log_event(self, username, role, ip, action, details):
        event = {
            "id": f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:4]}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": username or "Anonimo",
            "role": role or "Desconocido",
            "ip": ip or "127.0.0.1",
            "action": action,
            "details": details
        }

        try:
            events = self.list_events()
            events.insert(0, event)
            # Conservar los últimos 1000 eventos de auditoría
            events = events[:1000]

            with open(AUDIT_FILE, "w", encoding="utf-8") as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        return event

    def list_events(self):
        if os.path.exists(AUDIT_FILE):
            try:
                with open(AUDIT_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []
