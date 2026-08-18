import sys
import os

docki_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if docki_dir not in sys.path:
    sys.path.insert(0, docki_dir)

from app import create_app

app = create_app()

print("--- REGLAS DE NAVEGACION (URL RULES) ---")
for rule in app.url_map.iter_rules():
    print(f"Endpoint: {rule.endpoint} -> {rule}")
