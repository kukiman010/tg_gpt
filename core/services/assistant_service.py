class AssistantService:
    def __init__(self, db, assistants_api, languages_api):
        self._db = db
        self._assistants = assistants_api
        self._languages = languages_api

    def set_assistant(self, user, button_idx: int):
        assistant = self._assistants.find_assistent(button_idx)
        for model, company in assistant.items():
            self._db.update_user_assistent(user.get_userId(), company, model)
            break

    def can_use_assistant(self, button_idx: int, user_status: int) -> bool:
        return self._assistants.isAvailable(button_idx, user_status)

    def set_language_by_button(self, user, button_idx: int):
        code_lang = self._languages.find_bottom(button_idx)
        self._db.update_user_lang_code(user.get_userId(), code_lang)
        return code_lang

