import os
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from werkzeug.utils import secure_filename
from layers.data_storage.form_repository import FormRepository
from layers.data_storage.config_repository import ConfigRepository
from layers.business_logic.auth_service import login_required, admin_required

main_bp = Blueprint("main", __name__)
form_repo = FormRepository()
config_repo = ConfigRepository()

@main_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 5

    all_forms = form_repo.list_forms()
    total_forms = len(all_forms)
    total_pages = (total_forms + per_page - 1) // per_page if total_forms > 0 else 1

    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    forms_page = all_forms[start_idx:end_idx]

    config = config_repo.get_config()
    error_msg = request.args.get("error")

    return render_template(
        "index.html",
        forms=forms_page,
        current_page=page,
        total_pages=total_pages,
        total_forms=total_forms,
        config=config,
        error=error_msg
    )

@main_bp.route("/form/<form_id>/delete", methods=["POST"])
@admin_required
def delete_form(form_id):
    form_repo.delete_form(form_id)
    return redirect(url_for("main.index"))

@main_bp.route("/api/upload-logo", methods=["POST"])
@admin_required
def upload_logo():
    if "logo" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files["logo"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename"}), 400

    if file:
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.static_folder, "uploads", "assets")
        os.makedirs(upload_folder, exist_ok=True)

        target_path = os.path.join(upload_folder, filename)
        file.save(target_path)

        new_config = config_repo.update_logo(filename)
        return jsonify({"success": True, "logo_url": new_config["company_logo_url"]})

    return jsonify({"success": False, "error": "Upload failed"}), 400
