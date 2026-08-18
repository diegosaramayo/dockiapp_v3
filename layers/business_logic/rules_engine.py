import os
import csv
import re
import openpyxl
import unicodedata
import uuid
from layers.data_storage.rule_repository import RuleRepository

def normalize_text(text):
    """ Normaliza texto para comparaciones (pasa a minúsculas y remueve tildes solo para buscar coincidencias) """
    if not text:
        return ""
    text = str(text).lower()
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def clean_cell_text(text):
    """ Limpia comillas dobles y espacios sobrantes en texto de celdas """
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

class RulesEngine:
    def __init__(self):
        self.repository = RuleRepository()

    def import_rules_from_excel(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        imported_rules = []
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

        col_a_norm = normalize_text(col_a_first)
        col_b_norm = normalize_text(col_b_first)

        # Regla Mapeo Columnas Explícitas: Header A "Si el título..." / Header B "Al digitalizarlo..."
        if ("si el titulo" in col_a_norm or "si el campo" in col_a_norm or "si el titulo del campo dice" in col_a_norm) and ("pasar el titulo" in col_b_norm or "al digitalizarlo" in col_b_norm or "pasar el titulo a" in col_b_norm):
            current_target_label = ""
            label_groups = {}

            for r in rows[1:]:
                if not any(r):
                    continue
                orig_kw = clean_cell_text(r[0]) if len(r) > 0 else ""
                new_lbl = clean_cell_text(r[1]) if len(r) > 1 else ""

                if new_lbl:
                    current_target_label = new_lbl

                if orig_kw and current_target_label:
                    if current_target_label not in label_groups:
                        label_groups[current_target_label] = []
                    if orig_kw not in label_groups[current_target_label]:
                        label_groups[current_target_label].append(orig_kw)

            for new_label, keywords in label_groups.items():
                rule_id = f"rule_map_{uuid.uuid4().hex[:6]}"
                rule_code = f"RL-MAP-{uuid.uuid4().hex[:4].upper()}"
                rule_data = {
                    "id": rule_id,
                    "code": rule_code,
                    "name": f"Regla Mapeo Título: {new_label}",
                    "type": "rename_label",
                    "target_keywords": keywords,
                    "new_label": new_label,
                    "action": "rename_label",
                    "message": f"Al digitalizar, título transformado a '{new_label}'."
                }
                saved = self.repository.save_rule(rule_data)
                imported_rules.append(saved)

            return imported_rules

        keywords = []
        matches = re.findall(r'["“«\']([^"”»\']+)["”»\']', col_a_first)
        if matches:
            keywords = [m.strip() for m in matches if m.strip()]

        col_a_lower = col_a_first.lower()

        if "cambiar el título" in col_a_lower or "cambiar el titulo" in col_a_lower or "renombrar" in col_a_lower or ("solicita" in col_a_lower and not ("elegir" in col_a_lower or "selector" in col_a_lower)):
            new_label = clean_cell_text(col_b_first) if col_b_first else (clean_cell_text(rows[1][1]) if len(rows) > 1 and len(rows[1]) > 1 else "Nombre Completo")
            
            rule_id = f"rule_rename_{uuid.uuid4().hex[:6]}"
            rule_code = f"RL-REN-{uuid.uuid4().hex[:4].upper()}"
            rule_data = {
                "id": rule_id,
                "code": rule_code,
                "name": f"Regla Renombrar Campo ({new_label})",
                "type": "rename_label",
                "target_keywords": keywords if keywords else ["nombre completo", "nombre y apellido"],
                "new_label": new_label,
                "action": "rename_label",
                "message": f"Título de campo renombrado automáticamente a '{new_label}'."
            }
            saved = self.repository.save_rule(rule_data)
            imported_rules.append(saved)
            return imported_rules

        if "contiene" in col_a_lower or "elegir" in col_a_lower or "selector" in col_a_lower or len(rows) > 3:
            options_list = []
            for r in rows:
                if len(r) >= 2 and r[1].strip():
                    val = clean_cell_text(r[1])
                    if val.lower() not in ["lista", "opciones"] and val not in options_list:
                        options_list.append(val)

            if options_list and options_list[0].lower() in ["país", "pais"]:
                options_list.pop(0)

            if not keywords:
                if "país" in col_a_lower or "pais" in col_a_lower:
                    keywords.extend(["país", "pais", "país de nacimiento", "lugar de nacimiento", "país del titular"])

            rule_id = f"rule_select_{uuid.uuid4().hex[:6]}"
            rule_code = f"RL-SEL-{uuid.uuid4().hex[:4].upper()}"
            rule_name = "Regla Selector de Países" if any("pais" in k.lower() or "país" in k.lower() for k in keywords) else "Regla Selector desde Archivo"

            rule_data = {
                "id": rule_id,
                "code": rule_code,
                "name": rule_name,
                "type": "transform_to_select",
                "target_keywords": keywords if keywords else ["país", "pais"],
                "options": options_list,
                "action": "transform_to_select",
                "message": f"Campo transformado a selector desplegable con {len(options_list)} opciones."
            }
            saved = self.repository.save_rule(rule_data)
            imported_rules.append(saved)
            return imported_rules

        headers = [h.lower() for h in rows[0]]
        name_idx = next((i for i, h in enumerate(headers) if "nombre" in h or "name" in h), 0)
        code_idx = next((i for i, h in enumerate(headers) if "codigo" in h or "code" in h), -1)
        field_idx = next((i for i, h in enumerate(headers) if "campo" in h or "field" in h), -1)
        cond_idx = next((i for i, h in enumerate(headers) if "cond" in h), -1)
        val_idx = next((i for i, h in enumerate(headers) if "valor" in h or "val" in h), -1)
        action_idx = next((i for i, h in enumerate(headers) if "acc" in h or "action" in h), -1)
        msg_idx = next((i for i, h in enumerate(headers) if "mensa" in h or "msg" in h), -1)

        for row in rows[1:]:
            if not any(row):
                continue
            name_val = row[name_idx] if name_idx < len(row) and row[name_idx] else "Regla Importada"
            code_val = row[code_idx] if code_idx != -1 and code_idx < len(row) and row[code_idx] else f"RL-{uuid.uuid4().hex[:4].upper()}"
            field_val = row[field_idx] if field_idx != -1 and field_idx < len(row) and row[field_idx] else "campo"
            cond_val = row[cond_idx] if cond_idx != -1 and cond_idx < len(row) and row[cond_idx] else "equals"
            trig_val = row[val_idx] if val_idx != -1 and val_idx < len(row) and row[val_idx] else "yes"
            act_val = row[action_idx] if action_idx != -1 and action_idx < len(row) and row[action_idx] else "require_doc"
            msg_val = row[msg_idx] if msg_idx != -1 and msg_idx < len(row) and row[msg_idx] else "Regla activada."

            rule_data = {
                "id": f"rule_{uuid.uuid4().hex[:8]}",
                "code": code_val,
                "name": name_val,
                "target_field": field_val,
                "condition": cond_val,
                "trigger_value": trig_val,
                "action": act_val,
                "message": msg_val,
                "image_url": None
            }
            saved = self.repository.save_rule(rule_data)
            imported_rules.append(saved)

        return imported_rules

    def apply_transformations_to_fields(self, fields):
        """
        Aplica reglas de transformación a los campos de un formulario:
        1. Renombra etiquetas de campos según reglas 'rename_label'.
        2. Convierte campos a selecciones desplegables según reglas 'transform_to_select'.
        3. Convierte universalmente a 'date' CUALQUIER campo que contenga la palabra 'Fecha' en su título o descripción.
        """
        all_rules = self.repository.list_rules()

        processed_fields = []
        for field in fields:
            field_copy = dict(field)
            field_label_norm = normalize_text(field_copy.get("label", "") or field_copy.get("text", "") or field_copy.get("description", ""))

            # 1. Aplicar renombrado de etiquetas
            if all_rules:
                for rule in all_rules:
                    if rule.get("type") == "rename_label" or rule.get("action") == "rename_label":
                        keywords = rule.get("target_keywords", [])
                        new_label = rule.get("new_label")
                        if new_label and any(normalize_text(kw) in field_label_norm for kw in keywords if kw):
                            field_copy["label"] = new_label
                            field_label_norm = normalize_text(new_label)

            # 2. Aplicar transformación a selector desplegable
            if all_rules:
                for rule in all_rules:
                    if rule.get("type") == "transform_to_select" or rule.get("action") == "transform_to_select":
                        keywords = rule.get("target_keywords", [])
                        options = rule.get("options", [])
                        if any(normalize_text(kw) in field_label_norm for kw in keywords if kw):
                            field_copy["type"] = "select"
                            field_copy["options"] = options
                            break

            # 3. Regla universal: Si cualquier título o descripción contiene la palabra 'Fecha' o 'date'
            if "fecha" in field_label_norm or "date" in field_label_norm:
                field_copy["type"] = "date"

            processed_fields.append(field_copy)

        return processed_fields

    def evaluate_rules(self, form_responses):
        active_alerts = []
        all_rules = self.repository.list_rules()

        for rule in all_rules:
            target_field = rule.get("target_field")
            trigger_val = str(rule.get("trigger_value", "")).lower()
            actual_val = str(form_responses.get(target_field, "")).lower()

            if target_field and actual_val:
                condition = rule.get("condition", "equals")
                triggered = False
                if condition == "equals" and actual_val == trigger_val:
                    triggered = True
                elif condition == "contains" and trigger_val in actual_val:
                    triggered = True
                elif condition == "not_empty" and actual_val:
                    triggered = True

                if triggered:
                    active_alerts.append({
                        "rule_id": rule.get("id"),
                        "rule_name": rule.get("name"),
                        "message": rule.get("message"),
                        "action": rule.get("action")
                    })

        return active_alerts
