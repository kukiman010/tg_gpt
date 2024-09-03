import requests
import telebot
import speech
import base64
import sys
import os
import re

import Gpt_models.yandexgpt
import Gpt_models.sbergpt
import Gpt_models.metagpt
# import Gpt_models.googlegpt
import Control.context_model

from logger         import LoggerSingleton
from openai         import OpenAIError
from configure      import Settings
from databaseapi    import dbApi
from telebot        import types
from translator     import Locale
from Control.user   import User
from Gpt_models.gpt_api        import chatgpt
from data_models    import assistent_api
from data_models    import languages_api


from blinker            import signal
from file_worker        import MediaWorker
from file_worker        import FileConverter
from Control.user_media import UserMedia


_setting = Settings()
sys.stdout.reconfigure(encoding='utf-8')
_logger = LoggerSingleton.new_instance('log_gpt.log')
locale = Locale('locale/LC_MESSAGES/')
_mediaWorker = MediaWorker.new_instance()
post_signal = signal('post_media')
_converterFile = FileConverter()

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


if TOKEN_TG == '':
    print ('no tg token!')
    _logger.add_critical('no tg token!')
    sys.exit()

if TOKEN_GPT == '':
    print ('no gpts token!')
    _logger.add_critical('no gpts token!')
    sys.exit()

if TOKEN_FOLDER_ID == '':
    print ('no yandex folder id!')
    _logger.add_critical('no yandex folder id!')
    sys.exit()

if TOKEN_META_GPT == '':
    print ('no meta gpt token!')
    _logger.add_critical('no meta gpt toke!')
    sys.exit()

_speak = speech.speaker(TOKEN_FOLDER_ID)
if _speak.get_IAM() == '':
    print ('no yandex iam token!')
    _logger.add_critical('no yandex iam token!')
    sys.exit()


_speak.start_key_generation()
_assistent_api = assistent_api( _db.get_assistant_ai() )
_languages_api = languages_api( _db.get_languages() )

try:
    bot = telebot.TeleBot( TOKEN_TG )
except requests.exceptions.ConnectionError as e:
    print("{} Ошибка подключения:".format(_speak.get_time_string()), e)
    _logger.add_error('нет соединения с сервером telegram bot: {}'.format(e))

_gpt = chatgpt(TOKEN_GPT, TOKEN_FOLDER_ID)
_yag = Gpt_models.yandexgpt.YandexGpt( _speak.get_IAM(), TOKEN_FOLDER_ID)
_metaG = Gpt_models.metagpt.MetaGpt(TOKEN_META_GPT)
_sber = Gpt_models.sbergpt.Sber_gpt(_setting.get_sber_regData(), _setting.get_sber_guid(), _setting.get_sber_certificate())
_sber.start_key_generation()






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
def drop_context(message):
    user = user_verification(message)
    if _db.isAdmin(message.from_user.id, message.chat.username) == False:
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
    user_verification(message)

    if _db.isAdmin(message.from_user.id, message.chat.username) == False:
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


@bot.message_handler(commands=['help'])
def help(message):
    user_verification(message)

    text = "Коротко о софте:\nОтветы генерируются при помощи GPT. По умолчанию используется модель gpt-3.5-turbo.\nРаспознавание и генерация голосовых сообщений осуществляется при помощи Yandex SpeechKit v1 (позже перейдем на v3).\n\nКоманды:\n/dropcontext - удаляет весь контекст переписки."

    if _db.isAdmin(message.from_user.id, message.chat.username) == True:
        text_admin = "\n\nДоступно только для админа! будь аккуратнее с командами\n/notify_all <текст> - Эта команда отправит во все чаты твой текст, прошу, будь аккуратнее\nТут будут еще команды ..."
        text += text_admin

    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['premium'])
def premium(message):
    user = user_verification(message)
    bot.send_message(message.chat.id, locale.find_translation(user.get_language(), 'TR_DONT_RELEASES_FUNC'))

