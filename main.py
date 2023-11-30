import requests
import telebot
import speech
import base64
import sys
import os

from logger         import LoggerSingleton
from openai.error   import OpenAIError
from configure      import Settings
from databaseapi    import dbApi
from telebot        import types
from translator     import Locale
from user           import User
from gpt_api        import chatgpt


language = 'ru_RU' 
MAX_CHAR = 500

_setting = Settings()
sys.stdout.reconfigure(encoding='utf-8')
_logger = LoggerSingleton.new_instance('log_gpt.log')
locale = Locale('locale/LC_MESSAGES/')

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

_speak = speech.speaker(TOKEN_FOLDER_ID)
if _speak.get_IAM == '':
    print ('no yandex iam token!')
    _logger.add_critical('no yandex iam token!')
    sys.exit()


_speak.start_key_generation()



try:
    bot = telebot.TeleBot( TOKEN_TG )
except requests.exceptions.ConnectionError as e:
    print("{} Ошибка подключения:".format(_speak.get_time_string()), e)
    _logger.add_error('нет соединения с сервером telegram bot: {}'.format(e))

# openai.api_key = TOKEN_GPT
_gpt = chatgpt(TOKEN_GPT, TOKEN_FOLDER_ID)


@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
    user_verification(message)
    username = str(message.chat.username)
    _db.delete_user_context(message.from_user.id, message.chat.id)
    t_mes = locale.find_translation(language, 'TR_START_MESSAGE')
    bot.reply_to(message, t_mes.format(username) )
    # TODO: добавить подробное описание того, что бот умеет 
    

@bot.message_handler(commands=['dropcontext'])
def drop_context(message):
    user_verification(message)
    _db.delete_user_context(message.from_user.id, message.chat.id)
    t_mes = locale.find_translation(language, 'TR_CLEAR_CONTEXT')
    bot.send_message(message.chat.id, t_mes )


@bot.message_handler(commands=['lastlog'])
def drop_context(message):
    user_verification(message)
    if _db.isAdmin(message.from_user.id, message.chat.username) == False:
        return
    
    words = message.text.split()

    if len(words) == 2:
        second_word = words[1]
        if second_word.isdigit():
            text = _logger.read_file_from_end(int(second_word))
            t_mes = locale.find_translation(language, 'TR_GET_LOG')
            bot.send_message(message.chat.id, t_mes.format(second_word, text))

    elif len(words) == 3:
        second_word = words[1]
        type_log = words[2]

        if second_word.isdigit():
            text = _logger.read_file_from_end(int(second_word), type_log)
            t_mes = locale.find_translation(language, 'TR_GET_LOG_POST')
            bot.send_message(message.chat.id, t_mes.format(second_word, type_log, text))
    else:
        t_mes = locale.find_translation(language, 'TR_ERROR_SINTAX')
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

    text = "Коротко о софте:\nОтветы генерируются при помощи ChatGPT. По умолчанию используется модель gpt-3.5-turbo.\nРаспознавание и генерация голосовых сообщений осуществляется при помощи Yandex SpeechKit v1 (позже перейдем на v3).\n\nКоманды:\n/dropcontext - удаляет весь контекст переписки."

    if _db.isAdmin(message.from_user.id, message.chat.username) == True:
        text_admin = "\n\nДоступно только для админа! будь аккуратнее с командами\n/notify_all <текст> - Эта команда отправит во все чаты твой текст, прошу, будь аккуратнее\nТут будут еще команды ..."
        text += text_admin

    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['assistantmode'])
def help(message):
    user_verification(message)

    ##################################################################################
    # TODO
    ##########################################


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    user_verification(message)

    t_mes = locale.find_translation(language, 'TR_WAIT_POST')
    send_mess = bot.send_message(message.chat.id, t_mes)
    
    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = bot.download_file(file_path)

    filename = 'voice_{}_{}.ogg'.format(message.from_user.id, _speak.get_time_string())
    with open('./voice/' + filename, 'wb') as f:
        f.write(downloaded_file)

    text = _speak.voice_text_v1(downloaded_file, message.from_user.id)
    # text = _speak.voice_text_v3(downloaded_file, message.from_user.id)

    bot.delete_message(send_mess.chat.id, send_mess.message_id)

    if text != '':
        content = post_gpt(message, text)

        if not content:
            t_mes = locale.find_translation(language, 'TR_ERROR_GET_RESULT')
            bot.send_message(message.chat.id, t_mes)
        _logger.add_critical("Ошибка получения результата в handle_user_message: пустой content. Сообщение для {}".format(message.chat.username))

        if len(content) <= MAX_CHAR:
            markup = types.InlineKeyboardMarkup()
            markup.add( types.InlineKeyboardButton('Озвучить', callback_data='sintez') )
            bot.send_message(message.chat.id, content, reply_markup=markup)
        else:    
            bot.send_message(message.chat.id, content)
    else:
        t_mes = locale.find_translation(language, 'TR_ERROR_DECODE_VOICE')
        bot.send_message(message.chat.id, t_mes)
    
    # TODO: добавить возможность записи длинных голосовых сообщений(v3)


