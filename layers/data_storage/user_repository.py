import os
import json
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
USERS_FILE = os.path.join(STORAGE_DIR, "users.json")

class UserRepository:
    def __init__(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)
        self._ensure_default_users()

    def _ensure_default_users(self):
        if not os.path.exists(USERS_FILE):
            default_users = {
                "admin": {
                    "username": "admin",
                    "name": "Administrador General",
                    "password_hash": generate_password_hash("admin123"),
                    "role": "admin"
                },
                "operador": {
                    "username": "operador",
                    "name": "Operador de Formulario",
                    "password_hash": generate_password_hash("operador123"),
                    "role": "operator"
                }
            }
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(default_users, f, indent=2, ensure_ascii=False)

    def get_all_users(self):
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_user_by_username(self, username):
        users = self.get_all_users()
        return users.get(username.strip().lower())

    def authenticate(self, username, password):
        user = self.get_user_by_username(username)
        if user and check_password_hash(user.get("password_hash", ""), password):
            return user
        return None
