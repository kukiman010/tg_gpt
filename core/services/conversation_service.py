from openai import OpenAIError

import Control.context_model
from Control.user import User


class ConversationService:
    def __init__(self, db, speaker, logger, clients_by_company: dict):
        self._db = db
        self._speaker = speaker
        self._logger = logger
        self._clients = clients_by_company

    def merge_context(self, chat_id, user: User, text_to_photo, photos, generate_image: bool = False):
        context = Control.context_model.Context_model()
        context.set_data(user.get_userId(), chat_id, "system", chat_id, user.get_prompt(), False)

        data = [context]
        data.extend(self._db.get_context(user.get_userId(), chat_id))

        user_message = Control.context_model.Context_model()
        user_message.set_data(user.get_userId(), chat_id, "user", chat_id, text_to_photo, False)
        data.append(user_message)

        has_photo = False
        for photo_to_base64 in photos:
            if not photo_to_base64:
                continue
            photo_message = Control.context_model.Context_model()
            photo_message.set_data(user.get_userId(), chat_id, "user", chat_id, photo_to_base64, True)
            data.append(photo_message)
            has_photo = True

        converted = Control.context_model.convert(user.get_companyAi(), data, True, generate_image)
        return converted, has_photo

    def post_generate_image(self, user: User, payload, model) -> Control.context_model.AnswerAssistent:
        answer = Control.context_model.AnswerAssistent()
        try:
            answer = self._clients["OpenAi"].create_image(payload, model)
        except OpenAIError as err:
            self._logger.add_critical("OpenAI: {}".format(err))
            answer.code = 500
            answer.result = str(err)
        return answer

    def post_vision(self, payload, model) -> Control.context_model.AnswerAssistent:
        answer = Control.context_model.AnswerAssistent()
        try:
            answer = self._clients["OpenAi"].gpt_post_view(payload, model, 1300)
        except OpenAIError as err:
            self._logger.add_critical("OpenAI: {}".format(err))
            answer.code = 500
            answer.result = str(err)
        return answer

    def post_chat(self, user: User, payload, model) -> Control.context_model.AnswerAssistent:
        answer = Control.context_model.AnswerAssistent()
        company = str(user.get_companyAi()).strip().lower()
        try:
            if company == "openai":
                answer = self._clients["OpenAi"].post_gpt(payload, model, user.get_is_search())
            elif company == "yandex":
                self._clients["Yandex"].set_token(self._speaker.get_IAM())
                answer = self._clients["Yandex"].post_gpt(payload, model)
            elif company == "meta":
                answer = self._clients["Meta"].post_gpt(payload, model)
            elif company == "x ai":
                answer = self._clients["X ai"].post_gpt(model, payload)
            elif company == "claude":
                answer = self._clients["Claude"].post_gpt(payload, model)
            elif company == "deepseek":
                answer = self._clients["DeepSeek"].post_gpt(payload, model)
            elif company == "google":
                answer = self._clients["Google"].post_gpt(payload, model)
            else:
                answer.set_answer(400, f"Unknown provider: {user.get_companyAi()}", 0)
        except OpenAIError as err:
            self._logger.add_critical("OpenAI: {}".format(err))
            answer.code = 500
            answer.result = str(err)
        return answer

