import re
from typing import Any, Optional


def _find_substring_occurrences(text: str, substring: str) -> int:
    if not substring or not text:
        return -1
    indices = []
    start = 0
    while start != -1:
        start = text.find(substring, start)
        if start != -1:
            indices.append(start)
            start += len(substring)
    return indices[-1] if len(indices) % 2 != 0 else -1


def _fix_markdown_blocks(array: list) -> None:
    block_code = "```"
    block_bold = "**"
    fix_block = ""

    for i, text in enumerate(array):
        if fix_block:
            array[i] = fix_block + array[i]
            fix_block = ""

        find_block_code = _find_substring_occurrences(array[i], block_code)
        find_block_bold = _find_substring_occurrences(array[i], block_bold)

        if find_block_code != -1 and find_block_bold != -1:
            if find_block_code < find_block_bold:
                fix_block = block_code + block_bold
                array[i] += block_bold + block_code
            else:
                fix_block = block_bold + block_code
                array[i] += block_code + block_bold
        elif find_block_code != -1:
            fix_block = block_code
            array[i] += block_code
        elif find_block_bold != -1:
            fix_block = block_bold
            array[i] += block_bold


def _replace_stars_with_backticks(text: str) -> str:
    return re.sub(r"\*\*(.*?)\*\*", r"`\1`", text)


class TelegramMessageOutput:
    """Telegram implementation of long-text send + edit (telebot)."""

    def __init__(self, bot, logger):
        self._bot = bot
        self._logger = logger

    def send_text(
        self,
        chat_id: int,
        text: str,
        reply_markup: Any = None,
        id_message_for_edit: Optional[int] = None,
        isMarkdown: bool = False,
    ) -> None:
        max_message_length = 4050
        hard_break_point = 3700
        soft_break_point = 3300
        results = []

        while len(text) > max_message_length:
            offset = text[soft_break_point:hard_break_point].rfind("\n")
            if offset == -1:
                offset = text[soft_break_point:max_message_length].rfind(" ")
            if offset == -1:
                results.append(text[:max_message_length])
                text = text[max_message_length:]
            else:
                original_index = offset + soft_break_point
                results.append(text[:original_index])
                text = text[original_index:]

        if text:
            results.append(text)

        if isMarkdown:
            _fix_markdown_blocks(results)

        edit_id = id_message_for_edit
        for chunk in results:
            if isMarkdown:
                converted_text = _replace_stars_with_backticks(chunk)
            else:
                converted_text = chunk

            try:
                if edit_id:
                    if isMarkdown:
                        self._bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=edit_id,
                            text=converted_text,
                            reply_markup=reply_markup,
                            parse_mode="Markdown",
                        )
                    else:
                        self._bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=edit_id,
                            text=converted_text,
                            reply_markup=reply_markup,
                        )
                    edit_id = None
                else:
                    if isMarkdown:
                        self._bot.send_message(
                            chat_id,
                            converted_text,
                            reply_markup=reply_markup,
                            parse_mode="Markdown",
                        )
                    else:
                        self._bot.send_message(
                            chat_id, converted_text, reply_markup=reply_markup
                        )
            except Exception as e:
                self._logger.add_critical(
                    f"Ошибка для chat_id:{chat_id} при отправке сообщения. Ошибка: {e}\n В этом тексте: \n{converted_text}"
                )
                self._bot.send_message(
                    chat_id, converted_text, reply_markup=reply_markup
                )

    def delete_message(self, chat_id: int, message_id: int) -> None:
        self._bot.delete_message(chat_id, message_id)
