import os
import json
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
FORMS_DIR = os.path.join(STORAGE_DIR, "forms")
UPLOADS_DIR = os.path.join(STORAGE_DIR, "uploads")

class FormRepository:
    def __init__(self):
        os.makedirs(FORMS_DIR, exist_ok=True)
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        self._ensure_sample_forms()
        self._clean_legacy_address_fields()

    def _ensure_sample_forms(self):
        forms = self.list_forms()
        if len(forms) == 0:
            fatca_form = {
                "id": "fatca_06_0002",
                "code": "06.0002",
                "name": "06.0002 DDJJ FATCA",
                "short_name": "DDJJ FATCA",
                "version": "06.0005 (13/08/2026)",
                "created_at": "2026-08-13",
                "steps": [
                    {
                        "step_number": 1,
                        "title": "Datos del Titular",
                        "fields": [
                            {
                                "id": "num_cliente",
                                "type": "input",
                                "label": "Número de Cliente:",
                                "placeholder": "XXXX",
                                "value": ""
                            },
                            {
                                "id": "direccion_titular",
                                "type": "input",
                                "label": "Domicilio / Dirección del Titular:",
                                "placeholder": "Ingrese Domicilio Completo",
                                "value": ""
                            }
                        ]
                    },
                    {
                        "step_number": 2,
                        "title": "Declaración Jurada FATCA",
                        "fields": [
                            {
                                "id": "header_fatca",
                                "type": "terms_header",
                                "text": "Declaración Jurada sobre la condición FATCA:"
                            },
                            {
                                "id": "intro_fatca",
                                "type": "terms_box",
                                "text": "En relación con las disposiciones de la ley de Foreign Account Tax Compliance Act (\"FATCA\") manifiesto, con carácter de declaración jurada, que:"
                            },
                            {
                                "id": "us_person_check",
                                "type": "check_options",
                                "label": "me encuentro encuadrado bajo la figura de U.S. Person.",
                                "is_checked": None
                            },
                            {
                                "id": "legal_terms_fatca",
                                "type": "terms_box",
                                "text": "Al respecto, autorizo a Banco Patagonia S.A. a brindar toda información concerniente a mi persona en el caso que así lo requieran las autoridades, locales o extranjeras, bajo la normativa vigente. A tal efecto, será considerada como normativa vigente, a título de ejemplo y sin ser esta mención taxativa, toda Comunicación emanada por el Banco Central de la República Argentina, Resoluciones de la Comisión Nacional de Valores y Decretos y Leyes (Incluyendo la Ley FATCA).\n\nEn el caso de marcar la opción \"Sí\", el cliente deberá firmar el formulario 08.0035 \"Declaración Jurada U.S. Person - Persona Física\", marcando la opción \"me encuentro encuadrado bajo la figura de U.S. Person\"."
                            }
                        ]
                    }
                ]
            }

            nuevo_prod_form = {
                "id": "nuevo_prod_02_0001",
                "code": "02.0001",
                "name": "02.0001 NUEVO PRODUCTO",
                "short_name": "NUEVO PRODUCTO",
                "version": "02.0001 (10/01/2026)",
                "created_at": "2026-08-13",
                "steps": [
                    {
                        "step_number": 1,
                        "title": "Solicitud de Nuevo Producto",
                        "fields": [
                            {
                                "id": "nombre_solicitante",
                                "type": "input",
                                "label": "Nombre Completo del Solicitante:",
                                "placeholder": "Ingrese Nombre y Apellido",
                                "value": ""
                            },
                            {
                                "id": "cuit_cuil",
                                "type": "input",
                                "label": "CUIT / CUIL:",
                                "placeholder": "20-XXXXXXXX-X",
                                "value": ""
                            },
                            {
                                "id": "domicilio_comercial",
                                "type": "input",
                                "label": "Domicilio Comercial:",
                                "placeholder": "Ingrese Domicilio Comercial",
                                "value": ""
                            }
                        ]
                    }
                ]
            }

            self.save_form(fatca_form)
            self.save_form(nuevo_prod_form)

    def _clean_legacy_address_fields(self):
        for file_name in os.listdir(FORMS_DIR):
            if file_name.endswith(".json"):
                file_path = os.path.join(FORMS_DIR, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    modified = False
                    for step in data.get("steps", []):
                        for field in step.get("fields", []):
                            if field.get("type") == "address_verify":
                                field["type"] = "input"
                                field["placeholder"] = "Ingrese Domicilio"
                                field.pop("address", None)
                                field.pop("prompt", None)
                                field.pop("sub_label", None)
                                modified = True

                    if modified:
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                except Exception:
                    continue

    def list_forms(self):
        forms = []
        for file_name in os.listdir(FORMS_DIR):
            if file_name.endswith(".json"):
                file_path = os.path.join(FORMS_DIR, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        forms.append(data)
                except Exception:
                    continue
        forms.sort(key=lambda x: x.get("name", ""))
        return forms

    def get_all_unique_fields(self):
        """ Obtiene la lista de todos los campos digitalizados previamente en otros formularios """
        forms = self.list_forms()
        unique_fields = []
        seen_labels = set()

        for form in forms:
            for step in form.get("steps", []):
                for field in step.get("fields", []):
                    label = field.get("label") or field.get("text") or "Campo"
                    label_key = label.strip().lower()
                    if label_key not in seen_labels:
                        seen_labels.add(label_key)
                        unique_fields.append({
                            "id": f"field_ex_{len(unique_fields)+1}_{uuid.uuid4().hex[:4]}",
                            "label": label,
                            "type": field.get("type", "input"),
                            "placeholder": field.get("placeholder", "XXXX"),
                            "options": field.get("options", []),
                            "content_text": field.get("content_text") or field.get("text", ""),
                            "value": ""
                        })
        return unique_fields

    def get_form_by_id(self, form_id):
        file_path = os.path.join(FORMS_DIR, f"{form_id}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def save_form(self, form_data):
        if "id" not in form_data or not form_data["id"]:
            form_data["id"] = f"form_{uuid.uuid4().hex[:8]}"
        file_path = os.path.join(FORMS_DIR, f"{form_data['id']}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(form_data, f, indent=2, ensure_ascii=False)
        return form_data

    def delete_form(self, form_id):
        file_path = os.path.join(FORMS_DIR, f"{form_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