@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    user_verification(message)

    t_mes = locale.find_translation(language, 'TR_WAIT_POST')
    send_mess = bot.send_message(message.chat.id, t_mes)

    content = post_gpt(message, message.text)

    bot.delete_message(send_mess.chat.id, send_mess.message_id)

    if not content:
        t_mes = locale.find_translation(language, 'TR_ERROR_GET_RESULT')
        bot.send_message(message.chat.id, t_mes)
        _logger.add_critical("Ошибка получения результата в handle_user_message: пустой content")

    if len(content) <= MAX_CHAR:
        markup = types.InlineKeyboardMarkup()
        markup.add( types.InlineKeyboardButton('Озвучить', callback_data='sintez') )
        bot.send_message(message.chat.id, content, reply_markup=markup)
    else:    
        bot.send_message(message.chat.id, content)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data == 'sintez':
        text = call.message.text

        t_mes = locale.find_translation(language, 'TR_START_DECODE_VOICE')
        bot.answer_callback_query(call.id, text = t_mes)

        # file = _speak.voice_synthesis_v1(text, call.message.chat.id)
        file = _speak.voice_synthesis_v3(text, call.message.chat.id)
        
        with open(file, "rb") as audio:
            bot.send_audio(call.message.chat.id, audio)

        os.remove(file)

        # Удаление кнопки
        # bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

    elif call.data == 'errorPost':
        text = call.message.text
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        post_gpt(call, text)
        
    else:
        t_mes = locale.find_translation(language, 'TR_ERROR')
        bot.answer_callback_query(call.id, text = t_mes)
    



@bot.message_handler(content_types=['photo'])
def handle_message(message):
    user = user_verification(message)

    t_mes = locale.find_translation(language, 'TR_WAIT_POST')
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
    

    mes_json = {"role": "user","content": [
            {"type": "text", "text": "{}".format(text_to_photo)},
            {"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},},
            ],}

    dict = _db.get_context(message.from_user.id, message.chat.id)
    dict.append( mes_json )
    
    content = ""


    try:
        content = _gpt.gpt_post_view(dict, 1300 )

        bot.delete_message(send_mess.chat.id, send_mess.message_id)
        _db.add_context(message.from_user.id, message.chat.id, "user",          message.message_id,     text_to_photo,  False)
        # _db.add_context(message.from_user.id, message.chat.id, "user",          message.message_id,     base64_image,   True)
        _db.add_context(message.from_user.id, message.chat.id, "assistant",     message.message_id,     content,        False)


        bot.reply_to(message, "{}".format(content) )

    except OpenAIError as err: 
        t_mes = locale.find_translation(language, 'TR_ERROR_OPENAI')
        bot.reply_to(message, t_mes.format(err))
        _logger.add_critical("OpenAI: {}".format(err))

    

def user_verification(message):
    user = User()

    if _db.find_user(message.from_user.id) == False:
        _db.create_user(message.from_user.id, message.chat.username, False, 1, message.chat.type, user.get_companyAi(), user.get_model(), user.get_speaker(), user.get_contextSize(), message.from_user.language_code)
        _logger.add_info('создан новый пользователь {}'.format(message.chat.username))
    else:
        _db.add_users_in_groups(message.from_user.id, message.chat.id)
        # user.

    
    # TODO: добавить проверку аккаунта на блокировку 

    return user


def post_gpt(message, text):

    mes_json = {"role": "user", "content": str(text)}

    dict = _db.get_context(message.from_user.id, message.chat.id)
    dict.append( mes_json )
    content = ""

    try:
        # content = _gpt.post_gpt(dict, "gpt-4-1106-preview")
        content = _gpt.post_gpt(dict, "gpt-3.5-turbo")

        _db.add_context(message.from_user.id, message.chat.id, "user",          message.message_id, text,       False)
        _db.add_context(message.from_user.id, message.chat.id, "assistant",     message.message_id, content,    False)
    
    except OpenAIError as err: 
        t_mes = locale.find_translation(language, 'TR_ERROR_OPENAI')
        markup = types.InlineKeyboardMarkup()
        markup.add( types.InlineKeyboardButton('Повторить запрос', callback_data='errorPost') )
        # bot.send_message(message.chat.id, content, reply_markup=markup)
        bot.reply_to(message, t_mes.format(err),reply_markup=markup)
        _logger.add_critical("OpenAI: {}".format(err))

    return content


# def __del__():
#     print(1)
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


try:
    bot.infinity_polling()
    # bot.polling()
except requests.exceptions.ConnectionError as e:
    print("{} Ошибка подключения:".format(_speak.get_time_string()), e)
    _logger.add_error('нет соединения с сервером telegram bot: {}'.format(e))

