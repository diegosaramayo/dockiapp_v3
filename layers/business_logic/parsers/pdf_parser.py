import pypdf

class PDFParser:
    def parse(self, file_path):
        fields = []
        try:
            reader = pypdf.PdfReader(file_path)
            field_idx = 1
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

            lines = [line.strip() for line in full_text.split("\n") if line.strip()]
            for line in lines:
                if any(kw in line.lower() for kw in ["declaración", "declaracion", "jurada", "terminos"]):
                    if len(line) < 60:
                        fields.append({
                            "id": f"pdf_field_{field_idx}",
                            "type": "terms_header",
                            "text": line if line.endswith(":") else f"{line}:"
                        })
                    else:
                        fields.append({
                            "id": f"pdf_field_{field_idx}",
                            "type": "terms_box",
                            "text": line
                        })
                elif ":" in line and len(line) < 100:
                    parts = line.split(":", 1)
                    label = parts[0].strip() + ":"
                    val = parts[1].strip()
                    fields.append({
                        "id": f"pdf_field_{field_idx}",
                        "type": "input",
                        "label": label,
                        "placeholder": val if val else "XXXX",
                        "value": ""
                    })
                elif len(line) > 120:
                    fields.append({
                        "id": f"pdf_field_{field_idx}",
                        "type": "terms_box",
                        "text": line
                    })
                else:
                    fields.append({
                        "id": f"pdf_field_{field_idx}",
                        "type": "input",
                        "label": line if line.endswith(":") else f"{line}:",
                        "placeholder": "XXXX",
                        "value": ""
                    })
                field_idx += 1
        except Exception:
            pass

        if not fields:
            fields.append({
                "id": "pdf_default_1",
                "type": "input",
                "label": "Campo PDF Extraído 1:",
                "placeholder": "XXXX",
                "value": ""
            })
        return fields
