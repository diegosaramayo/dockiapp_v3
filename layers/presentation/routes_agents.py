import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from layers.data_storage.agent_repository import AgentRepository
from layers.data_storage.skill_repository import SkillRepository
from layers.data_storage.rule_repository import RuleRepository
from layers.data_storage.config_repository import ConfigRepository
from layers.business_logic.agents_engine import AgentsEngine
from layers.business_logic.ollama_service import OllamaService
from layers.business_logic.parsers.image_parser import ImageParser
from layers.business_logic.auth_service import admin_required

agents_bp = Blueprint("agents", __name__)
agent_repo = AgentRepository()
skill_repo = SkillRepository()
rule_repo = RuleRepository()
config_repo = ConfigRepository()
agents_engine = AgentsEngine()
ollama_service = OllamaService()
image_parser = ImageParser()

@agents_bp.route("/agents")
@admin_required
def list_agents():
    config = config_repo.get_config()
    agents = agent_repo.list_agents()

    agents_detailed = []
    for a in agents:
        profile = agents_engine.get_agent_full_profile(a["id"])
        if profile:
            agents_detailed.append(profile)
        else:
            agents_detailed.append(a)

    all_skills = skill_repo.list_skills()
    all_rules = rule_repo.list_rules()

    ollama_running = ollama_service.is_ollama_running()
    ollama_models = ollama_service.list_local_models()

    return render_template(
        "agents.html",
        agents=agents_detailed,
        skills=all_skills,
        rules=all_rules,
        config=config,
        ollama_running=ollama_running,
        ollama_models=ollama_models
    )

@agents_bp.route("/agents/create", methods=["POST"])
@admin_required
def create_agent():
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip()
    role = request.form.get("role", "").strip()
    ollama_model = request.form.get("ollama_model", "").strip()
    selected_skills = request.form.getlist("skills")
    selected_rules = request.form.getlist("rules")

    if name:
        avatar_file = request.files.get("avatar")
        avatar_url = None

        if avatar_file and avatar_file.filename != "":
            upload_dir = os.path.join(current_app.static_folder, "uploads", "images")
            saved_name = image_parser.save_image(avatar_file, upload_dir)
            if saved_name:
                avatar_url = f"/static/uploads/images/{saved_name}"

        agent_repo.save_agent({
            "code": code or "AG-NEW",
            "name": name,
            "role": role or "Asistente Digital",
            "ollama_model": ollama_model if ollama_model else None,
            "avatar_url": avatar_url,
            "skills": selected_skills,
            "rules": selected_rules
        })

    return redirect(url_for("agents.list_agents"))

@agents_bp.route("/agents/upload-excel", methods=["POST"])
@admin_required
def upload_excel():
    file = request.files.get("excel_file")
    if file and file.filename != "":
        ext = os.path.splitext(file.filename)[1].lower()
        if ext in [".xlsx", ".xls", ".csv"]:
            safe_filename = f"agent_upload_{uuid.uuid4().hex[:12]}{ext}"
            upload_dir = os.path.join(current_app.root_path, "storage", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, safe_filename)
            file.save(file_path)

            agents_engine.import_agents_from_excel(file_path)

    return redirect(url_for("agents.list_agents"))

@agents_bp.route("/agents/<agent_id>/delete", methods=["POST"])
@admin_required
def delete_agent(agent_id):
    agent_repo.delete_agent(agent_id)
    return redirect(url_for("agents.list_agents"))