@bot.message_handler(commands=['settings'])
def settings(message):
    user = user_verification(message)
    t_mes = locale.find_translation(user.get_language(), 'TR_SETTING')

    if user == None or _languages_api.size() == 0:
        bot.send_message(message.chat.id, locale.find_translation(user.get_language(), 'TR_ERROR_NOT_CHANGE_LANGUAGE'))
        return
    
    buttons = _languages_api.available_by_status()
    markup = types.InlineKeyboardMarkup()
    for key, value in buttons.items():
        but = types.InlineKeyboardButton(value, callback_data=key)
        markup.add(but)

    bot.send_message(message.chat.id, t_mes, reply_markup=markup)
    

@bot.message_handler(commands=['assistantmode'])
def help(message):
    user = user_verification(message)

    if user == None or _assistent_api.size() == 0:
        bot.send_message(message.chat.id, locale.find_translation(user.get_language(), 'TR_ERROR_NOT_FIND_MODELS'))
        return
    
    buttons = _assistent_api.available_by_status()

    markup = types.InlineKeyboardMarkup()
    for key, value in buttons.items():
        but = types.InlineKeyboardButton(value, callback_data=key)
        markup.add(but)

    text = locale.find_translation(user.get_language(), 'TR_DESCRIPTION_MODELS').format(user.get_model(), user.get_companyAi())
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    user = user_verification(message)
    
    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = bot.download_file(file_path)

    filename = 'voice_{}_{}.ogg'.format(message.from_user.id, _speak.get_time_string())
    with open('./voice/' + filename, 'wb') as f:
        f.write(downloaded_file)

    text = _speak.voice_text_v1(downloaded_file, message.from_user.id)
    # text = _speak.voice_text_v3(downloaded_file, message.from_user.id)
    
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
    # TODO: добавить возможность записи длинных голосовых сообщений(v3)



@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    user = user_verification(message)
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




@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user = user_verification_custom(call.message.chat.id, call.message.message_id, call.message.chat.username, call.message.chat.type, call.from_user.language_code)    
    key = call.data
    assistent_pattern = r'^set_model_(\d+)$'
    assistent_match = re.match(assistent_pattern, key)
    
    language_pattern = r'^set_lang_model_(\d+)$'
    language_match = re.match(language_pattern, key)

    if key == 'sintez':
        text = call.message.text

        t_mes = locale.find_translation(user.get_language(), 'TR_START_DECODE_VOICE')
        bot.answer_callback_query(call.id, text = t_mes)

        # file = _speak.voice_synthesis_v1(text, call.message.chat.id)
        file = _speak.voice_synthesis_v3(text, call.message.chat.id)
        # file = _speak.synthesize(text)
        
        with open(file, "rb") as audio:
            bot.send_audio(call.message.chat.id, audio)

        os.remove(file)

    elif key == 'errorPost':
        text = call.message.text
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        hasUser = _mediaWorker.find_userId(user.get_userId())
        media = UserMedia(user.get_userId(), call.message.chat.id, user.get_login() )

        if hasUser == False:
            t_mes = locale.find_translation(user.get_language(), 'TR_WAIT_POST')
            send_mess = bot.send_message(call.message.chat.id, t_mes)
            del_mes = UserMedia(user.get_userId(), call.message.chat.id, user.get_login() )
            del_mes.add_del_mess_id(send_mess.message_id)
            _mediaWorker.add_data(del_mes)

        media.add_mes(call.message)
        _mediaWorker.add_data(media)

    elif assistent_match:
        id = int(assistent_match.group(1))
        assistent = _assistent_api.find_assistent(id)

        if not _assistent_api.isAvailable(id, user.get_status()):
            bot.send_message(call.message.chat.id, locale.find_translation(user.get_language(), 'TR_NEED_PREMIUM_ASSISTANT'))
            bot.answer_callback_query(call.id, locale.find_translation(user.get_language(), 'TR_NEED_PERMISSION'))
            return

        for first, second in assistent.items():
            _db.update_user_assistent(user.get_userId(),second,first ) 
            break
        
        bot.send_message(call.message.chat.id, locale.find_translation(user.get_language(), 'TR_USE_NEW_ASSISTANT'))
        bot.answer_callback_query(call.id, locale.find_translation(user.get_language(), 'TR_SUCCESS'))

    elif language_match:
        id = int(language_match.group(1))
        code_lang = _languages_api.find_bottom(id)
        if locale.islanguage( code_lang ):
            _db.update_user_lang_code(user.get_userId(), code_lang)
            bot.send_message(call.message.chat.id, locale.find_translation(code_lang, 'TR_SYSTEM_LANGUAGE_CHANGE'))
            bot.answer_callback_query(call.id, locale.find_translation(code_lang, 'TR_SUCCESS'))
        else:
            bot.send_message(call.message.chat.id, locale.find_translation(user.get_language(), 'TR_SYSTEM_LANGUAGE_SUPPORT'))
            bot.answer_callback_query(call.id, locale.find_translation(user.get_language(), 'TR_FAILURE'))

    else:
        t_mes = locale.find_translation(user.get_language(), 'TR_ERROR')
        bot.answer_callback_query(call.id, text = t_mes)
    


