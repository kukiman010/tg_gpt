import telebot
import openai
import json 
import sys
# import os
# import uuid
import time
from configure import Settings
# from database import DB
from telebot import types
# import speech_recognition as sr
from databaseapi import dbApi
from openai.error import OpenAIError



language='ru_RU' 
_setting = Settings()
# r = sr.Recognizer() 
_db = dbApi(
    dbname =    _setting.get_db_dbname(),
    user =      _setting.get_db_user(),
    password =  _setting.get_db_pass(),
    host =      _setting.get_db_host(),
    port =      _setting.get_db_port()
)



TOKEN_TG = _setting.get_tgToken()
TOKEN_GPT = _setting.get_cGptToken()

if TOKEN_TG == '':
    print ('no tg token')
    sys.exit()

if TOKEN_GPT == '':
    print ('no gpts token')
    sys.exit()

bot = telebot.TeleBot( TOKEN_TG )
openai.api_key =       TOKEN_GPT



@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
    user_verification(message)
    username = str(message.chat.username)
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


# @bot.message_handler(commands=['help'])
# def info_o_users(message):
#     username = str(message.chat.username)
#     accaunts = users.showAll()
#     logger.logger_add_info('Пользователь ' + username + ' запросил данные ./user.txt')
#     bot.send_message(message.chat.id, accaunts)




# def recognise(filename):
#     with sr.AudioFile(filename) as source:
#         audio_text = r.listen(source)
#         try:
#             text = r.recognize_google(audio_text,language=language)
#             print('Converting audio transcripts into text ...')
#             print(text)
#             return text
#         except:
#             print('Sorry.. run again...')
#             return "Sorry.. run again..."


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    user_verification(message)
    bot.send_message(message.chat.id, "Распознование voice еще в разработке")
    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path
    downloaded_file = bot.download_file(file_path)

    # Сохранение голосового сообщения в файле

    current_time = time.time()
    time_struct = time.localtime(current_time)
    formatted_datetime = time.strftime("%Y%m%d_%H%M%S", time_struct)

    filename = 'voice_{}_{}.ogg'.format(message.from_user.id, formatted_datetime)
    with open('./voice/' + filename, 'wb') as f:
        f.write(downloaded_file)


#     filename = str(uuid.uuid4())
#     # filename = str('voice_{message.from_user.id}_ {time.time()}')
#     file_name_full="./voice/"+filename+".ogg"
#     file_name_full_converted="./ready/"+filename+".wav"
#     file_info = bot.get_file(message.voice.file_id)
#     downloaded_file = bot.download_file(file_info.file_path)
#     with open(file_name_full, 'wb') as new_file:
#         new_file.write(downloaded_file)
#     os.system("ffmpeg -i "+file_name_full+"  "+file_name_full_converted)
#     try:
#         text=recognise(file_name_full_converted)
#     except (Exception) as error:
#         print('Error while connecting to the database:', error)
#     bot.reply_to(message, text)
#     os.remove(file_name_full)
#     os.remove(file_name_full_converted)


@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    user_verification(message)

    send_mess = bot.send_message(message.chat.id, "Пожалуйста, подождите, запрос обрабатывается...")

    dict = _db.get_context(message.from_user.id, message.chat.id)
    dict.append( {"role": "user", "content": message.text})

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=dict
            )
    except OpenAIError as err:
        bot.reply_to(message, "Извините, ошибка OpenAI: {}".format(err))


    answer = str( completion.choices[0].message )
    data = json.loads(answer)
    content = data['content']

    # content = message.text

    _db.add_context(message.from_user.id, message.chat.id, "user",  message.message_id, message.text)
    _db.add_context(message.from_user.id, message.chat.id, "assistant",  message.message_id, content)

    bot.delete_message(message.chat.id, send_mess.message_id)

    if len(content) <= 500:
        markup = types.InlineKeyboardMarkup()
        markup.add( types.InlineKeyboardButton('Озвучить', callback_data='sintez') )
        bot.send_message(message.chat.id, content, reply_markup=markup)
    else:    
        bot.send_message(message.chat.id, content)



@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    button_text = call.data
    bot.send_message(chat_id=call.message.chat.id, text="Пока не доступно!")



def user_verification(message):
    if _db.find_user(message.from_user.id) == False:
        _db.create_user(message.from_user.id, message.chat.username, 1, message.chat.type)

    _db.add_users_in_groups(message.from_user.id, message.chat.id)
        



# def __del__():
#     print(1)

bot.infinity_polling()
# bot.polling()