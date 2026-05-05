"""Telegram-specific inline keyboards (telebot.types)."""

from telebot import types


def env_update_confirm_markup(locale, lang_code: str) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    m.add(
        types.InlineKeyboardButton(
            locale.find_translation(lang_code, "TR_YES"), callback_data="update_env"
        ),
        types.InlineKeyboardButton(
            locale.find_translation(lang_code, "TR_NO"), callback_data="no_update_env"
        ),
    )
    return m


def main_menu_markup(locale, lang_code: str) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    t = lambda k: locale.find_translation(lang_code, k)
    m.add(types.InlineKeyboardButton(t("TR_MENU_LANGUAGE"), callback_data="menu_language"))
    m.add(types.InlineKeyboardButton(t("TR_MENU_GEN_IMAGE"), callback_data="menu_generate_image"))
    m.add(types.InlineKeyboardButton(t("TR_MENU_PROMT"), callback_data="menu_promt"))
    m.add(types.InlineKeyboardButton(t("TR_MENU_WEBSEARCH"), callback_data="menu_websearch"))
    m.add(types.InlineKeyboardButton(t("TR_MENU_HELP"), callback_data="menu_help"))
    m.add(types.InlineKeyboardButton(t("TR_MENU_PREMIUM"), callback_data="menu_premium"))
    m.add(types.InlineKeyboardButton(t("TR_MENU_SUPPORT"), callback_data="menu_support"))
    return m


def assistant_select_markup(locale, lang_code: str, buttons: dict) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    for key, value in buttons.items():
        m.add(types.InlineKeyboardButton(value, callback_data=key))
    return m


def language_menu_markup(locale, lang_code: str, buttons: dict) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    for key, value in buttons.items():
        m.add(types.InlineKeyboardButton(value, callback_data=key))
    m.add(
        types.InlineKeyboardButton(
            locale.find_translation(lang_code, "TR_MENU"), callback_data="menu"
        )
    )
    return m


def prompt_menu_markup(locale, lang_code: str) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    t = lambda k: locale.find_translation(lang_code, k)
    m.add(types.InlineKeyboardButton(t("TR_BUTTOM_PROMT_NOW"), callback_data="show_my_promt"))
    m.add(types.InlineKeyboardButton(t("TR_BUTTOM_SET_PROMT"), callback_data="set_promt"))
    m.add(types.InlineKeyboardButton(t("TR_BUTTOM_DEFAULT_PROMT"), callback_data="set_default_promt"))
    m.add(types.InlineKeyboardButton(t("TR_MENU"), callback_data="menu"))
    return m


def back_only_markup(locale, lang_code: str, callback_data: str) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    m.add(
        types.InlineKeyboardButton(
            locale.find_translation(lang_code, "TR_BACK"), callback_data=callback_data
        )
    )
    return m


def set_prompt_undo_markup(locale, lang_code: str) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    m.add(
        types.InlineKeyboardButton(
            locale.find_translation(lang_code, "TR_UNDO"), callback_data="menu"
        )
    )
    return m


def default_prompt_actions_markup(locale, lang_code: str) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    t = lambda k: locale.find_translation(lang_code, k)
    m.add(types.InlineKeyboardButton(t("TR_BUTTOM_APPLY"), callback_data="apply_default_promt"))
    m.add(types.InlineKeyboardButton(t("TR_BACK"), callback_data="menu_promt"))
    return m


def help_menu_markup(locale, lang_code: str) -> types.InlineKeyboardMarkup:
    return back_only_markup(locale, lang_code, "menu")


def websearch_toggle_menu_markup(locale, lang_code: str, is_search: bool) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    t = lambda k: locale.find_translation(lang_code, k)
    if is_search:
        m.add(types.InlineKeyboardButton(t("TR_OFF"), callback_data="edit_websearch"))
    else:
        m.add(types.InlineKeyboardButton(t("TR_ON"), callback_data="edit_websearch"))
    m.add(types.InlineKeyboardButton(t("TR_BACK"), callback_data="menu_promt"))
    return m


def websearch_after_toggle_markup(locale, lang_code: str) -> types.InlineKeyboardMarkup:
    return back_only_markup(locale, lang_code, "menu_websearch")


def generate_image_cancel_markup(locale, lang_code: str) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    m.add(
        types.InlineKeyboardButton(
            locale.find_translation(lang_code, "TR_UNDO"), callback_data="menu"
        )
    )
    return m


def error_repeat_request_markup(locale, lang_code: str) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    m.add(
        types.InlineKeyboardButton(
            locale.find_translation(lang_code, "TR_REPEAT_REQUEST"),
            callback_data="errorPost ",
        )
    )
    return m


def vocalize_markup(locale, lang_code: str) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    m.add(
        types.InlineKeyboardButton(
            locale.find_translation(lang_code, "TR_VOCALIZE"), callback_data="sintez"
        )
    )
    return m


def prompt_applied_markup(locale, lang_code: str) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    t = lambda k: locale.find_translation(lang_code, k)
    m.add(types.InlineKeyboardButton(t("TR_BUTTOM_PROMT_NOW"), callback_data="show_my_promt"))
    m.add(types.InlineKeyboardButton(t("TR_MENU"), callback_data="menu"))
    return m


def payment_methods_markup(
    locale, lang_code: str, pay_buttons: dict, tarif_id: str, from_menu: bool
) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    for key, value in pay_buttons.items():
        m.add(types.InlineKeyboardButton(value, callback_data=key + "_" + str(tarif_id)))
    if from_menu:
        m.add(
            types.InlineKeyboardButton(
                locale.find_translation(lang_code, "TR_BACK"), callback_data="menu_premium"
            )
        )
    return m


def back_to_premium_markup(locale, lang_code: str) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    m.add(
        types.InlineKeyboardButton(
            locale.find_translation(lang_code, "TR_BACK"), callback_data="menu_premium"
        )
    )
    return m


def stars_invoice_markup(locale, lang_code: str, pay_description: str) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton(pay_description, pay=True))
    m.add(
        types.InlineKeyboardButton(
            locale.find_translation(lang_code, "TR_BACK"), pay=False, callback_data="menu_premium"
        )
    )
    return m


def external_payment_markup(
    locale, lang_code: str, pay_description: str, url_pay: str
) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton(pay_description, url=url_pay))
    m.add(
        types.InlineKeyboardButton(
            locale.find_translation(lang_code, "TR_BACK"), callback_data="menu_premium"
        )
    )
    return m


def premium_banned_markup(locale, lang_code: str) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    m.add(
        types.InlineKeyboardButton(
            locale.find_translation(lang_code, "TR_MENU"), callback_data="menu"
        )
    )
    return m


def tariff_list_markup(
    locale, lang_code: str, tariff_buttons: dict, include_menu_back: bool
) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup()
    for key, value in tariff_buttons.items():
        m.add(types.InlineKeyboardButton(value, callback_data=key))
    if include_menu_back:
        m.add(
            types.InlineKeyboardButton(
                locale.find_translation(lang_code, "TR_MENU"), callback_data="menu"
            )
        )
    return m


def support_message_markup(locale, lang_code: str) -> types.InlineKeyboardMarkup:
    return back_only_markup(locale, lang_code, "menu")
