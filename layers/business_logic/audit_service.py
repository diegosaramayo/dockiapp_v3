from flask import request, session
from layers.data_storage.audit_repository import AuditRepository

class AuditService:
    def __init__(self):
        self.repository = AuditRepository()

    def log(self, action, details):
        user = session.get("user", {})
        username = user.get("username", "Sistema")
        role = user.get("role", "Sistema")
        
        try:
            client_ip = request.remote_addr or "127.0.0.1"
        except Exception:
            client_ip = "127.0.0.1"

        return self.repository.log_event(
            username=username,
            role=role,
            ip=client_ip,
            action=action,
            details=details
        )

    def get_audit_trail(self):
        return self.repository.list_events()
