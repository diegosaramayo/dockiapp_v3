import os
import json
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
SKILLS_DIR = os.path.join(STORAGE_DIR, "skills")

class SkillRepository:
    def __init__(self):
        os.makedirs(SKILLS_DIR, exist_ok=True)
        self._ensure_sample_skills()

    def _ensure_sample_skills(self):
        if len(self.list_skills()) == 0:
            sample_skills = [
                {
                    "id": "skill_cuit_verify",
                    "code": "SK-001",
                    "name": "Validación de CUIT / CUIL",
                    "description": "Verifica que el número de CUIT/CUIL cumpla con la clave de control y longitud exacta.",
                    "category": "Validación Data",
                    "image_url": None,
                    "created_at": "2026-08-14"
                },
                {
                    "id": "skill_address_norm",
                    "code": "SK-002",
                    "name": "Normalización de Domicilio",
                    "description": "Formatea y valida las calles, localidades y códigos postales registrados.",
                    "category": "Geolocalización",
                    "image_url": None,
                    "created_at": "2026-08-14"
                },
                {
                    "id": "skill_fatca_check",
                    "code": "SK-003",
                    "name": "Verificación Ley FATCA",
                    "description": "Analiza las declaraciones juradas para clasificar la condición U.S. Person.",
                    "category": "Cumplimiento Legal",
                    "image_url": None,
                    "created_at": "2026-08-14"
                }
            ]
            for s in sample_skills:
                self.save_skill(s)

    def list_skills(self):
        skills = []
        for file_name in os.listdir(SKILLS_DIR):
            if file_name.endswith(".json"):
                file_path = os.path.join(SKILLS_DIR, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        skills.append(json.load(f))
                except Exception:
                    continue
        skills.sort(key=lambda x: x.get("name", ""))
        return skills

    def get_skill_by_id(self, skill_id):
        file_path = os.path.join(SKILLS_DIR, f"{skill_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def save_skill(self, skill_data):
        if "id" not in skill_data or not skill_data["id"]:
            skill_data["id"] = f"skill_{uuid.uuid4().hex[:8]}"
        file_path = os.path.join(SKILLS_DIR, f"{skill_data['id']}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(skill_data, f, indent=2, ensure_ascii=False)
        return skill_data

    def delete_skill(self, skill_id):
        file_path = os.path.join(SKILLS_DIR, f"{skill_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
