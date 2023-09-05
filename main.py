import telebot
import openai
import json 
import sys
from configure import Settings
from database import DB
from telebot import types


_setting = Settings()
_db = DB()


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
    username = str(message.chat.username)
    bot.reply_to(message, "Привет " + username +" ! я готов к работе, просто напиши сообщение\nP.S. я пока не помню контекст переписки, но скоро я вырасту и буду способнее")
    

# @bot.message_handler(commands=['help'])
# def info_o_users(message):
#     username = str(message.chat.username)
#     accaunts = users.showAll()
#     logger.logger_add_info('Пользователь ' + username + ' запросил данные ./user.txt')
#     bot.send_message(message.chat.id, accaunts)


@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    # audio = message.audio
    # file_id = audio.file_id
    # duration = audio.duration
    bot.send_message(message.chat.id, 'Появиться скоро!')



@bot.message_handler(func=lambda message: True)
def echo_all(message):

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # model = "text-davinci-002"
        # model = "text-babbage-001"
        messages=[
            {"role": "user", "content": message.text}
        ])

    answer = str( completion.choices[0].message )
    data = json.loads(answer)
    content = data['content']

    if len(content) <= 500:
        markup = types.InlineKeyboardMarkup()
        markup.add( types.InlineKeyboardButton('Озвучить', callback_data='sintez') )
        bot.send_message(message.chat.id, content, reply_markup=markup)
    else:    
        bot.send_message(message.chat.id, content)

    # decoded_s = content.encode().decode('unicode-escape')
    # bot.send_message(message.chat.id, decoded_s)


@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    button_text = call.data
    bot.send_message(chat_id=call.message.chat.id, text="Пока не доступно!")

bot.infinity_polling()
# bot.polling()