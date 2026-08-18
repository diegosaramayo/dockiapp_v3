import json
import urllib.request
import urllib.error

OLLAMA_API_BASE = "http://127.0.0.1:11434"

class OllamaService:
    """
    Servicio de comunicación local con Ollama (http://127.0.0.1:11434)
    para listar modelos locales e invocar agentes con LLMs.
    """
    def is_ollama_running(self):
        try:
            req = urllib.request.Request(f"{OLLAMA_API_BASE}/api/tags", headers={"User-Agent": "DockiApp"})
            with urllib.request.urlopen(req, timeout=1.5) as response:
                return response.status == 200
        except Exception:
            return False

    def list_local_models(self):
        """
        Consulta la API local de Ollama para listar los modelos descargados.
        Ej: ['llama3:latest', 'mistral:latest', 'gemma:2b', 'phi3']
        """
        try:
            req = urllib.request.Request(f"{OLLAMA_API_BASE}/api/tags", headers={"User-Agent": "DockiApp"})
            with urllib.request.urlopen(req, timeout=2.0) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                    return models
        except Exception:
            pass
        return []

    def generate_agent_response(self, model_name, system_prompt, user_prompt):
        """
        Genera una respuesta inteligente del agente usando el modelo LLM de Ollama seleccionado.
        """
        if not model_name:
            return None

        url = f"{OLLAMA_API_BASE}/api/generate"
        payload = {
            "model": model_name,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=8.0) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode("utf-8"))
                    return result.get("response", "").strip()
        except Exception as e:
            return f"[Respuesta del Agente Ollama ({model_name}) no disponible: {str(e)}]"

        return None
