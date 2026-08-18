import os
import csv
import re
import openpyxl
import unicodedata
import uuid
from layers.data_storage.skill_repository import SkillRepository

def normalize_text(text):
    if not text:
        return ""
    text = str(text).lower()
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def clean_cell_text(text):
    if not text:
        return ""
    text = str(text).strip()
    text = re.sub(r'^["“\'\s]+|["”\'\s]+$', '', text)
    return text.strip()

def read_csv_smart_encoding(file_path):
    encodings = ['utf-8-sig', 'utf-8', 'cp1252', 'latin1', 'iso-8859-1']
    delimiters = [';', ',']

    for enc in encodings:
        for delim in delimiters:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    reader = csv.reader(f, delimiter=delim)
                    rows = [[cell.strip() for cell in r] for r in reader if any(cell.strip() for cell in r)]
                    if len(rows) > 0 and len(rows[0]) >= 1:
                        sample_str = "".join("".join(r) for r in rows[:10])
                        if "" not in sample_str:
                            return rows
            except (UnicodeDecodeError, Exception):
                continue

    for enc in encodings:
        for delim in delimiters:
            try:
                with open(file_path, "r", encoding=enc, errors="replace") as f:
                    reader = csv.reader(f, delimiter=delim)
                    rows = [[cell.strip() for cell in r] for r in reader if any(cell.strip() for cell in r)]
                    if len(rows) > 0:
                        return rows
            except Exception:
                continue

    return []

class SkillsEngine:
    """
    Motor de gestión e importación de Skills desde archivos XLSX y CSV con soporte para transformaciones complejas de campos:
    - "Si el título del campo dice:"
    - "Al digitalizarlo, pasar el título a:"
    - "Al digitalizarlo, se debe agregar el contenido:"
    - "Al digitalizarlo, se debe elegir las siguientes opciones de una lista:"
    """
    def __init__(self):
        self.repository = SkillRepository()

    def import_skills_from_excel(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        imported_skills = []
        rows = []

        if ext in [".xlsx", ".xls"]:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            for r in sheet.iter_rows(values_only=True):
                clean_r = [str(val).strip() if val is not None else "" for val in r]
                if any(clean_r):
                    rows.append(clean_r)
        elif ext == ".csv":
            rows = read_csv_smart_encoding(file_path)

        if not rows:
            return []

        col_a_first = rows[0][0] if len(rows[0]) > 0 else ""
        col_b_first = rows[0][1] if len(rows[0]) > 1 else ""
        col_c_first = rows[0][2] if len(rows[0]) > 2 else ""
        col_d_first = rows[0][3] if len(rows[0]) > 3 else ""

        col_a_norm = normalize_text(col_a_first)
        col_b_norm = normalize_text(col_b_first)
        col_c_norm = normalize_text(col_c_first)
        col_d_norm = normalize_text(col_d_first)

        # REGLA DE MAPEO COMPLEJO DE SKILLS CON TEXTO Y OPCIONES:
        # Col A: "Si el título del campo dice:"
        # Col B: "Al digitalizarlo, pasar el título a:"
        # Col C: "Al digitalizarlo, se debe agregar el contenido:"
        # Col D: "Al digitalizarlo, se debe elegir las siguientes opciones de una lista:"
        if ("si el titulo" in col_a_norm or "si el campo" in col_a_norm) and ("pasar el titulo" in col_b_norm or "contenido" in col_c_norm or "opciones" in col_d_norm):
            current_target_title = ""
            current_content_text = ""
            keywords = []
            options_list = []

            for r in rows[1:]:
                if not any(r):
                    continue
                orig_kw = clean_cell_text(r[0]) if len(r) > 0 else ""
                new_title = clean_cell_text(r[1]) if len(r) > 1 else ""
                content_text = clean_cell_text(r[2]) if len(r) > 2 else ""
                opt_val = clean_cell_text(r[3]) if len(r) > 3 else ""

                if new_title:
                    current_target_title = new_title
                if content_text:
                    current_content_text = content_text

                if orig_kw and orig_kw not in keywords:
                    keywords.append(orig_kw)

                if opt_val and opt_val not in options_list:
                    options_list.append(opt_val)

            skill_id = f"skill_complex_{uuid.uuid4().hex[:6]}"
            skill_code = f"SK-CMP-{uuid.uuid4().hex[:4].upper()}"
            skill_data = {
                "id": skill_id,
                "code": skill_code,
                "name": f"Skill Transformación: {current_target_title or 'Compleja'}",
                "type": "complex_skill",
                "target_keywords": keywords,
                "new_title": current_target_title,
                "content_text": current_content_text,
                "options": options_list,
                "description": f"Añade contenido explicativo y selector ({len(options_list)} opciones) al digitalizar.",
                "category": "Transformación de Campos"
            }
            saved = self.repository.save_skill(skill_data)
            imported_skills.append(saved)

            return imported_skills

        # Si es un archivo XLSX de lista de Skills estándar con encabezados
        headers = [h.lower() for h in rows[0]]
        name_idx = next((i for i, h in enumerate(headers) if "nombre" in h or "name" in h or "skill" in h), 0)
        code_idx = next((i for i, h in enumerate(headers) if "codigo" in h or "code" in h), -1)
        desc_idx = next((i for i, h in enumerate(headers) if "desc" in h), -1)
        cat_idx = next((i for i, h in enumerate(headers) if "cat" in h), -1)

        for row in rows[1:]:
            if not any(row):
                continue
            name_val = str(row[name_idx]).strip() if name_idx < len(row) and row[name_idx] is not None else "Skill Excel"
            code_val = str(row[code_idx]).strip() if code_idx != -1 and code_idx < len(row) and row[code_idx] is not None else f"SK-{uuid.uuid4().hex[:4].upper()}"
            desc_val = str(row[desc_idx]).strip() if desc_idx != -1 and desc_idx < len(row) and row[desc_idx] is not None else "Skill importada desde XLSX."
            cat_val = str(row[cat_idx]).strip() if cat_idx != -1 and cat_idx < len(row) and row[cat_idx] is not None else "General"

            skill_data = {
                "id": f"skill_{uuid.uuid4().hex[:8]}",
                "code": code_val,
                "name": name_val,
                "description": desc_val,
                "category": cat_val,
                "image_url": None
            }
            saved = self.repository.save_skill(skill_data)
            imported_skills.append(saved)

        return imported_skills

    def apply_skill_transformations(self, fields):
        """
        Aplica las transformaciones de Skills a los campos de un formulario:
        Reemplaza títulos, añade textos legales de contenido y selectores de opciones Sí/No.
        """
        all_skills = self.repository.list_skills()
        complex_skills = [s for s in all_skills if s.get("type") == "complex_skill"]

        if not complex_skills:
            return fields

        processed_fields = []
        for field in fields:
            field_copy = dict(field)
            field_label_norm = normalize_text(field_copy.get("label", "") or field_copy.get("text", "") or field_copy.get("description", ""))

            for skill in complex_skills:
                keywords = skill.get("target_keywords", [])
                if any(normalize_text(kw) in field_label_norm for kw in keywords if kw):
                    field_copy["type"] = "complex_skill"
                    if skill.get("new_title"):
                        field_copy["label"] = skill.get("new_title")
                    if skill.get("content_text"):
                        field_copy["content_text"] = skill.get("content_text")
                    if skill.get("options"):
                        field_copy["options"] = skill.get("options")
                    break

            processed_fields.append(field_copy)

        return processed_fields
