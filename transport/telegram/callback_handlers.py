import datetime
import os
from typing import Optional

from telebot import types

from Control.user_media import UserMedia
from core.callback_codec import CallbackCodec
from transport.telegram import ui as tg_ui
from transport.telegram.handler_context import TelegramAppContext


def handle_telegram_callback(call, ctx: Optional[TelegramAppContext]):
    if ctx is None:
        raise RuntimeError("TelegramAppContext is not wired; call wire_telegram_app() before polling")
    user = ctx.verify_callback_user(
        call.message.chat.id,
        call.message.message_id,
        call.message.chat.username,
        call.message.chat.type,
        call.from_user.language_code,
    )
    key = call.data
    cmd = CallbackCodec.decode(key)

    message_id = call.message.message_id
    chat_id = call.message.chat.id
    bot = ctx.bot
    locale = ctx.locale
    _db = ctx.db
    _env = ctx.env
    _output = ctx.output
    _speak = ctx.speak
    _mediaWorker = ctx.media_worker
    _payMan = ctx.pay_man
    _languages_api = ctx.languages_api
    _tariffs_api = ctx.tariffs_api
    _user_service = ctx.user_service
    _assistant_service = ctx.assistant_service

    if key == "menu":
        bot.answer_callback_query(call.id, text="")
        ctx.main_menu(user, chat_id, message_id)
    elif key == "sintez":
        text = call.message.text

        t_mes = locale.find_translation(user.get_language(), "TR_START_DECODE_VOICE")
        bot.answer_callback_query(call.id, text=t_mes)

        files = _speak.speach(text, chat_id, "alena")

        for file in files:
            with open(file, "rb") as audio:
                bot.send_audio(chat_id, audio)
            os.remove(file)

    elif key == "update_env":
        data_dict = _db.get_environment()
        mes = _env.show_differences(
            data_dict,
            locale.find_translation(user.get_language(), "TR_NEW_OLD_CHANGES"),
        )

        if mes:
            answer = locale.find_translation(
                user.get_language(), "TR_CHANGES_HAVE_BEEN_APPLICED"
            ).format(mes)

            _env.update(data_dict)
            _output.send_text(chat_id, answer, id_message_for_edit=message_id)
            bot.answer_callback_query(
                call.id, locale.find_translation(user.get_language(), "TR_SUCCESS")
            )
        else:
            _output.send_text(
                chat_id,
                locale.find_translation(user.get_language(), "TR_DATA_IS_UP_TO_DATE"),
                id_message_for_edit=message_id,
            )
            bot.answer_callback_query(
                call.id, locale.find_translation(user.get_language(), "TR_FAILURE")
            )

    elif key == "no_update_env":
        _output.send_text(
            chat_id,
            locale.find_translation(user.get_language(), "TR_TR_CHANGES_NOT_APPLICED"),
            id_message_for_edit=message_id,
        )
        bot.answer_callback_query(
            call.id, locale.find_translation(user.get_language(), "TR_SUCCESS")
        )

    elif key == "menu_language":
        bot.answer_callback_query(call.id, text="")
        if user is None or _languages_api.size() == 0:
            _output.send_text(
                chat_id,
                locale.find_translation(user.get_language(), "TR_ERROR_NOT_CHANGE_LANGUAGE"),
            )
            return
        t_mes = locale.find_translation(user.get_language(), "TR_SELECT_LANGUAGE")

        buttons = _languages_api.available_by_status()
        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.language_menu_markup(locale, user.get_language(), buttons),
            id_message_for_edit=message_id,
        )

    elif key == "menu_promt":
        bot.answer_callback_query(call.id, text="")
        t_mes = locale.find_translation(user.get_language(), "TR_SELECT_PROMT")
        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.prompt_menu_markup(locale, user.get_language()),
            id_message_for_edit=message_id,
        )

    elif key == "menu_generate_image":
        bot.answer_callback_query(call.id, text="")
        ctx.generate_photo(user, message_id)

    elif key == "show_my_promt":
        bot.answer_callback_query(call.id, text="")
        t_mes = locale.find_translation(user.get_language(), "TR_SHOW_PROMT_NOW").format(
            user.get_prompt()
        )
        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.back_only_markup(locale, user.get_language(), "menu_promt"),
            id_message_for_edit=message_id,
        )

    elif key == "set_promt":
        bot.answer_callback_query(call.id, text="")
        t_mes = locale.find_translation(user.get_language(), "TR_SET_PROMT")
        _user_service.set_wait_action(user.get_userId(), "wait_new_prompt")
        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.set_prompt_undo_markup(locale, user.get_language()),
            id_message_for_edit=message_id,
        )

    elif key == "set_default_promt":
        bot.answer_callback_query(call.id, text="")
        t_mes = locale.find_translation(user.get_language(), "TR_DEFAULT_PROMT").format(
            _env.get_prompt()
        )
        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.default_prompt_actions_markup(locale, user.get_language()),
            id_message_for_edit=message_id,
        )

    elif key == "apply_default_promt":
        bot.answer_callback_query(
            call.id, text=locale.find_translation(user.get_language(), "TR_SUCCESS")
        )
        t_mes = locale.find_translation(user.get_language(), "TR_PROMT_APPLY")
        _db.update_user_prompt(user.get_userId(), _env.get_prompt())
        _output.send_text(chat_id, t_mes, id_message_for_edit=message_id)

    elif key == "menu_help":
        bot.answer_callback_query(call.id, text="")
        text = ctx.command_help(user)
        _output.send_text(
            chat_id,
            text,
            reply_markup=tg_ui.help_menu_markup(locale, user.get_language()),
            id_message_for_edit=message_id,
        )

    elif key == "menu_premium":
        ctx.premium_button(user, message_id)

    elif key == "menu_support":
        bot.answer_callback_query(call.id, text="")
        t_mes = locale.find_translation(user.get_language(), "TR_MESSAGE_SUPPORT").format(
            user.get_prompt()
        )
        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.support_message_markup(locale, user.get_language()),
            id_message_for_edit=message_id,
        )

    elif key == "menu_websearch":
        bot.answer_callback_query(call.id, text="")
        if user.get_is_search():
            t_mes = locale.find_translation(user.get_language(), "TR_TITLE_WEBSEARCH_ON")
        else:
            t_mes = locale.find_translation(user.get_language(), "TR_TITLE_WEBSEARCH_OFF")
        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.websearch_toggle_menu_markup(
                locale, user.get_language(), user.get_is_search()
            ),
            id_message_for_edit=message_id,
        )

    elif key == "edit_websearch":
        bot.answer_callback_query(
            call.id, text=locale.find_translation(user.get_language(), "TR_SUCCESS")
        )

        if user.get_is_search():
            _db.update_user_search_status(user.get_userId(), False)
            t_mes = locale.find_translation(user.get_language(), "TR_WEBSEARCH_OFF")
        else:
            _db.update_user_search_status(user.get_userId(), True)
            t_mes = locale.find_translation(user.get_language(), "TR_WEBSEARCH_ON")

        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.websearch_after_toggle_markup(locale, user.get_language()),
            id_message_for_edit=message_id,
        )

    elif key == "errorPost":
        bot.edit_message_reply_markup(chat_id, message_id)
        hasUser = _mediaWorker.find_userId(user.get_userId())
        media = UserMedia(user.get_userId(), chat_id, user.get_login())

        if hasUser is False:
            t_mes = locale.find_translation(user.get_language(), "TR_WAIT_POST")
            send_mess = bot.send_message(chat_id, t_mes)
            del_mes = UserMedia(user.get_userId(), chat_id, user.get_login())
            del_mes.add_del_mess_id(send_mess.message_id)
            _mediaWorker.add_data(del_mes)

        media.add_mes(call.message)
        _mediaWorker.add_data(media)

    elif cmd.action == "assistant_select":
        idx = int(cmd.args["id"])

        if not _assistant_service.can_use_assistant(idx, user.get_status()):
            bot.send_message(
                chat_id,
                locale.find_translation(user.get_language(), "TR_NEED_PREMIUM_ASSISTANT"),
            )
            bot.answer_callback_query(
                call.id,
                locale.find_translation(user.get_language(), "TR_NEED_PERMISSION"),
            )
            return

        _assistant_service.set_assistant(user, idx)

        bot.send_message(
            chat_id, locale.find_translation(user.get_language(), "TR_USE_NEW_ASSISTANT")
        )
        bot.answer_callback_query(
            call.id, locale.find_translation(user.get_language(), "TR_SUCCESS")
        )

    elif cmd.action == "language_select":
        idx = int(cmd.args["id"])
        code_lang = _assistant_service.set_language_by_button(user, idx)
        if locale.islanguage(code_lang):
            bot.send_message(
                chat_id, locale.find_translation(code_lang, "TR_SYSTEM_LANGUAGE_CHANGE")
            )
            bot.answer_callback_query(
                call.id, locale.find_translation(code_lang, "TR_SUCCESS")
            )
        else:
            bot.send_message(
                chat_id,
                locale.find_translation(user.get_language(), "TR_SYSTEM_LANGUAGE_SUPPORT"),
            )
            bot.answer_callback_query(
                call.id, locale.find_translation(user.get_language(), "TR_FAILURE")
            )

    elif cmd.action == "payment_select":
        bot.answer_callback_query(
            call.id, text=locale.find_translation(user.get_language(), "TR_SUCCESS")
        )
        paymet_system = cmd.args["system"]
        tarif_id = cmd.args["tariff_id"]

        tariffs_data = None
        tarifs_data = _db.get_tariffs(tarif_id)
        for node in tarifs_data:
            if node.tariff_id == int(tarif_id):
                tariffs_data = node

        if tariffs_data is None:
            _output.send_text(
                chat_id,
                locale.find_translation(
                    user.get_language(), "TR_TARRIF_DONT_LOAD"
                ).format(_env.get_support_chat()),
                reply_markup=tg_ui.back_to_premium_markup(locale, user.get_language()),
                id_message_for_edit=message_id,
            )
            return

        description = locale.find_translation(
            user.get_language(), "TR_SUBSCRIBE_FOR_ONE_MOUNTH"
        ).format(tariffs_data.activity_day)

        if paymet_system == "TelegramStarsPay":
            label = _payMan.generate_payment_label(user.get_userId())

            pay_description = locale.find_translation(user.get_language(), "TR_PAY").format(
                tariffs_data.price_stars, " stars"
            )
            markup = tg_ui.stars_invoice_markup(locale, user.get_language(), pay_description)

            prices = [types.LabeledPrice(label="XTR", amount=int(tariffs_data.price_stars))]
            bot.send_invoice(
                chat_id,
                title=description,
                description=description,
                invoice_payload=label,
                provider_token="",
                currency="XTR",
                prices=prices,
                reply_markup=markup,
            )
            bot.delete_message(chat_id, message_id)

            _db.add_invoice_journal(
                user.get_userId(),
                label,
                label,
                tarif_id,
                "pending",
                tariffs_data.price_stars,
                "XTR",
                paymet_system,
                description,
                datetime.datetime.now(
                    datetime.timezone(datetime.timedelta(hours=3))
                ),
                False,
            )

        else:
            pay_info = _payMan.create_invoice(
                paymet_system, int(tariffs_data.price_rub), "RUB", user.get_userId(), description
            )

            pay_info.tarrif = tarif_id
            pay_info.user_name = user.get_login()

            if pay_info.status == "pending":
                _db.add_invoice_journal(
                    pay_info.user_id,
                    pay_info.payment_id,
                    pay_info.label_pay,
                    pay_info.tarrif,
                    pay_info.status,
                    pay_info.amount,
                    pay_info.currency,
                    pay_info.payment_system,
                    pay_info.description,
                    pay_info.created_at,
                    pay_info.is_test,
                )
                _payMan.add_payment(pay_info)

                pay_description = locale.find_translation(
                    user.get_language(), "TR_PAY"
                ).format(pay_info.amount, pay_info.currency)
                markup = tg_ui.external_payment_markup(
                    locale, user.get_language(), pay_description, pay_info.url_pay
                )
                _output.send_text(
                    chat_id, description, reply_markup=markup, id_message_for_edit=message_id
                )

    elif cmd.action == "tariff_select":
        code_tariff = _tariffs_api.find_bottom(int(cmd.args["id"]))

        tariffs = _db.get_tariffs()

        for node in tariffs:
            if node.tariff_id == code_tariff:
                ctx.pay_button(user, True, node.tariff_id, node.description_code, message_id)
                break

    elif cmd.action == "check_payment":
        print()

    else:
        t_mes = locale.find_translation(user.get_language(), "TR_ERROR")
        bot.answer_callback_query(call.id, text=t_mes)
