import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
ASSETS_DIR = os.path.join(STORAGE_DIR, "assets")
CONFIG_PATH = os.path.join(ASSETS_DIR, "config.json")

class ConfigRepository:
    def __init__(self):
        os.makedirs(ASSETS_DIR, exist_ok=True)
        if not os.path.exists(CONFIG_PATH):
            self._save({
                "company_name": "Empresa",
                "company_logo_url": None
            })

    def _load(self):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"company_name": "Empresa", "company_logo_url": None}

    def _save(self, config_data):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

    def get_config(self):
        return self._load()

    def update_logo(self, logo_filename):
        config = self._load()
        config["company_logo_url"] = f"/static/uploads/assets/{logo_filename}"
        self._save(config)
        return config

    def update_company_name(self, name):
        config = self._load()
        config["company_name"] = name
        self._save(config)
        return config
