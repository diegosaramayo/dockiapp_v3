from datetime import datetime

class TXTExporter:
    """
    Servicio de generación del archivo TXT formateado con las respuestas del formulario completado,
    incluyendo el contenido completo de declaraciones juradas, términos y condiciones y skills.
    """
    def export(self, form_data, responses_data):
        lines = []
        lines.append("==================================================")
        lines.append(f"FORMULARIO DIGITALIZADO: {form_data.get('name', 'Formulario')}")
        lines.append(f"Versión: {form_data.get('version', '0001 (17/08/2026)')}")
        lines.append(f"Fecha de Completado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        lines.append("==================================================\n")

        for step in form_data.get("steps", []):
            lines.append(f"--- {step.get('title', 'Sección')} ---")
            for field in step.get("fields", []):
                field_id = field.get("id")
                field_type = field.get("type")
                field_label = field.get("label", field.get("text", "Campo")).rstrip(":")

                if field_type == "input" or field_type == "date" or field_type == "select":
                    val = responses_data.get(field_id, "")
                    lines.append(f"  * {field_label} {val}")

                elif field_type == "address_verify":
                    is_correct = responses_data.get(f"{field_id}_correct")
                    new_addr = responses_data.get(f"{field_id}_new_address", "")
                    addr_val = field.get("address", "")
                    lines.append(f"  * {field_label}:")
                    lines.append(f"    - Dirección Registrada: {addr_val}")
                    lines.append(f"    - ¿Es Correcto?: {'Sí' if is_correct == 'yes' else 'No' if is_correct == 'no' else 'Sin especificar'}")
                    if is_correct == 'no' and new_addr:
                        lines.append(f"    - Nueva Dirección: {new_addr}")

                elif field_type == "complex_skill":
                    user_val = responses_data.get(field_id, "Sí")
                    content = field.get("content_text") or field.get("text", "")
                    lines.append(f"  * {field_label}: {user_val}.")
                    if content:
                        lines.append(f"    {content}\n")

                elif field_type == "check_options":
                    is_checked = responses_data.get(f"{field_id}_checked")
                    resp_str = "Sí" if is_checked == "yes" else "No" if is_checked == "no" else "Sin especificar"
                    content = field.get("text") or field.get("content_text", "")
                    lines.append(f"  * {field_label}: {resp_str}.")
                    if content:
                        lines.append(f"    {content}\n")

                elif field_type == "terms_box":
                    content = field.get("text", "")
                    user_val = responses_data.get(field_id, "Sí")
                    lines.append(f"  * {field_label}: {user_val}.")
                    if content:
                        lines.append(f"    {content}\n")

                elif field_type == "terms_header":
                    lines.append(f"  [SECCIÓN] {field_label}")

            lines.append("")

        lines.append("==================================================")
        lines.append("Estado de Aceptación: CONFIRMADO Y ACEPADO")
        lines.append("==================================================")

        return "\n".join(lines)
