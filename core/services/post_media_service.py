import base64
import os
from dataclasses import dataclass
from typing import Any, Callable, List

from Control.user_media import UserMedia
from core.ports.message_output import MessageOutputPort
from core.services.conversation_service import ConversationService
from core.services.user_service import UserService


@dataclass
class PostMediaMarkups:
    """Клавиатуры для ответа после батча медиа (задаются transport-слоем)."""

    error_repeat: Callable[[str], Any]
    vocalize: Callable[[str], Any]


class PostMediaService:
    """Сборка текста/фото из MediaWorker, вызов LLM, сохранение контекста, ответ пользователю."""

    def __init__(
        self,
        db,
        conversation: ConversationService,
        user_service: UserService,
        env,
        locale,
        output: MessageOutputPort,
        file_converter,
        markups: PostMediaMarkups,
    ):
        self._db = db
        self._conversation = conversation
        self._user_service = user_service
        self._env = env
        self._locale = locale
        self._output = output
        self._file_converter = file_converter
        self._markups = markups

    @staticmethod
    def encode_image_file(image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def handle(self, _sender, user_id, media_list: List[UserMedia], get_user_easy) -> None:
        message = ""
        text_mes = ""
        chat_id = ""
        title_mess_ids = []
        photos = []
        is_photos = False

        for media in media_list:
            if chat_id == "":
                chat_id = media._chatId

            if media._type == "document":
                path = "users_media/files/{}".format(media._fileWay)
                message += self._file_converter.convert_files_to_text(path, media._fileName)
                os.remove(path)
            if media._type == "message":
                text_mes += media._mediaData
            if media._type == "titleId":
                title_mess_ids.append(media._titleId)
            if media._type == "photo":
                photos.append(self.encode_image_file(media._fileWay))
                if media._mediaData:
                    text_mes += media._mediaData
                is_photos = True

            message = text_mes + "\n" + message

        if chat_id == "":
            chat_id = user_id

        user = get_user_easy(user_id)
        if user is None:
            return

        self._db.update_last_login(user_id)

        generate_image = user.get_wait_action() == "generate_image"

        payload, bool_photo_result = self._conversation.merge_context(
            chat_id, user, message, photos, generate_image
        )

        if generate_image:
            content = self._conversation.post_generate_image(
                user, payload, "gpt-4.1"
            )
            self._user_service.reset_action(user.get_userId())
        elif is_photos or bool_photo_result:
            content = self._conversation.post_vision(payload, "gpt-4o")
        else:
            content = self._conversation.post_chat(user, payload, user.get_model())

        if content and content.get_code() == 200:
            self._db.add_context(user.get_userId(), chat_id, "user", chat_id, message)
            for photo_b64 in photos:
                self._db.add_context(
                    user.get_userId(), chat_id, "user", chat_id, photo_b64, True
                )
            self._db.add_context(
                user.get_userId(), chat_id, "assistant", chat_id, content.get_result()
            )

        max_char = int(self._env.get_count_char_for_gen_audio())

        for med_id in title_mess_ids:
            self._output.delete_message(chat_id, med_id)

        lang = user.get_language()
        if not content.get_result() or content.get_code() >= 300:
            self._output.send_text(
                chat_id,
                self._locale.find_translation(lang, "TR_ERROR_GET_RESULT").format(
                    content.get_result()
                ),
                reply_markup=self._markups.error_repeat(lang),
                isMarkdown=True,
            )
            return

        if len(content.get_result()) <= max_char:
            self._output.send_text(
                chat_id,
                content.get_result(),
                reply_markup=self._markups.vocalize(lang),
                isMarkdown=True,
            )
        else:
            self._output.send_text(chat_id, content.get_result(), isMarkdown=True)
