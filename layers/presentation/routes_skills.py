import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from layers.data_storage.skill_repository import SkillRepository
from layers.data_storage.config_repository import ConfigRepository
from layers.business_logic.skills_engine import SkillsEngine
from layers.business_logic.parsers.image_parser import ImageParser
from layers.business_logic.auth_service import admin_required

skills_bp = Blueprint("skills", __name__)
skill_repo = SkillRepository()
config_repo = ConfigRepository()
skills_engine = SkillsEngine()
image_parser = ImageParser()

@skills_bp.route("/skills")
@admin_required
def list_skills():
    config = config_repo.get_config()
    skills = skill_repo.list_skills()
    return render_template("skills.html", skills=skills, config=config)

@skills_bp.route("/skills/create", methods=["POST"])
@admin_required
def create_skill():
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip()
    desc = request.form.get("description", "").strip()
    category = request.form.get("category", "General").strip()

    if name:
        image_file = request.files.get("image")
        image_url = None

        if image_file and image_file.filename != "":
            upload_dir = os.path.join(current_app.static_folder, "uploads", "images")
            saved_name = image_parser.save_image(image_file, upload_dir)
            if saved_name:
                image_url = f"/static/uploads/images/{saved_name}"

        skill_repo.save_skill({
            "code": code or "SK-NEW",
            "name": name,
            "description": desc,
            "category": category,
            "image_url": image_url
        })

    return redirect(url_for("skills.list_skills"))

@skills_bp.route("/skills/upload-excel", methods=["POST"])
@admin_required
def upload_excel():
    file = request.files.get("excel_file")
    if file and file.filename != "":
        ext = os.path.splitext(file.filename)[1].lower()
        if ext in [".xlsx", ".xls", ".csv"]:
            safe_filename = f"skill_upload_{uuid.uuid4().hex[:12]}{ext}"
            upload_dir = os.path.join(current_app.root_path, "storage", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, safe_filename)
            file.save(file_path)

            skills_engine.import_skills_from_excel(file_path)

    return redirect(url_for("skills.list_skills"))

@skills_bp.route("/skills/<skill_id>/delete", methods=["POST"])
@admin_required
def delete_skill(skill_id):
    skill_repo.delete_skill(skill_id)
    return redirect(url_for("skills.list_skills"))
