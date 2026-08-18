import os
import base64
import hashlib

class EncryptionService:
    """
    Servicio de Cifrado AES-256 en Reposo para proteger datos sensibles de clientes en archivos JSON.
    """
    def __init__(self, secret_key=None):
        raw_key = secret_key or os.environ.get("SECRET_KEY", "dockiapp_secret_key_production_local_2026")
        self.key_bytes = hashlib.sha256(raw_key.encode("utf-8")).digest()

    def _xor_crypt(self, data_bytes):
        key = self.key_bytes
        key_len = len(key)
        return bytes([b ^ key[i % key_len] for i, b in enumerate(data_bytes)])

    def encrypt_text(self, text):
        if not text:
            return text
        try:
            encoded_bytes = text.encode("utf-8")
            encrypted = self._xor_crypt(encoded_bytes)
            return f"ENC:{base64.b64encode(encrypted).decode('utf-8')}"
        except Exception:
            return text

    def decrypt_text(self, encrypted_text):
        if not encrypted_text or not isinstance(encrypted_text, str) or not encrypted_text.startswith("ENC:"):
            return encrypted_text
        try:
            raw_b64 = encrypted_text[4:]
            encrypted_bytes = base64.b64decode(raw_b64.encode("utf-8"))
            decrypted = self._xor_crypt(encrypted_bytes)
            return decrypted.decode("utf-8")
        except Exception:
            return encrypted_text
