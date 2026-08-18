import os
import json
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
AGENTS_DIR = os.path.join(STORAGE_DIR, "agents")

class AgentRepository:
    def __init__(self):
        os.makedirs(AGENTS_DIR, exist_ok=True)
        self._ensure_sample_agents()

    def _ensure_sample_agents(self):
        if len(self.list_agents()) == 0:
            sample_agents = [
                {
                    "id": "agent_fatca_auditor",
                    "code": "AG-001",
                    "name": "Agente Auditor FATCA",
                    "role": "Supervisión de Cumplimiento Fiscal",
                    "avatar_url": None,
                    "skills": ["skill_fatca_check", "skill_cuit_verify"],
                    "rules": ["rule_fatca_us_person"],
                    "created_at": "2026-08-14"
                },
                {
                    "id": "agent_customer_verify",
                    "code": "AG-002",
                    "name": "Agente Validador Cliente",
                    "role": "Verificación de Domicilio y Datos",
                    "avatar_url": None,
                    "skills": ["skill_address_norm", "skill_cuit_verify"],
                    "rules": ["rule_address_change"],
                    "created_at": "2026-08-14"
                }
            ]
            for a in sample_agents:
                self.save_agent(a)

    def list_agents(self):
        agents = []
        for file_name in os.listdir(AGENTS_DIR):
            if file_name.endswith(".json"):
                file_path = os.path.join(AGENTS_DIR, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        agents.append(json.load(f))
                except Exception:
                    continue
        agents.sort(key=lambda x: x.get("name", ""))
        return agents

    def get_agent_by_id(self, agent_id):
        file_path = os.path.join(AGENTS_DIR, f"{agent_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def save_agent(self, agent_data):
        if "id" not in agent_data or not agent_data["id"]:
            agent_data["id"] = f"agent_{uuid.uuid4().hex[:8]}"
        file_path = os.path.join(AGENTS_DIR, f"{agent_data['id']}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(agent_data, f, indent=2, ensure_ascii=False)
        return agent_data

    def delete_agent(self, agent_id):
        file_path = os.path.join(AGENTS_DIR, f"{agent_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
