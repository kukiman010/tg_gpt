import requests
import telebot
import openai
import speech
import json 
import sys
import os

from logger         import LoggerSingleton
from openai.error   import OpenAIError
from configure      import Settings
from databaseapi    import dbApi
from telebot        import types


language = 'ru_RU' 
_setting = Settings()
sys.stdout.reconfigure(encoding='utf-8')
_logger = LoggerSingleton('log_gpt.log')


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


# _speak.start_key_generation()



try:
    bot = telebot.TeleBot( TOKEN_TG )
except requests.exceptions.ConnectionError as e:
    print("{} Ошибка подключения:".format(_speak.get_time_string()), e)
    _logger.add_error('нет соединения с сервером telegram bot: {}'.format(e))

openai.api_key = TOKEN_GPT



@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
    user_verification(message)
    username = str(message.chat.username)
    _db.delete_user_context(message.from_user.id, message.chat.id)
    bot.reply_to(message, "Привет " + username +" ! я готов к работе, просто напиши сообщение")
    # TODO: добавить подробное описание того, что бот умеет 
    

@bot.message_handler(commands=['dropcontext'])
def drop_context(message):
    user_verification(message)
    _db.delete_user_context(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, "Контекст очищен")


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
            bot.send_message(message.chat.id, "Ваши последние {} лог(ов)\n\n{}".format(second_word, text))

    elif len(words) == 3:
        second_word = words[1]
        type_log = words[2]

        if second_word.isdigit():
            text = _logger.read_file_from_end(int(second_word), type_log)
            bot.send_message(message.chat.id, "Ваши последние {} лог(ов) по запроссу {}\n\n{}".format(second_word, type_log, text))
    else:
        bot.send_message(message.chat.id, "Не верный синтаксис\n подробнее в /help")


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


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    user_verification(message)

    send_mess = bot.send_message(message.chat.id, "Пожалуйста, подождите, запрос обрабатывается...")
    
    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = bot.download_file(file_path)

    filename = 'voice_{}_{}.ogg'.format(message.from_user.id, _speak.get_time_string)
    with open('./voice/' + filename, 'wb') as f:
        f.write(downloaded_file)

    text = _speak.gen_voice_v1(downloaded_file, message.from_user.id)

    if text != '':
        content = post_gpt(message, text)

        if len(content) <= 500:
            markup = types.InlineKeyboardMarkup()
            markup.add( types.InlineKeyboardButton('Озвучить', callback_data='sintez') )
            bot.edit_message_text(content, send_mess.chat.id, send_mess.message_id, reply_markup=markup)
        else:    
            bot.edit_message_text(content, send_mess.chat.id, send_mess.message_id)
    else:
        bot.edit_message_text("Извините, но произошла ошибка", send_mess.chat.id, send_mess.message_id)
    
    # TODO: добавить возможность записи длинных голосовых сообщений(v3)


@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    user_verification(message)

    send_mess = bot.send_message(message.chat.id, "Пожалуйста, подождите, запрос обрабатывается...")

    content = post_gpt(message, message.text)

    if len(content) <= 500:
        markup = types.InlineKeyboardMarkup()
        markup.add( types.InlineKeyboardButton('Озвучить', callback_data='sintez') )
        bot.edit_message_text(content, send_mess.chat.id, send_mess.message_id, reply_markup=markup)
    else:    
        bot.edit_message_text(content, send_mess.chat.id, send_mess.message_id)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data == 'sintez':
        text = call.message.text

        bot.answer_callback_query(call.id, text='Обработка начилась!')

        # file = _speak.voice_synthesis_v1(text, call.message.chat.id)
        file = _speak.voice_synthesis_v3(text, call.message.chat.id)
        
        with open(file, "rb") as audio:
            bot.send_audio(call.message.chat.id, audio)

        os.remove(file)
    else:
        bot.answer_callback_query(call.id, text='Ошибка!')
    


def user_verification(message):
    if _db.find_user(message.from_user.id) == False:
        _db.create_user(message.from_user.id, message.chat.username, 1, message.chat.type)
        _logger.add_error('создан новый пользователь {}'.format(message.chat.username))

    _db.add_users_in_groups(message.from_user.id, message.chat.id)
    # TODO: добавить проверку аккаунта на блокировку 


def post_gpt(message, text):
    dict = _db.get_context(message.from_user.id, message.chat.id)
    dict.append( {"role": "user", "content": str(text)})
    content = ""

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=dict
            )
        answer = str( completion.choices[0].message )
        data = json.loads(answer)
        content = data['content']
        # content = text

        _db.add_context(message.from_user.id, message.chat.id, "user",  message.message_id, text)
        _db.add_context(message.from_user.id, message.chat.id, "assistant",  message.message_id, content)
    
    except OpenAIError as err: 
        bot.reply_to(message, "Извините, ошибка OpenAI: {}".format(err))
        _logger.add_critical("OpenAI: {}".format(err))

    return content


# def __del__():
#     print(1)


try:
    bot.infinity_polling()
    # bot.polling()
except requests.exceptions.ConnectionError as e:
    print("{} Ошибка подключения:".format(_speak.get_time_string()), e)
    _logger.add_error('нет соединения с сервером telegram bot: {}'.format(e))

