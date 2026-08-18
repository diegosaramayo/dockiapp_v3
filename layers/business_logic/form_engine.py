class FormEngine:
    """
    Motor de gestión de formularios, estado de respuestas y paginación.
    """
    def __init__(self, form_data):
        self.form = form_data
        self.steps = form_data.get("steps", [])
        self.total_content_steps = len(self.steps)
        # El paso final de confirmación es total_content_steps + 1
        self.total_pages = self.total_content_steps + 1

    def get_step(self, step_number):
        if 1 <= step_number <= self.total_content_steps:
            return self.steps[step_number - 1]
        return None

    def is_final_step(self, step_number):
        return step_number == self.total_pages
