import os
import json
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
RULES_DIR = os.path.join(STORAGE_DIR, "rules")

class RuleRepository:
    def __init__(self):
        os.makedirs(RULES_DIR, exist_ok=True)
        self._ensure_sample_rules()

    def _ensure_sample_rules(self):
        if len(self.list_rules()) == 0:
            sample_rules = [
                {
                    "id": "rule_fatca_us_person",
                    "code": "RL-001",
                    "name": "Regla Requisito Formulario U.S. Person",
                    "target_field": "us_person_check_checked",
                    "condition": "equals",
                    "trigger_value": "yes",
                    "action": "require_doc",
                    "message": "Atención: Debe firmar el formulario 08.0035 Declaración Jurada U.S. Person.",
                    "image_url": None,
                    "created_at": "2026-08-14"
                },
                {
                    "id": "rule_address_change",
                    "code": "RL-002",
                    "name": "Regla Actualización Domicilio Comercial",
                    "target_field": "direccion_titular_correct",
                    "condition": "equals",
                    "trigger_value": "no",
                    "action": "require_field",
                    "message": "Se requiere ingresar el comprobante del nuevo domicilio declarado.",
                    "image_url": None,
                    "created_at": "2026-08-14"
                }
            ]
            for r in sample_rules:
                self.save_rule(r)

    def list_rules(self):
        rules = []
        for file_name in os.listdir(RULES_DIR):
            if file_name.endswith(".json"):
                file_path = os.path.join(RULES_DIR, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        rules.append(json.load(f))
                except Exception:
                    continue
        rules.sort(key=lambda x: x.get("name", ""))
        return rules

    def get_rule_by_id(self, rule_id):
        file_path = os.path.join(RULES_DIR, f"{rule_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def save_rule(self, rule_data):
        if "id" not in rule_data or not rule_data["id"]:
            rule_data["id"] = f"rule_{uuid.uuid4().hex[:8]}"
        file_path = os.path.join(RULES_DIR, f"{rule_data['id']}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(rule_data, f, indent=2, ensure_ascii=False)
        return rule_data

    def delete_rule(self, rule_id):
        file_path = os.path.join(RULES_DIR, f"{rule_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
