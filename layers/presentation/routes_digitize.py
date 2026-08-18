import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from werkzeug.utils import secure_filename
from layers.business_logic.digitizer_service import DigitizerService
from layers.data_storage.config_repository import ConfigRepository
from layers.data_storage.form_repository import FormRepository
from layers.business_logic.auth_service import admin_required
from layers.business_logic.audit_service import AuditService

digitize_bp = Blueprint("digitize", __name__)
digitizer_service = DigitizerService()
config_repo = ConfigRepository()
form_repo = FormRepository()
audit_service = AuditService()

ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv", ".docx", ".doc", ".pdf"}

@digitize_bp.route("/digitize", methods=["GET", "POST"])
@admin_required
def digitize_form():
    config = config_repo.get_config()

    if request.method == "POST":
        file = request.files.get("form_file")
        form_name = request.form.get("form_name", "").strip()
        form_version = request.form.get("form_version", "").strip()

        if not file or file.filename == "":
            return render_template("digitize.html", config=config, error="Por favor seleccione un archivo del explorador.")

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return render_template("digitize.html", config=config, error=f"Formato de archivo no soportado ({ext}). Formatos permitidos: xlsx, csv, docx, pdf.")

        original_clean_name = secure_filename(file.filename)
        safe_filename = f"upload_{uuid.uuid4().hex[:12]}{ext}"
        
        uploads_dir = os.path.join(current_app.root_path, "storage", "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        file_path = os.path.join(uploads_dir, safe_filename)
        file.save(file_path)

        if not form_name:
            form_name = os.path.splitext(original_clean_name)[0]
        if not form_version:
            form_version = "01.0001"

        try:
            raw_fields = digitizer_service.parse_file_fields(file_path)
            session["digitize_draft"] = {
                "form_name": form_name,
                "form_version": form_version,
                "fields": raw_fields
            }
            audit_service.log("CARGA_ARCHIVO", f"Digitalizado borrador inicial de archivo '{original_clean_name}'")
            return redirect(url_for("digitize.digitize_review"))
        except Exception as e:
            return render_template("digitize.html", config=config, error=f"Error al digitalizar el archivo: {str(e)}")

    return render_template("digitize.html", config=config, error=None)

@digitize_bp.route("/digitize/review", methods=["GET", "POST"])
@admin_required
def digitize_review():
    config = config_repo.get_config()
    draft = session.get("digitize_draft")

    if not draft or not isinstance(draft, dict) or "fields" not in draft:
        return redirect(url_for("digitize.digitize_form"))

    existing_fields = form_repo.get_all_unique_fields()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "confirm":
            try:
                saved_form = digitizer_service.save_final_digitized_form(
                    draft.get("form_name", "Nuevo Formulario"),
                    draft.get("form_version", "01.0001"),
                    draft.get("fields", [])
                )
                audit_service.log("FORMULARIO_DIGITALIZADO", f"Guardado nuevo formulario '{saved_form.get('name')}' con {len(draft.get('fields', []))} campos")
                session.pop("digitize_draft", None)
                return redirect(url_for("main.index"))
            except Exception as e:
                return render_template(
                    "digitize_review.html",
                    draft=draft,
                    config=config,
                    existing_fields=existing_fields,
                    error=f"Error al guardar el formulario: {str(e)}"
                )

        elif action == "add_fields":
            selected_labels = request.form.getlist("selected_existing_labels")
            current_fields = draft.get("fields", [])

            for label in selected_labels:
                matching = next((f for f in existing_fields if f.get("label") == label), None)
                if matching:
                    new_field = dict(matching)
                    new_field["id"] = f"added_{uuid.uuid4().hex[:6]}"
                    current_fields.append(new_field)

            draft["fields"] = current_fields
            session["digitize_draft"] = draft
            session.modified = True
            audit_service.log("CAMPOS_AGREGADOS", f"Agregados {len(selected_labels)} campos desde otros formularios")
            return redirect(url_for("digitize.digitize_review"))

        elif action == "cancel":
            session.pop("digitize_draft", None)
            return redirect(url_for("main.index"))

    return render_template(
        "digitize_review.html",
        draft=draft,
        config=config,
        existing_fields=existing_fields
    )

@digitize_bp.route("/digitize/move-field/<field_id>/<direction>")
@admin_required
def move_field(field_id, direction):
    draft = session.get("digitize_draft")
    if draft and "fields" in draft:
        fields = draft["fields"]
        idx = next((i for i, f in enumerate(fields) if f.get("id") == field_id), -1)

        if idx != -1:
            if direction == "up" and idx > 0:
                fields[idx], fields[idx - 1] = fields[idx - 1], fields[idx]
            elif direction == "down" and idx < len(fields) - 1:
                fields[idx], fields[idx + 1] = fields[idx + 1], fields[idx]

            draft["fields"] = fields
            session["digitize_draft"] = draft
            session.modified = True

    return redirect(url_for("digitize.digitize_review"))

@digitize_bp.route("/digitize/reject-field/<field_id>")
@admin_required
def reject_field(field_id):
    draft = session.get("digitize_draft")
    if draft and "fields" in draft:
        draft["fields"] = [f for f in draft.get("fields", []) if f.get("id") != field_id]
        session["digitize_draft"] = draft
        session.modified = True
    return redirect(url_for("digitize.digitize_review"))
