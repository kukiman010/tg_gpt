from Control.user import User


class UserService:
    def __init__(self, db, env, logger):
        self._db = db
        self._env = env
        self._logger = logger

    def verify_from_message(self, message) -> User:
        if self._db.find_user(message.from_user.id) is False:
            name = message.chat.username or message.chat.first_name
            self._create_default_user(message.from_user.id, name, message.chat.type, message.from_user.language_code)
            self._logger.add_info("создан новый пользователь {}".format(message.chat.username))
        else:
            self._db.add_users_in_groups(message.from_user.id, message.chat.id)
        return self._get_if_active(message.from_user.id)

    def verify_custom(self, user_id, chat_id, chat_username, chat_type, lang_code) -> User:
        if self._db.find_user(user_id) is False:
            self._create_default_user(user_id, chat_username, chat_type, lang_code)
            self._logger.add_info("создан новый пользователь {}".format(chat_username))
        else:
            self._db.add_users_in_groups(user_id, chat_id)
        return self._get_if_active(user_id)

    def verify_easy(self, user_id) -> User:
        if self._db.find_user(user_id) is False:
            return None
        return self._db.get_user_def(user_id)

    def reset_action(self, user_id):
        self._db.update_user_action(user_id, "")

    def set_wait_action(self, user_id, action):
        self._db.update_user_action(user_id, action)

    def apply_prompt_action(self, user: User, text: str):
        self.reset_action(user.get_userId())
        self._db.update_user_prompt(user.get_userId(), text.replace("'", " "))

    def _create_default_user(self, user_id, username, chat_type, language_code):
        user = User()
        user.set_default_data(
            self._env.get_language(),
            self._env.get_permission(),
            self._env.get_company_ai(),
            self._env.get_assistant_model(),
            self._env.get_recognizes_photo_model(),
            self._env.get_generate_photo_model(),
            self._env.get_text_to_audio(),
            self._env.get_audio_to_text(),
            self._env.get_speakerName(),
            self._env.get_prompt(),
        )
        self._db.add_user(user_id, username, chat_type, language_code)

    def _get_if_active(self, user_id):
        user = self._db.get_user_def(user_id)
        if user.get_status() == 0:
            return None
        return user

