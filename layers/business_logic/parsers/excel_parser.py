import openpyxl
import re

class ExcelParser:
    def parse(self, file_path):
        fields = []
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active

        row_idx = 1
        for row in sheet.iter_rows(values_only=True):
            non_empty = [str(val).strip() for val in row if val is not None and str(val).strip()]
            if not non_empty:
                continue

            row_text = " ".join(non_empty)
            if any(term in row_text.lower() for term in ["declaracion", "jurada", "terminos", "condiciones", "manifiesto"]):
                fields.append({
                    "id": f"excel_field_{row_idx}",
                    "type": "terms_box",
                    "text": row_text
                })
            elif len(non_empty) >= 2:
                label = non_empty[0]
                val = non_empty[1] if len(non_empty) > 1 else ""
                if not label.endswith(":"):
                    label += ":"

                fields.append({
                    "id": f"excel_field_{row_idx}",
                    "type": "input",
                    "label": label,
                    "placeholder": val if val else "XXXX",
                    "value": ""
                })
            else:
                label = non_empty[0]
                if not label.endswith(":"):
                    label += ":"
                fields.append({
                    "id": f"excel_field_{row_idx}",
                    "type": "input",
                    "label": label,
                    "placeholder": "XXXX",
                    "value": ""
                })
            row_idx += 1

        if not fields:
            fields.append({
                "id": "excel_default_1",
                "type": "input",
                "label": "Campo Extraído 1:",
                "placeholder": "XXXX",
                "value": ""
            })

        return fields
