import os
from datetime import datetime
from layers.business_logic.parsers.excel_parser import ExcelParser
from layers.business_logic.parsers.csv_parser import CSVParser
from layers.business_logic.parsers.docx_parser import DocxParser
from layers.business_logic.parsers.pdf_parser import PDFParser
from layers.data_storage.form_repository import FormRepository

class DigitizerService:
    def __init__(self):
        self.repository = FormRepository()
        self.excel_parser = ExcelParser()
        self.csv_parser = CSVParser()
        self.docx_parser = DocxParser()
        self.pdf_parser = PDFParser()

    def parse_file_fields(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()

        if ext in [".xlsx", ".xls"]:
            raw_fields = self.excel_parser.parse(file_path)
        elif ext == ".csv":
            raw_fields = self.csv_parser.parse(file_path)
        elif ext in [".docx", ".doc"]:
            raw_fields = self.docx_parser.parse(file_path)
        elif ext == ".pdf":
            raw_fields = self.pdf_parser.parse(file_path)
        else:
            raise ValueError(f"Formato de archivo no soportado: {ext}")

        from layers.business_logic.rules_engine import RulesEngine
        from layers.business_logic.skills_engine import SkillsEngine
        rules_engine = RulesEngine()
        skills_engine = SkillsEngine()

        # 1. Aplicar transformaciones de reglas de negocio
        transformed_fields = rules_engine.apply_transformations_to_fields(raw_fields)

        # 2. Aplicar transformaciones complejas de Skills
        transformed_fields = skills_engine.apply_skill_transformations(transformed_fields)

        # 3. Clasificación defensiva de campos de fecha
        for field in transformed_fields:
            if isinstance(field, dict):
                lbl = str(field.get("label") or field.get("text") or "").lower()
                if "fecha" in lbl or "date" in lbl:
                    field["type"] = "date"

        return transformed_fields

    def save_final_digitized_form(self, form_name, form_version, raw_fields):
        steps = []
        step_number = 1
        current_step_fields = []
        current_weight = 0

        fields_list = raw_fields if isinstance(raw_fields, list) else []

        for field in fields_list:
            if not isinstance(field, dict):
                continue

            weight = 2 if field.get("type") in ["terms_box", "address_verify", "complex_skill"] else 1
            
            if current_weight + weight > 4 and current_step_fields:
                steps.append({
                    "step_number": step_number,
                    "title": f"Sección {step_number}",
                    "fields": current_step_fields
                })
                step_number += 1
                current_step_fields = []
                current_weight = 0

            current_step_fields.append(field)
            current_weight += weight

        if current_step_fields:
            steps.append({
                "step_number": step_number,
                "title": f"Sección {step_number}",
                "fields": current_step_fields
            })

        clean_name = str(form_name or "Nuevo Formulario").strip()
        clean_version = str(form_version or "01.0001").strip()
        code_prefix = clean_version.split()[0] if clean_version else "01.0001"

        if clean_name.startswith(code_prefix):
            full_form_name = clean_name
        else:
            full_form_name = f"{code_prefix} {clean_name}".strip()

        date_str = datetime.now().strftime("%d/%m/%Y")
        version_str = f"{clean_version} ({date_str})" if "(" not in clean_version else clean_version

        form_id = f"form_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        form_data = {
            "id": form_id,
            "code": code_prefix,
            "name": full_form_name,
            "short_name": clean_name,
            "version": version_str,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "steps": steps
        }

        saved_form = self.repository.save_form(form_data)
        return saved_form
