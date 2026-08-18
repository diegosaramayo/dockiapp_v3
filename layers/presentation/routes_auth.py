from flask import Blueprint, render_template, request, redirect, url_for, session
from layers.business_logic.auth_service import AuthService
from layers.business_logic.audit_service import AuditService
from layers.data_storage.config_repository import ConfigRepository

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()
audit_service = AuditService()
config_repo = ConfigRepository()

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    config = config_repo.get_config()
    error = None

    if auth_service.is_authenticated():
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            error = "Por favor ingrese usuario y contraseña."
        else:
            if auth_service.login_user(username, password):
                audit_service.log("LOGIN_EXITOSO", f"Inicio de sesión correcto del usuario '{username}'")
                next_page = request.args.get("next")
                if next_page and next_page.startswith("/"):
                    return redirect(next_page)
                return redirect(url_for("main.index"))
            else:
                audit_service.log("LOGIN_FALLIDO", f"Intento fallido de inicio de sesión para el usuario '{username}'")
                error = "Usuario o contraseña incorrectos."

    return render_template("login.html", config=config, error=error)

@auth_bp.route("/logout")
def logout():
    user = auth_service.get_current_user()
    if user:
        audit_service.log("LOGOUT", f"Cierre de sesión del usuario '{user.get('username')}'")
    auth_service.logout_user()
    return redirect(url_for("auth.login"))
