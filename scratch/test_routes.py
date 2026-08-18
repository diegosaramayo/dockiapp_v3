import sys
import os
import io

docki_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if docki_dir not in sys.path:
    sys.path.insert(0, docki_dir)

from app import create_app

app = create_app()
app.config["TESTING"] = True
client = app.test_client()

print("--- PROBANDO POST EN DIGITALIZACIÓN ---")

# Crear un archivo CSV de prueba en memoria
sample_csv = "Campo 1,Valor 1\nNombre Completo,Diego\nFecha de Nacimiento,16/08/1990\n"
data = {
    "form_file": (io.BytesIO(sample_csv.encode("utf-8")), "test_form.csv"),
    "form_name": "TEST FORM CSV",
    "form_version": "01.0001"
}

res_post = client.post("/digitize", data=data, content_type="multipart/form-data", follow_redirects=True)
print(f"POST /digitize -> status {res_post.status_code}")

if res_post.status_code >= 500:
    print("ERROR 500 EN POST /digitize:")
    print(res_post.data.decode("utf-8", errors="ignore")[:600])

# Probar confirmación del borrador en review
res_confirm = client.post("/digitize/review", data={"action": "confirm"}, follow_redirects=True)
print(f"POST /digitize/review (confirm) -> status {res_confirm.status_code}")

if res_confirm.status_code >= 500:
    print("ERROR 500 EN POST /digitize/review (confirm):")
    print(res_confirm.data.decode("utf-8", errors="ignore")[:600])

# Probar agregar campos en review
res_add = client.post("/digitize/review", data={"action": "add_fields", "selected_existing_labels": ["Número de Cliente:"]}, follow_redirects=True)
print(f"POST /digitize/review (add_fields) -> status {res_add.status_code}")

if res_add.status_code >= 500:
    print("ERROR 500 EN POST /digitize/review (add_fields):")
    print(res_add.data.decode("utf-8", errors="ignore")[:600])