@bot.message_handler(content_types=['document'])
def handle_docs(message):
    user = user_verification(message)
    file_size = message.document.file_size

    MAX_FILE_SIZE = _db.get_max_file_size()

    if file_size > MAX_FILE_SIZE:
        bot.reply_to(message, "Размер файла превышает допустимый лимит в 1MB.")
    else:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            name = 'file_{}_{}.date'.format(message.from_user.id, _speak.get_time_string())
            with open(os.path.join('files/', f'{name}'), 'wb') as new_file:
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

    if user.get_status() != 2:
        bot.send_message(message.chat.id, locale.find_translation(user.get_language(), 'TR_NEED_PERMISSION_UPLOAD_PHOTO'))
        return

    t_mes = locale.find_translation(user.get_language(), 'TR_WAIT_POST')
    send_mess = bot.send_message(message.chat.id, t_mes)

    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    
    downloaded_file = bot.download_file(file_info.file_path)
    
    
    name = 'photo_{}_{}.jpg'.format(message.from_user.id, _speak.get_time_string())
    with open(os.path.join('photos/', f'{name}'), 'wb') as new_file:
        new_file.write(downloaded_file)
    
    base64_image = encode_image(f'photos/{name}')

    text_to_photo = message.caption

    if text_to_photo == '' or text_to_photo == None:
        text_to_photo = 'What’s in this image?'



    mes = Control.context_model.Context_model()
    mes_photo = Control.context_model.Context_model()
    mes.set_data(message.from_user.id, message.chat.id,"user",message.message_id,text_to_photo,False )
    mes_photo.set_data(message.from_user.id, message.chat.id,"user",message.message_id,base64_image,True )

    dict = _db.get_context(user.get_userId(), message.chat.id)
    dict.append(mes)
    dict.append(mes_photo)
    json = Control.context_model.convert(user.get_companyAi(), dict, True)

    content = ""
    # tokenSizeNow = 0
    model = "gpt-4-vision-preview"

    # if str(user.get_companyAi()).upper() == str("OpenAi").upper():
        # tokenSizeNow = _gpt.num_tokens_from_messages(json, model)

    maxToken = _assistent_api.getToken(model)

    # if tokenSizeNow > maxToken:
    #     markup = types.InlineKeyboardMarkup()
    #     markup.add( types.InlineKeyboardButton('Повторить запрос', callback_data='errorPost') )
    #     text = "Извините, но ваш запрос привышает максималтную длинну контекста.\nВаш запрос: {}\nМаксимальная длинна: {}\n для продолжения спросте контекст командой /dropcontext, используйте другую модель  или преобретите премиум /premium".format(tokenSizeNow, maxToken)
    #     bot.reply_to(message, text, reply_markup=markup)
    #     return ""


    try:
        content = _gpt.gpt_post_view(json, model, 1300 )

        bot.delete_message(send_mess.chat.id, send_mess.message_id)

        if content.get_code() == 200:
            _db.add_context(message.from_user.id, message.chat.id, "user",          message.message_id,     text_to_photo,  False)
            _db.add_context(message.from_user.id, message.chat.id, "user",          message.message_id,     base64_image,   True)
            _db.add_context(message.from_user.id, message.chat.id, "assistant",     message.message_id,     content.get_result(),        False)


        bot.reply_to(message, "{}".format(content.get_result()) )

    except OpenAIError as err: 
        t_mes = locale.find_translation(user.get_language(), 'TR_ERROR_OPENAI')
        bot.reply_to(message, t_mes.format(err))
        _logger.add_critical("OpenAI: {}".format(err))

    

