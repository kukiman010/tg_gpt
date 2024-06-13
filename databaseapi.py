from database import Database
from data_models import assistent_model
from data_models import languages_model
from Control.user import User
from typing import List

import Control.context_model

class dbApi:
    def __init__(self, dbname, user, password, host, port):
        self.db = Database(dbname,user, password, host, port)
        self.db.connect()


#   USER
    def find_user(self, userId):
        query = "SELECT * FROM users WHERE user_id='{}';".format(userId)
        self.db.execute_query(query)
        data = self.db.fetch_all()
        self.db.commit()
        # print(data)

        if len(data) == 1:
            if data[0][0] == userId:
                return True

        return False    
    

    def create_user(self, user_id, username, status_user, wait_action, type, company_ai, model, speaker_name, language_code, model_recognizes_photo, model_generate_pthoto, text_to_audio, audio_to_text):
        query = """
        INSERT INTO users (
            user_id, login, status_user, wait_action, type, company_ai, model, speaker_name, language_code,
            model_rec_photo, model_gen_pthoto, text_to_audio, audio_to_text,
            last_login, registration_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW());
        """
        values = (user_id, username, status_user, wait_action, type, company_ai, model, speaker_name, language_code, model_recognizes_photo, model_generate_pthoto, text_to_audio, audio_to_text)
        self.db.execute_query(query, values)
        self.db.commit()

    def update_user_assistent(self, userId, company, model): 
        query = "UPDATE users SET company_ai='{}',model='{}' WHERE user_id={};".format(company,model,userId)
        self.db.execute_query(query)
        self.db.commit()

    def get_user_def(self, userId):
        query = "select * from users WHERE user_id={};".format(userId)
        self.db.execute_query(query)
        data = self.db.fetch_all()
        self.db.commit()

        for i in data:
            user = User()
#   0      1       2        3        4         5           6          7                  8                        9                10             11           12          13  
# 
# 0         1      2        5        6         7           8         3                  9                        10                11             12           13          14                  
#userId, login, status, companyAi, model, speakerName, language, wait_action, model_recognizes_photo, model_generate_pthoto, text_to_audio, audio_to_text, last_login, reg_date
            # user.set_base_info(i[0],i[1],i[2],i[3],i[5],i[6],i[7],i[8],i[9],i[10],i[11],i[12],i[13],i[14])
            user.set_base_info(i[0],i[1],i[2],i[5],i[6],i[7],i[8],i[3],i[9],i[10],i[11],i[12],i[13],i[14])
            return user
        
    def update_user_lang_code(self, userId, code): 
        query = "UPDATE users SET language_code='{}' WHERE user_id={};".format(code,userId)
        self.db.execute_query(query)
        self.db.commit()
        




    def add_context(self, userId, chatId, role, messageId, message, isPhoto):
        query = "INSERT INTO context VALUES (%s,%s,%s,%s,%s,%s);"
        self.db.custom_execute_query(query, (userId, chatId, role, messageId, str(message), isPhoto) )
        self.db.commit()

    def get_context(self, userId, chatId) -> List[Control.context_model.Context_model]:
        query = "SELECT * FROM context WHERE user_id='{}' AND chat_id='{}';".format(userId, chatId)
        self.db.execute_query(query)
        data = self.db.fetch_all()
        self.db.commit()
        result = []

        for i in data:
            context = Control.context_model.Context_model()
            context.set_data(i[0],i[1],i[2],i[3],i[4],i[5])
            if  i[4] != "":
                result.append( context )
        return result
    
    def delete_user_context(self, userId, chatId):
        query = "DELETE FROM context WHERE user_id='{}' AND chat_id='{}';".format(userId, chatId)
        self.db.execute_query(query)
        self.db.commit()
    
    def add_users_in_groups(self, userId, chatId):
        query = "SELECT add_chats_id("+str(userId)+", '{"+str(chatId) +"}');"
        self.db.execute_query(query)
        self.db.commit()

    def get_all_chat(self, userId):
        query = "SELECT * FROM get_chats_id({});".format(userId)
        self.db.execute_query(query)
        data = self.db.fetch_all()
        self.db.commit()
        return data
    
    def isAdmin(self, userId, username):
        query = "SELECT * FROM admins WHERE user_id={};".format(userId)
        self.db.execute_query(query)
        data = self.db.fetch_all()
        self.db.commit()
        if len(data) == 1:
            if data[0][0] == userId and data[0][1] == username and data[0][2] != 0:
                return True
        return False
    
    def get_assistant_ai(self):
        query = "select * from assistant_ai;"
        self.db.execute_query(query)
        data = self.db.fetch_all()
        self.db.commit()
        array = []

        for i in data:
            am = assistent_model()
            am.set_model(i[0],i[1],i[2],i[3],i[4],i[5],i[6])
            array.append( am )
        return array
        

    def get_languages(self):
        query = "select * from languages;"
        self.db.execute_query(query)
        data = self.db.fetch_all()
        self.db.commit()
        array = []

        for i in data:
            lm = languages_model()
            lm.set_model(i[0],i[1],i[2])
            array.append( lm )
        return array
    


    # def get_user(self)

    # def (self):
    #     print('')

    def __del__(self):
        self.db.close()
#     print(1)


# dbApi