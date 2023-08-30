import telebot
import openai
import json 
from configure import Settings
from database import DB


_setting = Settings()
_db = DB()

bot = telebot.TeleBot(_setting.get_tgToken())
openai.api_key = _setting.get_cGptToken()



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
    bot.send_message(message.chat.id, content)

    # decoded_s = content.encode().decode('unicode-escape')
    # bot.send_message(message.chat.id, decoded_s)

    
        

bot.infinity_polling()