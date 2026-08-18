from flask import Blueprint, render_template, request
from layers.business_logic.audit_service import AuditService
from layers.data_storage.config_repository import ConfigRepository
from layers.business_logic.auth_service import admin_required

audit_bp = Blueprint("audit", __name__)
audit_service = AuditService()
config_repo = ConfigRepository()

@audit_bp.route("/audit")
@admin_required
def view_audit_log():
    config = config_repo.get_config()
    all_events = audit_service.get_audit_trail()

    search_query = request.args.get("q", "").strip().lower()
    if search_query:
        events = [
            e for e in all_events
            if search_query in e.get("action", "").lower()
            or search_query in e.get("username", "").lower()
            or search_query in e.get("details", "").lower()
            or search_query in e.get("ip", "").lower()
        ]
    else:
        events = all_events

    return render_template("audit.html", events=events, config=config, search_query=search_query)