def user_verification(message):
    user = User()

    if _db.find_user(message.from_user.id) == False:
        #_db.create_user(message.from_user.id, message.chat.username, 1, user.get_wait_action(), message.chat.type, user.get_companyAi(), user.get_model(), user.get_speaker(), message.from_user.language_code, user.get_model_recognizes_photo(), user.get_model_generate_pthoto(), user.get_text_to_audio(), user.get_audio_to_text())
        _db.add_user(message.from_user.id, message.chat.username, message.chat.type, message.from_user.language_code )
        _logger.add_info('создан новый пользователь {}'.format(message.chat.username))
    else:
        _db.add_users_in_groups(message.from_user.id, message.chat.id)
    
    user = _db.get_user_def(message.from_user.id)

    if user.get_status() == 0: 
        return None

    return user

def user_verification_custom(userId, chatId, chat_username, chatType, lang_code):
    user = User()
    if _db.find_user(userId) == False:
        # _db.create_user(userId, chat_username, False, 1, chatType, user.get_companyAi(), user.get_model(), user.get_speaker(), user.get_contextSize(), lang_code)
        _db.add_user(userId, chat_username, chatType, lang_code )
        _logger.add_info('создан новый пользователь {}'.format(chat_username))
    else:
        _db.add_users_in_groups(userId, chatId)
    
    user = _db.get_user_def(userId)

    if user.get_status() == 0: # TODO: добавить проверку аккаунта на блокировку 
        return None

    return user

def user_verification_easy(userId):
    user = User()
    if _db.find_user(userId) == False:
        return None
    else:
        user = _db.get_user_def(userId)
        return user



def post_gpt(chatId, user:User, text, model) -> Control.context_model.AnswerAssistent :
    mes = Control.context_model.Context_model()
    mes.set_data(user.get_userId(), chatId,"user", chatId,text,False )

    dict = _db.get_context(user.get_userId(), chatId)
    # dict = Control.context_model.rm_photos_in_dict(dict)
    dict.append(mes)
    json = Control.context_model.convert(user.get_companyAi(), dict)

    # content = NULL
    tokenSizeNow = 0

    if str(user.get_companyAi()).upper() == str("OpenAi").upper():
        tokenSizeNow = _gpt.num_tokens_from_messages(json, model)
    elif str(user.get_companyAi()).upper() == str("Yandex").upper():
        tokenSizeNow = _yag.count_tokens(json, model)
    elif str(user.get_companyAi()).upper() == str("Sber").upper():
        tokenSizeNow = _sber.count_tokens(json, model)
    elif str(user.get_companyAi()).upper() == str("Meta").upper():
        tokenSizeNow = _metaG.count_tokens(json, model)
    

    maxToken = _assistent_api.getToken(model)

    if tokenSizeNow > maxToken:
        markup = types.InlineKeyboardMarkup()
        markup.add( types.InlineKeyboardButton(locale.find_translation(user.get_language(), 'TR_REPEAT_REQUEST'), callback_data='errorPost') )
        # text = "Извините, но ваш запрос привышает максималтную длинну контекста.\nВаш запрос: {}\nМаксимальная длинна: {}\n для продолжения спросте контекст командой /dropcontext, используйте другую модель или преобретите премиум /premium".format(tokenSizeNow, maxToken)
        bot.reply_to(chatId, locale.find_translation(user.get_language(), 'TR_HAVE_NOT_TOKENS'), reply_markup=markup)
        return ""

    try:
        if str(user.get_companyAi()).upper() == str("OpenAi").upper():
            content = _gpt.post_gpt(json, model)
        elif str(user.get_companyAi()).upper() == str("Yandex").upper():
            _yag.set_token( _speak.get_IAM() )
            content = _yag.post_gpt(json, model)
        elif str(user.get_companyAi()).upper() == str("Sber").upper():
            content = _sber.post_gpt(json, model)
        elif str(user.get_companyAi()).upper() == str("Meta").upper():
            content = _metaG.post_gpt(json, model)


        if content.get_code() == 200:
            _db.add_context(user.get_userId(), chatId, "user",          chatId, text,       False)
            _db.add_context(user.get_userId(), chatId, "assistant",     chatId, content.get_result(),    False)
    
    except OpenAIError as err: 
        t_mes = locale.find_translation(user.get_language(), 'TR_ERROR_OPENAI')
        markup = types.InlineKeyboardMarkup()
        markup.add( types.InlineKeyboardButton(locale.find_translation(user.get_language(), 'TR_REPEAT_REQUEST'), callback_data='errorPost ') )
        # bot.send_message(message.chat.id, content, reply_markup=markup)
        bot.reply_to(chatId, t_mes.format(err),reply_markup=markup)
        _logger.add_critical("OpenAI: {}".format(err))

    return content


