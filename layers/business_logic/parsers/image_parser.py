import os
from werkzeug.utils import secure_filename

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp"}

class ImageParser:
    """
    Procesador de archivos de imagen para Skills, Rules y Avatares de Agents.
    """
    def save_image(self, file_object, upload_folder):
        if not file_object or file_object.filename == "":
            return None

        ext = os.path.splitext(file_object.filename)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise ValueError(f"Formato de imagen no permitido ({ext}). Permitidos: png, jpg, jpeg, svg, webp.")

        filename = secure_filename(file_object.filename)
        os.makedirs(upload_folder, exist_ok=True)
        target_path = os.path.join(upload_folder, filename)
        file_object.save(target_path)

        return filename
