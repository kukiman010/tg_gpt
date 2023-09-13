import requests
import telebot
import openai
import sched
import time
import json 
import sys

from configure import Settings
from telebot import types
from databaseapi import dbApi
from openai.error import OpenAIError


language = 'ru_RU' 
_setting = Settings()
scheduler = sched.scheduler(time.monotonic, time.sleep)

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
TOKEN_IAM = _setting.get_yandex_iam()


if TOKEN_TG == '':
    print ('no tg token!')
    sys.exit()

if TOKEN_GPT == '':
    print ('no gpts token!')
    sys.exit()

if TOKEN_FOLDER_ID == '':
    print ('no yandex folder id!')
    sys.exit()

if TOKEN_IAM == '':
    print ('no yandex iam token!')
    sys.exit()


try:
    bot = telebot.TeleBot( TOKEN_TG )
except requests.exceptions.ConnectionError as e:
    current_time = time.time()
    time_struct = time.localtime(current_time)
    formatted_datetime = time.strftime("%Y.%m.%d_%H.%M.%S", time_struct)
    print("{} Ошибка подключения:".format(formatted_datetime), e)

openai.api_key = TOKEN_GPT



@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
    user_verification(message)
    username = str(message.chat.username)
    _db.delete_user_context(message.from_user.id, message.chat.id)
    bot.reply_to(message, "Привет " + username +" ! я готов к работе, просто напиши сообщение")
    

@bot.message_handler(commands=['dropcontext'])
def drop_context(message):
    user_verification(message)
    _db.delete_user_context(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, "Контекст очищен")


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

    current_time = time.time()
    time_struct = time.localtime(current_time)
    formatted_datetime = time.strftime("%Y%m%d_%H%M%S", time_struct)

    filename = 'voice_{}_{}.ogg'.format(message.from_user.id, formatted_datetime)
    with open('./voice/' + filename, 'wb') as f:
        f.write(downloaded_file)


    url = f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?folderId={TOKEN_FOLDER_ID}&lang=auto"
    headers = {"Authorization": f"Bearer {TOKEN_IAM}"}
    binary_data = open('./voice/' + filename, "rb").read()

    response = requests.post(url, headers=headers, data=binary_data)
    
    if response.status_code == 200:
        response_data = response.json()
        answer = str( response_data['result'] )

        if answer == False:
            bot.edit_message_text("Извините, но произошла ошибка", send_mess.chat.id, send_mess.message_id)
            return

        content = post_gpt(message, answer)

        if len(content) <= 500:
            markup = types.InlineKeyboardMarkup()
            markup.add( types.InlineKeyboardButton('Озвучить', callback_data='sintez') )
            bot.edit_message_text(content, send_mess.chat.id, send_mess.message_id, reply_markup=markup)
        else:    
            bot.edit_message_text(content, send_mess.chat.id, send_mess.message_id)
    else:
        bot.edit_message_text("Извините, но произошла ошибка", send_mess.chat.id, send_mess.message_id)

    # TODO: добавить возможность записи длинных сообщений


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
def handle_button_click(call):
    button_text = call.data
    bot.send_message(chat_id=call.message.chat.id, text="Пока не доступно!")



def user_verification(message):
    if _db.find_user(message.from_user.id) == False:
        _db.create_user(message.from_user.id, message.chat.username, 1, message.chat.type)

    _db.add_users_in_groups(message.from_user.id, message.chat.id)


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


    return content
    



# def __del__():
#     print(1)


try:
    bot.infinity_polling()
    # bot.polling()
except requests.exceptions.ConnectionError as e:
    current_time = time.time()
    time_struct = time.localtime(current_time)
    formatted_datetime = time.strftime("%Y.%m.%d_%H.%M.%S", time_struct)
    print("{} Ошибка подключения:".format(formatted_datetime), e)




def hourly_task():
    current_time = time.time()
    time_struct = time.localtime(current_time)
    formatted_datetime = time.strftime("%Y.%m.%d_%H.%M.%S", time_struct)
    print("Сработал планировщик задач для get_yandex_iam. дата: {}".format(formatted_datetime))

    TOKEN_IAM = _setting.get_yandex_iam()
    scheduler.enter(3600, 1, hourly_task)

scheduler.enter(3600, 1, hourly_task)
scheduler.run()


# scheduler = sched.scheduler(time.time, time.sleep)
# scheduler.enter(0, 1, hourly_task, ())
# while True:
#     scheduler.run()
#     time.sleep(3600) 