import json
from flask import Blueprint, render_template, request, redirect, url_for, session, Response, jsonify
from layers.data_storage.form_repository import FormRepository
from layers.data_storage.config_repository import ConfigRepository
from layers.business_logic.form_engine import FormEngine
from layers.business_logic.rules_engine import RulesEngine
from layers.business_logic.skills_engine import SkillsEngine
from layers.business_logic.txt_exporter import TXTExporter
from layers.business_logic.auth_service import login_required
from layers.business_logic.audit_service import AuditService

form_bp = Blueprint("form", __name__)
form_repo = FormRepository()
config_repo = ConfigRepository()
rules_engine = RulesEngine()
skills_engine = SkillsEngine()
exporter = TXTExporter()
audit_service = AuditService()

@form_bp.route("/form/<form_id>/step/<int:step_num>", methods=["GET", "POST"])
@login_required
def render_step(form_id, step_num):
    form_data = form_repo.get_form_by_id(form_id)
    if not form_data:
        return redirect(url_for("main.index"))

    engine = FormEngine(form_data)
    config = config_repo.get_config()

    if step_num > engine.total_pages:
        return redirect(url_for("form.render_final", form_id=form_id))

    session_key = f"form_responses_{form_id}"
    
    if request.args.get("reset") == "1":
        session.pop(session_key, None)

    if session_key not in session:
        session[session_key] = {}

    responses = session.get(session_key, {})

    if request.method == "POST":
        for key, val in request.form.items():
            responses[key] = val
        session[session_key] = responses
        session.modified = True

        action = request.form.get("action")
        if action == "next":
            next_step = step_num + 1
            if next_step >= engine.total_pages:
                return redirect(url_for("form.render_final", form_id=form_id))
            return redirect(url_for("form.render_step", form_id=form_id, step_num=next_step))
        elif action == "back":
            prev_step = step_num - 1
            if prev_step < 1:
                session.pop(session_key, None)
                return redirect(url_for("main.index"))
            return redirect(url_for("form.render_step", form_id=form_id, step_num=prev_step))

    step_data = engine.get_step(step_num)
    if not step_data:
        return redirect(url_for("form.render_final", form_id=form_id))

    transformed_fields = rules_engine.apply_transformations_to_fields(step_data.get("fields", []))
    transformed_fields = skills_engine.apply_skill_transformations(transformed_fields)

    step_data_copy = dict(step_data)
    step_data_copy["fields"] = transformed_fields

    active_alerts = rules_engine.evaluate_rules(responses)

    return render_template(
        "form_step.html",
        form=form_data,
        step=step_data_copy,
        step_num=step_num,
        total_pages=engine.total_pages,
        config=config,
        responses=responses,
        active_alerts=active_alerts
    )

@form_bp.route("/form/<form_id>/final", methods=["GET", "POST"])
@login_required
def render_final(form_id):
    form_data = form_repo.get_form_by_id(form_id)
    if not form_data:
        return redirect(url_for("main.index"))

    engine = FormEngine(form_data)
    config = config_repo.get_config()
    session_key = f"form_responses_{form_id}"
    responses = session.get(session_key, {})

    if request.method == "POST":
        action = request.form.get("action")
        if action == "cancel":
            session.pop(session_key, None)
            return redirect(url_for("main.index"))

    return render_template(
        "form_final.html",
        form=form_data,
        step_num=engine.total_pages,
        total_pages=engine.total_pages,
        config=config,
        responses=responses
    )

@form_bp.route("/form/<form_id>/download-txt", methods=["GET", "POST"])
@login_required
def download_txt(form_id):
    form_data = form_repo.get_form_by_id(form_id)
    if not form_data:
        return redirect(url_for("main.index"))

    session_key = f"form_responses_{form_id}"
    responses = session.get(session_key, {})

    txt_content = exporter.export(form_data, responses)
    clean_name = form_data.get("short_name", "Formulario").replace(" ", "_")
    filename = f"Solicitud_{clean_name}_{form_id}.txt"

    # MEDIDA 4: Registrar auditoría de exportación de datos de solicitud de cliente
    audit_service.log("SOLICITUD_EXPORTADA", f"Completado y exportado archivo TXT para el formulario '{form_data.get('name')}'")

    session.pop(session_key, None)
    session.modified = True

    return Response(
        txt_content,
        mimetype="text/plain",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )
