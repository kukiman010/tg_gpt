import requests
import telebot
import speech
import base64
import sys
import os
import re
import datetime

from configure      import Settings
_setting = Settings()

import Gpt_models.yandexgpt
# import Gpt_models.sbergpt
import Gpt_models.metagpt
import Gpt_models.x_ai
import Gpt_models.google_api
import Gpt_models.claude_api
import Gpt_models.deepseak_api
import Control.context_model

from logger         import LoggerSingleton
from databaseapi    import dbApi
from telebot        import types
from translator     import Locale
from Gpt_models.gpt_api        import chatgpt
from data_models    import assistent_api
from data_models    import languages_api
from data_models    import tariffs_api
from payments.payment_manager import PaymentManager
from threading      import Lock


from blinker            import signal
from file_worker        import MediaWorker
from file_worker        import FileConverter
from Control.user       import User
from Control.user_media import UserMedia
from Control.environment import Environment
from apscheduler.schedulers.background import BackgroundScheduler

import signals
from core.callback_codec import CallbackCodec
from core.services.conversation_service import ConversationService
from core.services.user_service import UserService
from core.services.payment_service import PaymentService
from core.services.assistant_service import AssistantService
from transport.telegram import TelegramMessageOutput
from transport.telegram import ui as tg_ui


sys.stdout.reconfigure(encoding='utf-8')
_logger = LoggerSingleton.new_instance('logs/log_gpt.log')
locale = Locale('locale/LC_MESSAGES/')
_mediaWorker = MediaWorker.new_instance()
post_signal = signal('post_media')
# post_signal_payment = signal('finish_payment')
_converterFile = FileConverter()
_env = Environment()
_scheduler = None
_scheduler_lock = Lock()

_db = dbApi(
    dbname =    _setting.get_db_dbname(),
    user =      _setting.get_db_user(),
    password =  _setting.get_db_pass(),
    host =      _setting.get_db_host(),
    port =      _setting.get_db_port()
)


TOKEN_TG = _setting.get_tgToken()
TOKEN_GPT = _setting.get_cGptToken()
TOKEN_FOLDER_ID = _setting.get_yandex_folder()
TOKEN_META_GPT = _setting.get_meta_gpt()
TOKEN_XAI = _setting.get_xai_gpt()
TOKEN_CLAUDE = _setting.get_claude_gpt()
TOKEN_DEEPSEEK = _setting.get_deepseek_gpt()
TOKEN_YANDEX_API = _setting.get_yandex_api()
TOKEN_GOOGLE_API = _setting.get_google_api()
YOOMONEY_SHOP_ID = _setting.get_yoomoney_shopId()
TOKEN_YOOMONEY = _setting.get_yoomoney_token()


if TOKEN_TG == '':
    _logger.add_critical('No tg token!')
    sys.exit()

if TOKEN_GPT == '':
    _logger.add_critical('No gpts token!')
    sys.exit()

if TOKEN_FOLDER_ID == '':
    _logger.add_critical('No yandex folder id!')
    sys.exit()

if TOKEN_YANDEX_API == '':
    _logger.add_critical('No yandex api key!')
    sys.exit()

if TOKEN_META_GPT == '':
    _logger.add_critical('No meta gpt token!')
    sys.exit()

if TOKEN_CLAUDE == '':
    _logger.add_critical('No claude gpt token!')
    sys.exit()

if TOKEN_DEEPSEEK == '':
    _logger.add_critical('No deepseek gpt token!')
    sys.exit()

if TOKEN_GOOGLE_API == '':
    _logger.add_critical('No google gpt token!')
    sys.exit()

if YOOMONEY_SHOP_ID == '':
    _logger.add_critical('No yoomoney shop id!')
    sys.exit()

if TOKEN_YOOMONEY == '':
    _logger.add_critical('No yoomoney token!')
    sys.exit()



_env.update( _db.get_environment() )
if not _env.is_valid():
    _logger.add_critical('Environment is not corrected!')
    exit 


_speak = speech.speaker()
_speak.start_key_generation()
_assistent_api = assistent_api( _db.get_assistant_ai() )
_languages_api = languages_api( _db.get_languages() )
_tariffs_api =   tariffs_api(_db.get_tariffs())

try:
    bot = telebot.TeleBot( TOKEN_TG )
except requests.exceptions.ConnectionError as e:
    print("{} Ошибка подключения:".format(_speak.get_time_string()), e)
    _logger.add_error('нет соединения с сервером telegram bot: {}'.format(e))

_output = TelegramMessageOutput(bot, _logger)

_gpt = chatgpt(TOKEN_GPT)
_yag = Gpt_models.yandexgpt.YandexGpt( _speak.get_IAM(), TOKEN_FOLDER_ID)
_metaG = Gpt_models.metagpt.MetaGpt(TOKEN_META_GPT)
_xai = Gpt_models.x_ai.Xai(TOKEN_XAI)
# _sber = Gpt_models.sbergpt.Sber_gpt(_setting.get_sber_regData(), _setting.get_sber_guid(), _setting.get_sber_certificate())
# _sber.start_key_generation()
_claude = Gpt_models.claude_api.Claud(TOKEN_CLAUDE)
_deepseek = Gpt_models.deepseak_api.DeepSeek(TOKEN_DEEPSEEK)
_google = Gpt_models.google_api.Google(TOKEN_GOOGLE_API)

_conversation_service = ConversationService(
    _db,
    _speak,
    _logger,
    {
        "OpenAi": _gpt,
        "Yandex": _yag,
        "Meta": _metaG,
        "X ai": _xai,
        "Claude": _claude,
        "DeepSeek": _deepseek,
        "Google": _google,
    },
)
_user_service = UserService(_db, _env, _logger)
_payment_service = PaymentService(_db, _env, locale, _logger)
_assistant_service = AssistantService(_db, _assistent_api, _languages_api)


_payMan = PaymentManager( _env.get_global_payment())
_payMan.update(_db.get_payment_systems())
_payMan.start_auto_checker()





@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
    user = user_verification(message)
    username = str(message.chat.username)
    _db.delete_user_context(message.from_user.id, message.chat.id)
    t_mes = locale.find_translation(user.get_language(), 'TR_START_MESSAGE')
    bot.reply_to(message, t_mes.format(username) )
    


@bot.message_handler(commands=['dropcontext'])
def drop_context(message):
    user = user_verification(message)
    _db.delete_user_context(message.from_user.id, message.chat.id)
    t_mes = locale.find_translation(user.get_language(), 'TR_CLEAR_CONTEXT')
    bot.send_message(message.chat.id, t_mes )



@bot.message_handler(commands=['lastlog'])
def lastlog(message):
    user = user_verification(message)
    if _db.isAdmin(message.from_user.id, message.chat.username) == False:
        bot.send_message(message.chat.id, locale.find_translation(user.get_language(), 'TR_NO_PERMITION'))
        return
    
    words = message.text.split()

    if len(words) == 2:
        second_word = words[1]
        if second_word.isdigit():
            text = _logger.read_file_from_end(int(second_word))
            t_mes = locale.find_translation(user.get_language(), 'TR_GET_LOG')
            bot.send_message(message.chat.id, t_mes.format(second_word, text))

    elif len(words) == 3:
        second_word = words[1]
        type_log = words[2]

        if second_word.isdigit():
            text = _logger.read_file_from_end(int(second_word), type_log)
            t_mes = locale.find_translation(user.get_language(), 'TR_GET_LOG_POST')
            bot.send_message(message.chat.id, t_mes.format(second_word, type_log, text))
    else:
        t_mes = locale.find_translation(user.get_language(), 'TR_ERROR_SINTAX')
        bot.send_message(message.chat.id, t_mes)



@bot.message_handler(commands=['notify_all'])
def notify_all(message):
    user = user_verification(message)

    if _db.isAdmin(message.from_user.id, message.chat.username) == False:
        bot.send_message(message.chat.id, locale.find_translation(user.get_language(), 'TR_NO_PERMITION'))
        return

    data = _db.get_all_chat(message.from_user.id)
    text = message.text
    words = text.split()  
    result = ' '.join(words[1:]) 

    for i in data:  # итерация по внешнему списку
        for j in i:  # итерация по внутреннему списку
            for k in j:  # итерация по вложенному списку
                # print (k, result)
                bot.send_message(k, result)



@bot.message_handler(commands=['update_env'])
def update_environment (message):
    user = user_verification(message)
    chatId = message.chat.id
    if _db.isAdmin(message.from_user.id, message.chat.username) == False:
        bot.send_message(chatId, locale.find_translation(user.get_language(), 'TR_NO_PERMITION'))
        return

    mes = _env.show_differences(_db.get_environment(), locale.find_translation(user.get_language(), 'TR_NEW_OLD_CHANGES'))

    if mes:
        answer = locale.find_translation(user.get_language(), 'DATA_IS_NOT_RELEVANT').format(mes)
        _output.send_text(
            chatId,
            answer,
            reply_markup=tg_ui.env_update_confirm_markup(locale, user.get_language()),
        )
    else:
        _output.send_text(chatId, locale.find_translation(user.get_language(), 'TR_DATA_IS_UP_TO_DATE'))



@bot.message_handler(commands=['update_lang_models_pay'])
def update_data (message):
    user = user_verification(message)
    chatId = message.chat.id
    if _db.isAdmin(message.from_user.id, message.chat.username) == False:
        bot.send_message(chatId, locale.find_translation(user.get_language(), 'TR_NO_PERMITION'))
        return

    _logger.add_info("Запущено обновление переменных _payMan, _assistent_api, _languages_api, _scheduler")

    # update list pay system
    _payMan.update(_db.get_payment_systems())
    # update list model list
    _assistent_api.clear()
    _assistent_api.load_models( _db.get_assistant_ai() )
    # update list languages
    _languages_api.clear()
    _languages_api.load_models( _db.get_languages() )
    # update list tariffs
    _tariffs_api.clear()
    _tariffs_api.load_models( _db.get_tariffs() )
    # update timer check subscrube
    update_scheduler_time()

    _output.send_text(chatId, locale.find_translation(user.get_language(), 'TR_UPDATE_DATA'))

    


@bot.message_handler(commands=['help'])
def help(message):
    user = user_verification(message)
    text = command_help(user)
    _output.send_text(message.chat.id, text)



@bot.message_handler(commands=['premium'])
def premium(message):
    user = user_verification(message)
    if not user.is_valid():
        _output.send_text(message.chat.id, locale.find_translation(user.get_language(), 'TR_ERROR'))
        return 
    
    premium_button(user)



@bot.message_handler(commands=['img'])
def premium(message):
    user = user_verification(message)
    if not user.is_valid():
        _output.send_text(message.chat.id, locale.find_translation(user.get_language(), 'TR_ERROR'))
        return 
    generate_photo(user)
        


@bot.message_handler(commands=['settings'])
def settings(message):
    user = user_verification(message)
    main_menu(user, message.chat.id)
    


@bot.message_handler(commands=['assistantmode'])
def help(message):
    user = user_verification(message)

    if user == None or _assistent_api.size() == 0:
        _output.send_text(message.chat.id, locale.find_translation(user.get_language(), 'TR_ERROR_NOT_FIND_MODELS'))
        return
    
    buttons = _assistent_api.available_by_status()

    descrption_model = _assistent_api.get_description( user.get_model(), user.get_companyAi() )

    text = locale.find_translation(user.get_language(), 'TR_DESCRIPTION_MODELS').format(descrption_model, user.get_companyAi())
    _output.send_text(
        message.chat.id,
        text,
        reply_markup=tg_ui.assistant_select_markup(locale, user.get_language(), buttons),
    )



@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    user = user_verification(message)
    
    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = bot.download_file(file_path)

    filename = 'voice_{}_{}.ogg'.format(message.from_user.id, _speak.get_time_string())
    with open('./users_media/voice/' + filename, 'wb') as f:
        f.write(downloaded_file)

    text = _speak.recognize('./users_media/voice/' + filename)
    
    hasUser = _mediaWorker.find_userId(user.get_userId())
    media = UserMedia(user.get_userId(), message.chat.id, user.get_login() )

    if hasUser == False:
        t_mes = locale.find_translation(user.get_language(), 'TR_WAIT_POST')
        send_mess = bot.send_message(message.chat.id, t_mes)
        del_mes = UserMedia(user.get_userId(), message.chat.id, user.get_login() )
        del_mes.add_del_mess_id(send_mess.message_id)
        _mediaWorker.add_data(del_mes)

    media.add_mes(text)
    _mediaWorker.add_data(media)



@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    user = user_verification(message)

    action = user.get_wait_action()
    if action != '' and action != None and action != 'generate_image':
        action_handler(user.get_userId(), user, action, message.text)
        return


    hasUser = _mediaWorker.find_userId(user.get_userId())
    media = UserMedia(user.get_userId(), message.chat.id, user.get_login() )

    if hasUser == False:
        t_mes = locale.find_translation(user.get_language(), 'TR_WAIT_POST')
        send_mess = bot.send_message(message.chat.id, t_mes)
        del_mes = UserMedia(user.get_userId(), message.chat.id, user.get_login() )
        del_mes.add_del_mess_id(send_mess.message_id)
        _mediaWorker.add_data(del_mes)

    media.add_mes(message.text)
    _mediaWorker.add_data(media)



@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout_query(pre_checkout_query):
    label = pre_checkout_query.invoice_payload
    isDuplicate  = _db.checking_for_duplicate_payment(label)

    userId_pattern = r'^^PAY_(\d+)_\S+_\S+_\S+$'
    userId_match = re.match(userId_pattern, label)
    if userId_match:
        userId = userId_match.group(1)

    user = user_verification_easy(userId)

    if isDuplicate:
        t_mes= ''
        if user != None:
            t_mes = locale.find_translation(user.get_language(), 'TR_DUBLICATE_PAY')
        else:
            t_mes = locale.find_translation('en', 'TR_DUBLICATE_PAY')
            
        bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=False,
            error_message=t_mes
        )
        _output.send_text(user.get_userId(), t_mes )
        return
    else:
        bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)



@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    user = user_verification(message)
    payment_id = message.successful_payment.provider_payment_charge_id  
    amount = message.successful_payment.total_amount
    currency = message.successful_payment.currency
    label = message.successful_payment.invoice_payload
    result = _payment_service.process_success(user, payment_id, amount, currency, label)
    if not result.get("ok"):
        _output.send_text(user.get_userId(), result.get("error", locale.find_translation(user.get_language(), "TR_ERROR")))
        return
    _output.send_text(user.get_userId(), locale.find_translation(user.get_language(), "TR_SUCCESSFUL_PAYMENT"))



@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user = user_verification_custom(call.message.chat.id, call.message.message_id, call.message.chat.username, call.message.chat.type, call.from_user.language_code)    
    key = call.data
    cmd = CallbackCodec.decode(key)

    message_id = call.message.message_id
    chat_id = call.message.chat.id

    if key == 'menu':
        bot.answer_callback_query(call.id, text = '')
        main_menu(user, chat_id, message_id)
    elif key == 'sintez':
        text = call.message.text

        t_mes = locale.find_translation(user.get_language(), 'TR_START_DECODE_VOICE')
        bot.answer_callback_query(call.id, text = t_mes)

        files = _speak.speach(text, chat_id, 'alena')
        
        for file in files:
            with open(file, "rb") as audio:
                bot.send_audio(chat_id, audio)
            os.remove(file)

    elif key == "update_env":
        data_dict = _db.get_environment()
        mes = _env.show_differences(data_dict, locale.find_translation(user.get_language(), 'TR_NEW_OLD_CHANGES'))

        if mes:
            answer = locale.find_translation(user.get_language(), 'TR_CHANGES_HAVE_BEEN_APPLICED').format(mes)

            _env.update(data_dict)
            _output.send_text(chat_id, answer, id_message_for_edit=message_id)
            bot.answer_callback_query(call.id, locale.find_translation(user.get_language(), 'TR_SUCCESS'))
        else:
            _output.send_text(chat_id, locale.find_translation(user.get_language(), 'TR_DATA_IS_UP_TO_DATE'), id_message_for_edit=message_id)
            bot.answer_callback_query(call.id, locale.find_translation(user.get_language(), 'TR_FAILURE'))

    elif key == "no_update_env":
        _output.send_text(chat_id, locale.find_translation(user.get_language(), 'TR_TR_CHANGES_NOT_APPLICED'), id_message_for_edit=message_id)
        # bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
        bot.answer_callback_query(call.id, locale.find_translation(user.get_language(), 'TR_SUCCESS'))

    elif key == "menu_language":
        bot.answer_callback_query(call.id, text = '')
        if user == None or _languages_api.size() == 0:
            _output.send_text(chat_id, locale.find_translation(user.get_language(), 'TR_ERROR_NOT_CHANGE_LANGUAGE'))
            return
        t_mes = locale.find_translation(user.get_language(), 'TR_SELECT_LANGUAGE')
        
        buttons = _languages_api.available_by_status()
        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.language_menu_markup(locale, user.get_language(), buttons),
            id_message_for_edit=message_id,
        )

    elif key == 'menu_promt':
        bot.answer_callback_query(call.id, text = '')
        t_mes = locale.find_translation(user.get_language(), 'TR_SELECT_PROMT')
        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.prompt_menu_markup(locale, user.get_language()),
            id_message_for_edit=message_id,
        )

    elif key == 'menu_generate_image':
        bot.answer_callback_query(call.id, text = '')
        generate_photo(user, message_id)

    elif key == 'show_my_promt':
        bot.answer_callback_query(call.id, text = '')
        t_mes = locale.find_translation(user.get_language(), 'TR_SHOW_PROMT_NOW').format(user.get_prompt())
        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.back_only_markup(locale, user.get_language(), "menu_promt"),
            id_message_for_edit=message_id,
        )

    elif key == 'set_promt':
        bot.answer_callback_query(call.id, text = '')
        t_mes = locale.find_translation(user.get_language(), 'TR_SET_PROMT')
        _user_service.set_wait_action(user.get_userId(), "wait_new_prompt")
        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.set_prompt_undo_markup(locale, user.get_language()),
            id_message_for_edit=message_id,
        )

    elif key == 'set_default_promt':
        bot.answer_callback_query(call.id, text = '')
        t_mes = locale.find_translation(user.get_language(), 'TR_DEFAULT_PROMT').format(_env.get_prompt())
        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.default_prompt_actions_markup(locale, user.get_language()),
            id_message_for_edit=message_id,
        )

    elif key == 'apply_default_promt': 
        bot.answer_callback_query(call.id, text = locale.find_translation(user.get_language(), 'TR_SUCCESS'))
        t_mes = locale.find_translation(user.get_language(), 'TR_PROMT_APPLY')
        _db.update_user_prompt(user.get_userId(), _env.get_prompt())
        _output.send_text(chat_id, t_mes, id_message_for_edit=message_id)

    elif key == 'menu_help':
        bot.answer_callback_query(call.id, text = '')
        text = command_help(user)
        _output.send_text(
            chat_id,
            text,
            reply_markup=tg_ui.help_menu_markup(locale, user.get_language()),
            id_message_for_edit=message_id,
        )

    elif key == 'menu_premium':
        premium_button(user, message_id)

    elif key == 'menu_support':
        bot.answer_callback_query(call.id, text = '')
        t_mes = locale.find_translation(user.get_language(), 'TR_MESSAGE_SUPPORT').format(user.get_prompt())
        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.support_message_markup(locale, user.get_language()),
            id_message_for_edit=message_id,
        )
    
    elif key == 'menu_websearch':
        bot.answer_callback_query(call.id, text = '')
        if user.get_is_search():
            t_mes = locale.find_translation(user.get_language(), 'TR_TITLE_WEBSEARCH_ON')
        else:
            t_mes = locale.find_translation(user.get_language(), 'TR_TITLE_WEBSEARCH_OFF')
        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.websearch_toggle_menu_markup(
                locale, user.get_language(), user.get_is_search()
            ),
            id_message_for_edit=message_id,
        )

    elif key == 'edit_websearch':
        bot.answer_callback_query(call.id, text = locale.find_translation(user.get_language(), 'TR_SUCCESS'))

        if user.get_is_search():
            _db.update_user_search_status(user.get_userId(), False)
            t_mes = locale.find_translation(user.get_language(), 'TR_WEBSEARCH_OFF')
        else:
            _db.update_user_search_status(user.get_userId(), True)
            t_mes = locale.find_translation(user.get_language(), 'TR_WEBSEARCH_ON')

        _output.send_text(
            chat_id,
            t_mes,
            reply_markup=tg_ui.websearch_after_toggle_markup(locale, user.get_language()),
            id_message_for_edit=message_id,
        )

    # elif key == 'menu_think':

    # elif key == 'menu_locate':
    #     bot.answer_callback_query(call.id, text = '')
    #     t_mes = locale.find_translation(user.get_language(), 'TR_DONT_RELEASES_FUNC').format(user.get_prompt())
    #     markup = types.InlineKeyboardMarkup()
    #     markup.add( types.InlineKeyboardButton(locale.find_translation(user.get_language(), 'TR_BACK'),                callback_data='menu',request_location=True) )
    #     _output.send_text(chat_id, t_mes, reply_markup=markup, id_message_for_edit=message_id)


    elif key == 'errorPost':
        text = call.message.text
        bot.edit_message_reply_markup(chat_id, message_id)
        hasUser = _mediaWorker.find_userId(user.get_userId())
        media = UserMedia(user.get_userId(), chat_id, user.get_login() )

        if hasUser == False:
            t_mes = locale.find_translation(user.get_language(), 'TR_WAIT_POST')
            send_mess = bot.send_message(chat_id, t_mes)
            del_mes = UserMedia(user.get_userId(), chat_id, user.get_login() )
            del_mes.add_del_mess_id(send_mess.message_id)
            _mediaWorker.add_data(del_mes)

        media.add_mes(call.message)
        _mediaWorker.add_data(media)

    elif cmd.action == "assistant_select":
        idx = int(cmd.args["id"])

        if not _assistant_service.can_use_assistant(idx, user.get_status()):
            bot.send_message(chat_id, locale.find_translation(user.get_language(), 'TR_NEED_PREMIUM_ASSISTANT'))
            bot.answer_callback_query(call.id, locale.find_translation(user.get_language(), 'TR_NEED_PERMISSION'))
            return

        _assistant_service.set_assistant(user, idx)
        
        bot.send_message(chat_id, locale.find_translation(user.get_language(), 'TR_USE_NEW_ASSISTANT'))
        bot.answer_callback_query(call.id, locale.find_translation(user.get_language(), 'TR_SUCCESS'))

    elif cmd.action == "language_select":
        idx = int(cmd.args["id"])
        code_lang = _assistant_service.set_language_by_button(user, idx)
        if locale.islanguage( code_lang ):
            bot.send_message(chat_id, locale.find_translation(code_lang, 'TR_SYSTEM_LANGUAGE_CHANGE'))
            bot.answer_callback_query(call.id, locale.find_translation(code_lang, 'TR_SUCCESS'))
        else:
            bot.send_message(chat_id, locale.find_translation(user.get_language(), 'TR_SYSTEM_LANGUAGE_SUPPORT'))
            bot.answer_callback_query(call.id, locale.find_translation(user.get_language(), 'TR_FAILURE'))

    elif cmd.action == "payment_select":
        bot.answer_callback_query(call.id, text = locale.find_translation(user.get_language(), 'TR_SUCCESS'))
        paymet_system = cmd.args["system"]
        tarif_id = cmd.args["tariff_id"]
        
        
        
        tariffs_data = None
        tarifs_data = _db.get_tariffs(tarif_id)
        for node in tarifs_data:
            if node.tariff_id == int(tarif_id):
                tariffs_data = node

        if tariffs_data == None:
            _output.send_text(
                chat_id,
                locale.find_translation(user.get_language(), 'TR_TARRIF_DONT_LOAD'.format(_env.get_support_chat())),
                reply_markup=tg_ui.back_to_premium_markup(locale, user.get_language()),
                id_message_for_edit=message_id,
            )
            return

        description = locale.find_translation(user.get_language(), 'TR_SUBSCRIBE_FOR_ONE_MOUNTH').format(tariffs_data.activity_day)

        if paymet_system == 'TelegramStarsPay':
            # price = _payMan.convector.usd_to_tgStars(price_in_usd)
            # price = _payMan.convector.custom_round(price)

            label = _payMan.generate_payment_label(user.get_userId())

            pay_description = locale.find_translation(user.get_language(), 'TR_PAY').format(tariffs_data.price_stars, ' stars')
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
                reply_markup=markup
            )
            bot.delete_message(chat_id, message_id)

            _db.add_invoice_journal(user.get_userId(), label, label, tarif_id, 'pending', tariffs_data.price_stars, 'XTR', paymet_system, description, datetime.datetime.now( datetime.timezone(datetime.timedelta(hours=3)) ), False)
            

        else:
            # if user.get_language() == 'ru':
            pay_info = _payMan.create_invoice(paymet_system, int(tariffs_data.price_rub), 'RUB', user.get_userId(), description)

            pay_info.tarrif = tarif_id
            pay_info.user_name = user.get_login()

            if pay_info.status == 'pending':
                _db.add_invoice_journal(pay_info.user_id, pay_info.payment_id, pay_info.label_pay, pay_info.tarrif, pay_info.status, pay_info.amount, pay_info.currency, pay_info.payment_system, pay_info.description, pay_info.created_at, pay_info.is_test)
                _payMan.add_payment(pay_info)

                pay_description = locale.find_translation(user.get_language(), 'TR_PAY').format(pay_info.amount, pay_info.currency)
                markup = tg_ui.external_payment_markup(
                    locale, user.get_language(), pay_description, pay_info.url_pay
                )
                _output.send_text(chat_id, description, reply_markup=markup, id_message_for_edit=message_id)

    elif cmd.action == "tariff_select":
        code_tariff = _tariffs_api.find_bottom(int(cmd.args["id"]))

        tariffs = _db.get_tariffs()

        for node in tariffs:
            if node.tariff_id == code_tariff:
                pay_button(user, True, node.tariff_id, node.description_code, message_id)
                break

    elif cmd.action == "check_payment":
        payment_id = cmd.args["payment_id"]
        print()


    else:
        t_mes = locale.find_translation(user.get_language(), 'TR_ERROR')
        bot.answer_callback_query(call.id, text = t_mes)
    


@bot.message_handler(content_types=['document'])
def handle_docs(message):
    user = user_verification(message)
    file_size = message.document.file_size

    if file_size > int(_env.get_sum_max_file_size()):
        bot.reply_to(message, "Размер файла превышает допустимый лимит в 1MB.")
    else:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            name = 'file_{}_{}.date'.format(message.from_user.id, _speak.get_time_string())
            with open(os.path.join('users_media/files/', f'{name}'), 'wb') as new_file:
                new_file.write(downloaded_file)


            hasUser = _mediaWorker.find_userId(user.get_userId())
            media = UserMedia(user.get_userId(), message.chat.id, user.get_login() )

            if hasUser == False:
                t_mes = locale.find_translation(user.get_language(), 'TR_WAIT_POST')
                send_mess = bot.send_message(message.chat.id, t_mes)
                del_mes = UserMedia(user.get_userId(), message.chat.id, user.get_login() )
                del_mes.add_del_mess_id(send_mess.message_id)
                _mediaWorker.add_data(del_mes)

            if message.caption != None:
                media_text = UserMedia(user.get_userId(), message.chat.id, user.get_login() )
                media_text.add_mes(message.caption)
                _mediaWorker.add_data(media_text)

            media.add_document(name, message.document.file_name, file_size)
            _mediaWorker.add_data(media)

        except Exception as e:
            bot.reply_to(message, f'Произошла ошибка при обработке файла: {e}')



@bot.message_handler(content_types=['photo'])
def handle_message(message):
    user = user_verification(message)

    if user.get_status() < 2:
        _output.send_text(message.chat.id, locale.find_translation(user.get_language(), 'TR_NEED_PERMISSION_UPLOAD_PHOTO'))
        return

    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    
    downloaded_file = bot.download_file(file_info.file_path)
    
    name = 'photo_{}_{}.jpg'.format(message.from_user.id, _speak.get_time_string())
    with open(os.path.join('users_media/photos/', f'{name}'), 'wb') as new_file:
        new_file.write(downloaded_file)
    

    hasUser = _mediaWorker.find_userId(user.get_userId())
    media = UserMedia(user.get_userId(), message.chat.id, user.get_login() )

    if hasUser == False:
        t_mes = locale.find_translation(user.get_language(), 'TR_WAIT_POST')
        send_mess = bot.send_message(message.chat.id, t_mes)
        del_mes = UserMedia(user.get_userId(), message.chat.id, user.get_login() )
        del_mes.add_del_mess_id(send_mess.message_id)
        _mediaWorker.add_data(del_mes)

    media = UserMedia(user.get_userId(), message.chat.id, user.get_login() )

    if message.caption:
        media.add_photo(str('users_media/photos/'+ name), name, file_info.file_size, message.caption)
    else:
        media.add_photo(str('users_media/photos/'+ name), name, file_info.file_size)
        
    # media.add_photo(name, str('users_media/photos/'+ name), file_info.file_size, message.caption)
    _mediaWorker.add_data(media)




def user_verification(message) -> User:
    return _user_service.verify_from_message(message)



def user_verification_custom(userId, chatId, chat_username, chatType, lang_code):
    return _user_service.verify_custom(userId, chatId, chat_username, chatType, lang_code)



def user_verification_easy(userId) -> User:
    return _user_service.verify_easy(userId)


def mergeConversationContext(chatId, user:User, text_to_photo, photos, generate_image:bool = False): # -> list[str], bool:
    return _conversation_service.merge_context(chatId, user, text_to_photo, photos, generate_image)


def poat_generate_image(user:User, json, model) -> Control.context_model.AnswerAssistent :
    model="gpt-4.1"
    return _conversation_service.post_generate_image(user, json, model)

def poat_vision_gpt(user:User, json, model) -> Control.context_model.AnswerAssistent :
    model = "gpt-4o"
    return _conversation_service.post_vision(json, model)


def post_gpt(user:User, json, model) -> Control.context_model.AnswerAssistent :
    return _conversation_service.post_chat(user, json, model)


def generate_photo(user:User, id_message_for_edit:int = 0):
    t_mes = locale.find_translation(user.get_language(), "TR_GEN_IMAGE_DESCRIPTION")
    _user_service.set_wait_action(user.get_userId(), "generate_image")

    if id_message_for_edit > 0:
        _output.send_text(
            user.get_userId(),
            t_mes,
            reply_markup=tg_ui.generate_image_cancel_markup(locale, user.get_language()),
            id_message_for_edit=id_message_for_edit,
        )
    else:
        _output.send_text(user.get_userId(), t_mes)



def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  


def on_post_media(sender, userId, mediaList: list[UserMedia]):
    message = ''
    textMes = ''
    chatId = ''
    titleMessId = []
    photos = []
    isPhotos:bool = False
    for media in mediaList:
        if chatId == '':
            chatId = media._chatId
        
        if media._type == "document":
            message += _converterFile.convert_files_to_text('users_media/files/{}'.format(media._fileWay), media._fileName)
            os.remove('users_media/files/{}'.format(media._fileWay))
        if media._type == "message":
            textMes += media._mediaData
        if media._type == "titleId":
            titleMessId.append( media._titleId)
        if media._type == 'photo':
            photos.append( encode_image(media._fileWay))
            if media._mediaData:
                textMes += media._mediaData
            isPhotos = True

        message = textMes + '\n' + message
        
    if chatId == '':
        chatId = userId
    
    # print( "\n\n" + message)

    user = user_verification_easy(userId)

    if user == None:
        return

    _db.update_last_login(userId)

    action = user.get_wait_action()

    generate_image = False
    if action == 'generate_image':
        generate_image = True
    
    json, boolPhotoResult = mergeConversationContext(chatId, user, message, photos, generate_image)

    action = user.get_wait_action()

    if generate_image:
        content = poat_generate_image(user, json, user.get_model_generate_photo())
        _user_service.reset_action(user.get_userId())
    elif isPhotos or boolPhotoResult:
        content = poat_vision_gpt(user, json, user.get_model())
    else:
        content = post_gpt(user, json, user.get_model())


    if content and content.get_code() == 200:
        _db.add_context(user.get_userId(), chatId, "user",          chatId,     message)
        for photo_to_base64 in photos:
            _db.add_context(user.get_userId(), chatId, "user",      chatId,     photo_to_base64,        True)
        _db.add_context(user.get_userId(), chatId, "assistant",     chatId,     content.get_result())

        
    MAX_CHAR = int(_env.get_count_char_for_gen_audio())

    if len(titleMessId) != 0:
        for medId in titleMessId:
            _output.delete_message(chatId, medId)

    if not content.get_result() or content.get_code() >= 300:
        _output.send_text(
            chatId,
            locale.find_translation(user.get_language(), 'TR_ERROR_GET_RESULT').format(content.get_result()),
            reply_markup=tg_ui.error_repeat_request_markup(locale, user.get_language()),
            isMarkdown=True,
        )
        return

    if len(content.get_result()) <= MAX_CHAR:
        _output.send_text(
            chatId,
            content.get_result(),
            reply_markup=tg_ui.vocalize_markup(locale, user.get_language()),
            isMarkdown=True,
        )
    else:    
        _output.send_text(chatId, content.get_result(), isMarkdown=True)



def on_finish_payment(sender, userId, data):
    if sender != 'PaymentManager':
        _logger.add_critical('Сигнал on_finish_payment инициализирован {}, а не PaymentManager'.format(sender))
        return
    
    result = _payment_service.process_finished_payment_signal(userId, data, user_verification_easy)
    if not result.get("ok"):
        _logger.add_critical("Не удалось обработать payment signal для user {}".format(userId))
        return
    lang = result.get("notify_lang", "en")
    _output.send_text(userId, locale.find_translation(lang, "TR_SUCCESSFUL_PAYMENT"))
    


def main_menu(user, charId, id_message = None):
    t_mes = locale.find_translation(user.get_language(), 'TR_SETTING')
    
    if user.get_wait_action() == 'wait_new_prompt':
        _user_service.reset_action(user.get_userId())

    _output.send_text(
        charId,
        t_mes,
        reply_markup=tg_ui.main_menu_markup(locale, user.get_language()),
        id_message_for_edit=id_message,
    )
    


def action_handler(chatId, user, action, text):
    if action == 'wait_new_prompt':
        _user_service.apply_prompt_action(user, text)

        t_mes = locale.find_translation(user.get_language(), 'TR_PROMT_APPLY')
        _output.send_text(
            chatId,
            t_mes,
            reply_markup=tg_ui.prompt_applied_markup(locale, user.get_language()),
        )

    else:
        _user_service.reset_action(user.get_userId())
        _logger.add_critical('There is no processing of such a scenario: {}, the action will be reset'.format(action))



def command_help(user):
    if not user.is_valid():
        return locale.find_translation(user.get_language(), 'TR_ERROR')

    text = locale.find_translation(user.get_language(), 'TR_GET_HELP')

    if _db.isAdmin(user.get_userId(), user.get_login()) == True:
        text += locale.find_translation(user.get_language(), 'TR_GET_HELP_ADMIN')

    return text



def pay_button(user: User, callFromMenu: bool, tarif_id: str, tarif_description = 'TR_TARIFF_ONCE', id_message_for_edit : int = 0):
    buttons = _payMan.get_buttons()

    have_sub, hours = _db.its_have_this_subscribe(user.get_userId(), tarif_id, datetime.datetime.now( datetime.timezone(datetime.timedelta(hours=3)) ))

    if len(buttons) > 0:
        if have_sub:
            text = locale.find_translation(user.get_language(), 'TR_SUBSCRIPTION_RENEWAL').format(round(hours / 24, 1))
        else:
            text = locale.find_translation(user.get_language(), tarif_description)

        markup = tg_ui.payment_methods_markup(
            locale, user.get_language(), buttons, str(tarif_id), callFromMenu
        )

        if callFromMenu:
            _output.send_text(user.get_userId(), text, reply_markup=markup, id_message_for_edit=id_message_for_edit)
        else:
            _output.send_text(user.get_userId(), text, reply_markup=markup)
        
    else:
        _output.send_text(user.get_userId(), locale.find_translation(user.get_language(), 'TR_PAYMENT_SYSTEM_EMPTY') )



def premium_button(user: User, id_message_for_edit : int = 0):
    if user.get_status() == 0: 
        if id_message_for_edit != 0:
            _output.send_text(
                user.get_userId(),
                locale.find_translation(user.get_language(), 'TR_PAYMENT_LOCK_FOR_BANED_USER'),
                reply_markup=tg_ui.premium_banned_markup(locale, user.get_language()),
            )
        else:
            _output.send_text(user.get_userId(), locale.find_translation(user.get_language(), 'TR_PAYMENT_LOCK_FOR_BANED_USER'))
        return

    code_lang = user.get_language()
    tarifs = _db.get_tariffs()
    rub_countries = {
        'RU',  # Россия
        'UZ',  # Узбекистан
        'TJ',  # Таджикистан
        'KG',  # Кыргызстан
        'AM',  # Армения
        'AZ',  # Азербайджан
        'KZ',  # Казахстан
        'UA',  # Украина
        'BY',  # Беларусь
        'MD',  # Молдова
    }

    main_currency = ''
    if code_lang.upper() in rub_countries:
        main_currency = 'RUB'
    else:
        main_currency = 'USD'
    
    text_tarifs = ''

    t_all = locale.find_translation(user.get_language(), 'TR_TARIF_ALL')
    for node in tarifs:
        if node.tariff_name != None:
            
            if node.price_rub <= 0 and node.price_usd <= 0 and node.price_stars <= 0:
                continue
            
            config_tarif = ''

            for key, value in node.rules_json.items():
                if value == "all":
                    config_tarif += key + ': ' + t_all + '\n'
                elif isinstance(value, list):
                    config_tarif += key + ': ' + value + '\n'


            if node.price_usd  <= 0:
                node.price_usd = _payMan.convector.custom_round(node.price_rub / _payMan.convector.usd_to_rub(1))

            if node.price_stars <= 0:
                node.price_stars = _payMan.convector.custom_round( _payMan.convector.usd_to_tgStars(node.price_usd) )


            main_price = ''
            if main_currency == 'RUB':
                main_price = str(node.price_rub) + '₽'
            else:
                main_price = str(node.price_usd) + '$'

            if config_tarif:
                text_tarifs += locale.find_translation(user.get_language(), 'TR_TARIF_PATERN').format(node.tariff_name, config_tarif, main_price, str(node.price_stars) + '⭐️', node.activity_day) + '\n'
            else:
                text_tarifs += locale.find_translation(user.get_language(), 'TR_TARIF_PATERN_EMPTY').format(node.tariff_name, main_price, str(node.price_stars) + '⭐️', node.activity_day) + '\n'


    buttons = _tariffs_api.available_by_status()
    markup = tg_ui.tariff_list_markup(
        locale, user.get_language(), buttons, id_message_for_edit != 0
    )
    
    t_mes = locale.find_translation(user.get_language(), 'TR_TARIFFS_MENU').format(text_tarifs)
    _output.send_text(user.get_userId(), t_mes, reply_markup=markup)
    if id_message_for_edit != 0:
        _output.delete_message(user.get_userId(), id_message_for_edit)



def subscription_verification():
    tz_moscow = datetime.timezone(datetime.timedelta(hours=3))
    data_now = datetime.datetime.now(tz_moscow)

    list = _db.get_subscription_users()

    for userSub in list:
        data_until = userSub.active_until
        if data_until < data_now:
            userId = userSub.userId

            user = user_verification_easy(userId)

            _db.update_invoice_journal(userSub.last_label, userSub.last_label, 'subscription ended', None , None, 0, datetime.datetime.now(tz_moscow))
            _db.remove_subscription_ended(userSub.last_label)
            _db.update_status_in_users(userId, 1)

            text = locale.find_translation(user.get_language(), 'TR_SUBSCRIPRION_ENDED')
            _output.send_text(userId, text)

        else:
            continue



def start_or_restart_scheduler(hour: int, minute: int):
    global _scheduler
    with _scheduler_lock:
        # Остановить старый планировщик, если есть
        if _scheduler:
            _scheduler.remove_all_jobs()
            _scheduler.shutdown(wait=False)
        
        _scheduler = BackgroundScheduler(timezone="Europe/Moscow")
        _scheduler.add_job(subscription_verification, 'cron', hour=hour, minute=minute)
        _scheduler.start()



def update_scheduler_time():
    data_dict = _db.get_environment()
    time_str = data_dict.get("check_premium")
    if time_str == None:
        time_str = _env.get_check_premium()  
        
    hour, minute = map(int, time_str.split(':'))
    start_or_restart_scheduler(hour, minute)



try:
    subscription_verification()
    update_scheduler_time() 

    post_signal.connect(on_post_media, sender='MediaWorker')
    signals.finish_payment.connect(on_finish_payment, sender='PaymentManager')
    bot.infinity_polling()    
    # bot.polling()
except requests.exceptions.ConnectionError as e:
    print("{} Ошибка подключения:".format(_speak.get_time_string()), e)
    _logger.add_error('нет соединения с сервером telegram bot: {}'.format(e))


