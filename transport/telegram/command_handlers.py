"""Обработчики админ-команд Telegram (тонкий transport-слой)."""

from dataclasses import dataclass
from typing import Any, Callable

from Control.user import User
from transport.telegram import ui as tg_ui


@dataclass
class AdminCommandsDeps:
    bot: Any
    db: Any
    locale: Any
    output: Any
    env: Any
    logger: Any
    pay_man: Any
    assistent_api: Any
    languages_api: Any
    tariffs_api: Any
    update_scheduler_time: Callable[[], None]


def handle_lastlog(message, user: User, d: AdminCommandsDeps):
    if d.db.isAdmin(message.from_user.id, message.chat.username) is False:
        d.bot.send_message(
            message.chat.id,
            d.locale.find_translation(user.get_language(), "TR_NO_PERMITION"),
        )
        return

    words = message.text.split()

    if len(words) == 2:
        second_word = words[1]
        if second_word.isdigit():
            text = d.logger.read_file_from_end(int(second_word))
            t_mes = d.locale.find_translation(user.get_language(), "TR_GET_LOG")
            d.bot.send_message(message.chat.id, t_mes.format(second_word, text))

    elif len(words) == 3:
        second_word = words[1]
        type_log = words[2]

        if second_word.isdigit():
            text = d.logger.read_file_from_end(int(second_word), type_log)
            t_mes = d.locale.find_translation(user.get_language(), "TR_GET_LOG_POST")
            d.bot.send_message(
                message.chat.id, t_mes.format(second_word, type_log, text)
            )
    else:
        t_mes = d.locale.find_translation(user.get_language(), "TR_ERROR_SINTAX")
        d.bot.send_message(message.chat.id, t_mes)


def handle_notify_all(message, user: User, d: AdminCommandsDeps):
    if d.db.isAdmin(message.from_user.id, message.chat.username) is False:
        d.bot.send_message(
            message.chat.id,
            d.locale.find_translation(user.get_language(), "TR_NO_PERMITION"),
        )
        return

    data = d.db.get_all_chat(message.from_user.id)
    text = message.text
    words = text.split()
    result = " ".join(words[1:])

    for i in data:
        for j in i:
            for k in j:
                d.bot.send_message(k, result)


def handle_update_env(message, user: User, d: AdminCommandsDeps):
    chat_id = message.chat.id
    if d.db.isAdmin(message.from_user.id, message.chat.username) is False:
        d.bot.send_message(
            chat_id,
            d.locale.find_translation(user.get_language(), "TR_NO_PERMITION"),
        )
        return

    mes = d.env.show_differences(
        d.db.get_environment(),
        d.locale.find_translation(user.get_language(), "TR_NEW_OLD_CHANGES"),
    )

    if mes:
        answer = d.locale.find_translation(user.get_language(), "DATA_IS_NOT_RELEVANT").format(
            mes
        )
        d.output.send_text(
            chat_id,
            answer,
            reply_markup=tg_ui.env_update_confirm_markup(d.locale, user.get_language()),
        )
    else:
        d.output.send_text(
            chat_id,
            d.locale.find_translation(user.get_language(), "TR_DATA_IS_UP_TO_DATE"),
        )


def handle_update_lang_models_pay(message, user: User, d: AdminCommandsDeps):
    chat_id = message.chat.id
    if d.db.isAdmin(message.from_user.id, message.chat.username) is False:
        d.bot.send_message(
            chat_id,
            d.locale.find_translation(user.get_language(), "TR_NO_PERMITION"),
        )
        return

    d.logger.add_info(
        "Запущено обновление переменных _payMan, _assistent_api, _languages_api, _scheduler"
    )

    d.pay_man.update(d.db.get_payment_systems())
    d.assistent_api.clear()
    d.assistent_api.load_models(d.db.get_assistant_ai())
    d.languages_api.clear()
    d.languages_api.load_models(d.db.get_languages())
    d.tariffs_api.clear()
    d.tariffs_api.load_models(d.db.get_tariffs())
    d.update_scheduler_time()

    d.output.send_text(
        chat_id, d.locale.find_translation(user.get_language(), "TR_UPDATE_DATA")
    )
