from functools import wraps
from flask import session, redirect, url_for, flash, request
from layers.data_storage.user_repository import UserRepository

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def login_user(self, username, password):
        user = self.user_repo.authenticate(username, password)
        if user:
            session["user"] = {
                "username": user["username"],
                "name": user["name"],
                "role": user["role"]
            }
            session.permanent = True
            return True
        return False

    def logout_user(self):
        session.pop("user", None)

    def get_current_user(self):
        return session.get("user")

    def is_authenticated(self):
        return "user" in session

    def is_admin(self):
        user = self.get_current_user()
        return user and user.get("role") == "admin"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user")
        if not user:
            return redirect(url_for("auth.login", next=request.url))
        if user.get("role") != "admin":
            return redirect(url_for("main.index", error="Acceso denegado. Se requieren permisos de Administrador."))
        return f(*args, **kwargs)
    return decorated_function
