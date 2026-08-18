import sys
import os
from datetime import timedelta
from flask import Flask

# Obtener la ruta absoluta del directorio donde se encuentra este archivo app.py
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Rutas absolutas explícitas para plantillas Jinja2 y archivos estáticos
template_dir = os.path.abspath(os.path.join(base_dir, "templates"))
static_dir = os.path.abspath(os.path.join(base_dir, "static"))

# Garantizar la existencia de todas las carpetas de persistencia e imágenes en el servidor cloud
os.makedirs(os.path.join(base_dir, "storage", "forms"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "storage", "skills"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "storage", "rules"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "storage", "agents"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "storage", "uploads"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "static", "uploads", "images"), exist_ok=True)

from layers.presentation.routes_auth import auth_bp
from layers.presentation.routes_main import main_bp
from layers.presentation.routes_digitize import digitize_bp
from layers.presentation.routes_form import form_bp
from layers.presentation.routes_skills import skills_bp
from layers.presentation.routes_rules import rules_bp
from layers.presentation.routes_agents import agents_bp
from layers.presentation.routes_audit import audit_bp

def create_app():
    app = Flask(
        "dockiapp",
        template_folder=template_dir,
        static_folder=static_dir
    )

    app.secret_key = os.environ.get("SECRET_KEY", "dockiapp_secret_key_production_local_2026")
    
    # MEDIDA 2: Límite máximo de seguridad para la subida de archivos (10 MB)
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
    
    # MEDIDA 1: Expiración automática de sesión inactiva (10 minutos)
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=10)

    # MEDIDA 3: Inyección de Cabeceras HTTP de Seguridad Estándar Bancario
    @app.after_request
    def apply_security_headers(response):
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Registrar Blueprints de la Capa de Presentación
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(digitize_bp)
    app.register_blueprint(form_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(rules_bp)
    app.register_blueprint(agents_bp)
    app.register_blueprint(audit_bp)

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host=host, port=port, debug=debug)
