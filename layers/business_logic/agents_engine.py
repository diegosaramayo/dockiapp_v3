import os
import openpyxl
import csv
from layers.data_storage.agent_repository import AgentRepository
from layers.data_storage.skill_repository import SkillRepository
from layers.data_storage.rule_repository import RuleRepository

class AgentsEngine:
    """
    Motor de coordinación de Agentes: vinculación con Skills, Rules e importación desde XLSX/CSV.
    """
    def __init__(self):
        self.agent_repo = AgentRepository()
        self.skill_repo = SkillRepository()
        self.rule_repo = RuleRepository()

    def import_agents_from_excel(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        imported_agents = []
        rows = []

        if ext in [".xlsx", ".xls"]:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            for r in sheet.iter_rows(values_only=True):
                clean_r = [str(val).strip() if val is not None else "" for val in r]
                if any(clean_r):
                    rows.append(clean_r)
        elif ext == ".csv":
            with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as f:
                reader = csv.reader(f)
                rows = [ [cell.strip() for cell in r] for r in reader if any(cell.strip() for cell in r) ]

        if not rows:
            return []

        headers = [h.lower() for h in rows[0]]
        name_idx = next((i for i, h in enumerate(headers) if "nombre" in h or "name" in h), 0)
        code_idx = next((i for i, h in enumerate(headers) if "codigo" in h or "code" in h), -1)
        role_idx = next((i for i, h in enumerate(headers) if "rol" in h or "role" in h), -1)
        model_idx = next((i for i, h in enumerate(headers) if "model" in h or "ollama" in h), -1)

        for row in rows[1:]:
            if not any(row):
                continue
            name_val = row[name_idx] if name_idx < len(row) and row[name_idx] else "Agente XLSX"
            code_val = row[code_idx] if code_idx != -1 and code_idx < len(row) and row[code_idx] else "AG-XLSX"
            role_val = row[role_idx] if role_idx != -1 and role_idx < len(row) and row[role_idx] else "Asistente Digital"
            model_val = row[model_idx] if model_idx != -1 and model_idx < len(row) and row[model_idx] else None

            agent_data = {
                "code": code_val,
                "name": name_val,
                "role": role_val,
                "ollama_model": model_val,
                "avatar_url": None,
                "skills": [],
                "rules": []
            }
            saved = self.agent_repo.save_agent(agent_data)
            imported_agents.append(saved)

        return imported_agents

    def get_agent_full_profile(self, agent_id):
        agent = self.agent_repo.get_agent_by_id(agent_id)
        if not agent:
            return None

        assigned_skills = []
        for s_id in agent.get("skills", []):
            skill = self.skill_repo.get_skill_by_id(s_id)
            if skill:
                assigned_skills.append(skill)

        assigned_rules = []
        for r_id in agent.get("rules", []):
            rule = self.rule_repo.get_rule_by_id(r_id)
            if rule:
                assigned_rules.append(rule)

        agent_copy = dict(agent)
        agent_copy["skills_details"] = assigned_skills
        agent_copy["rules_details"] = assigned_rules
        return agent_copy