def send_text(chat_id, text, reply_markup=None):
    max_message_length = 4096
    while len(text) > 0:
        if len(text) <= max_message_length:
            bot.send_message(chat_id, text, reply_markup=reply_markup)
            break
        
        breakpoint = text[:max_message_length].rfind(' ')       # Ищем последний пробел или перенос строки в пределах допустимой длины
        if breakpoint == -1:
            breakpoint = text[:max_message_length].rfind('\n')

        if breakpoint == -1:                                    # В пределах max_message_length нет пробелов
            message_chunk = text[:max_message_length]
            text = text[max_message_length:]
        else:                                                   # Разделяем по найденному пробелу/переносу строки
            message_chunk = text[:breakpoint]
            text = text[breakpoint:].lstrip()

        bot.send_message(chat_id, message_chunk, reply_markup=reply_markup)



# def __del__():
#     print(1)
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  

def on_post_media(sender, userId, mediaList):
    message = ''
    chatId = ''
    titleMessId = []
    for media in mediaList:
        if chatId == '':
            chatId = media._chatId
        
        if media._type == "document":
            message += _converterFile.convert_files_to_text('files/{}'.format(media._fileWay), media._fileName)
            os.remove('files/{}'.format(media._fileWay))
        if media._type == "message":
            message = media._mediaData + '\n' + message
        if media._type == "titleId":
            titleMessId.append( media._titleId)
        
    if chatId == '':
        chatId = userId
    
    # print( "\n\n" + message)

    user = user_verification_easy(userId)
    content = post_gpt(chatId, user, message, user.get_model())
    MAX_CHAR = _db.get_count_char_for_gen_audio()

    if len(titleMessId) != 0:
        for medId in titleMessId:
            bot.delete_message(chatId, medId)

    if not content.get_result():
        t_mes = locale.find_translation(user.get_language(), 'TR_ERROR_GET_RESULT')
        bot.send_message(chatId, t_mes)
        # _logger.add_critical("Ошибка получения результата в handle_user_message: пустой content")

    if len(content.get_result()) <= MAX_CHAR:
        markup = types.InlineKeyboardMarkup()
        markup.add( types.InlineKeyboardButton(locale.find_translation(user.get_language(), 'TR_VOCALIZE'), callback_data='sintez') )

        send_text(chatId, content.get_result(), reply_markup=markup)
    else:    
        send_text(chatId, content.get_result())







try:
    post_signal.connect(on_post_media, sender='MediaWorker')
    bot.infinity_polling()
    # bot.polling()
except requests.exceptions.ConnectionError as e:
    print("{} Ошибка подключения:".format(_speak.get_time_string()), e)
    _logger.add_error('нет соединения с сервером telegram bot: {}'.format(e))


