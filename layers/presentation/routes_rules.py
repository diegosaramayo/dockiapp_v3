import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from layers.data_storage.rule_repository import RuleRepository
from layers.data_storage.config_repository import ConfigRepository
from layers.business_logic.rules_engine import RulesEngine
from layers.business_logic.parsers.image_parser import ImageParser
from layers.business_logic.auth_service import admin_required

rules_bp = Blueprint("rules", __name__)
rule_repo = RuleRepository()
config_repo = ConfigRepository()
rules_engine = RulesEngine()
image_parser = ImageParser()

@rules_bp.route("/rules")
@admin_required
def list_rules():
    config = config_repo.get_config()
    rules = rule_repo.list_rules()
    return render_template("rules.html", rules=rules, config=config)

@rules_bp.route("/rules/create", methods=["POST"])
@admin_required
def create_rule():
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip()
    field = request.form.get("target_field", "").strip()
    condition = request.form.get("condition", "equals")
    val = request.form.get("trigger_value", "").strip()
    action = request.form.get("action", "require_doc")
    msg = request.form.get("message", "").strip()

    if name:
        image_file = request.files.get("image")
        image_url = None

        if image_file and image_file.filename != "":
            upload_dir = os.path.join(current_app.static_folder, "uploads", "images")
            saved_name = image_parser.save_image(image_file, upload_dir)
            if saved_name:
                image_url = f"/static/uploads/images/{saved_name}"

        rule_repo.save_rule({
            "code": code or "RL-NEW",
            "name": name,
            "target_field": field,
            "condition": condition,
            "trigger_value": val,
            "action": action,
            "message": msg,
            "image_url": image_url
        })

    return redirect(url_for("rules.list_rules"))

@rules_bp.route("/rules/upload-excel", methods=["POST"])
@admin_required
def upload_excel():
    file = request.files.get("excel_file")
    if file and file.filename != "":
        ext = os.path.splitext(file.filename)[1].lower()
        if ext in [".xlsx", ".xls", ".csv"]:
            safe_filename = f"rule_upload_{uuid.uuid4().hex[:12]}{ext}"
            upload_dir = os.path.join(current_app.root_path, "storage", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, safe_filename)
            file.save(file_path)

            rules_engine.import_rules_from_excel(file_path)

    return redirect(url_for("rules.list_rules"))

@rules_bp.route("/rules/<rule_id>/delete", methods=["POST"])
@admin_required
def delete_rule(rule_id):
    rule_repo.delete_rule(rule_id)
    return redirect(url_for("rules.list_rules"))

@rules_bp.route("/rules/delete-bulk", methods=["POST"])
@admin_required
def delete_rules_bulk():
    rule_ids = request.form.getlist("rule_ids")
    for r_id in rule_ids:
        rule_repo.delete_rule(r_id)
    return redirect(url_for("rules.list_rules"))
