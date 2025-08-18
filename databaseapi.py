from database import Database
from data_models import assistent_model
from data_models import languages_model
from data_models import payments_model
from data_models import tariffs_model
from Control.user import User
from typing import List
from Control.subscription_data import SubscriptionData

import Control.context_model

class dbApi:
    def __init__(self, dbname, user, password, host, port):
        self.db = Database(dbname,user, password, host, port)

    def find_user(self, userId:int):
        query = "SELECT user_find({});".format(userId)
        data = self.db.execute_query(query)
        return bool(data and data[0][0])

    def add_user(self, user_id, username, type, language_code):
        query = 'SELECT add_user(%s, %s, %s, %s);'
        values = (user_id, username, type, language_code)
        self.db.execute_query(query, values)

    def update_user_assistent(self, userId, company, model): 
        query = "UPDATE users SET company_ai=%s, model=%s WHERE user_id=%s;"
        values = (company, model, userId)
        self.db.execute_query(query, values)
        
    def get_user_def(self, user_id):
        query = "SELECT * FROM get_user_and_prompts({});".format(user_id)
        data = self.db.execute_query(query)

        if not data:
            return None
        
        columns = [
            'user_id', 'login', 'status_user', 'wait_action', 'type', 'company_ai', 
            'model', 'language_code', 'model_rec_photo', 'model_gen_photo', 
            'text_to_audio', 'audio_to_text', 'speaker_name', 'is_search',
            'is_think', 'location', 'last_login', 'registration_date', 'prompt'
        ]
        
        user = User()
        
        for row in data:
            user_data = dict(zip(columns, row))
            
            user.set_user_id(user_data['user_id'])
            user.set_login(user_data['login'])
            user.set_status(user_data['status_user'])
            user.set_wait_action(user_data['wait_action'])
            user.set_type(user_data['type'])  
            user.set_companyAi(user_data['company_ai'])
            user.set_model(user_data['model'])
            user.set_speaker(user_data['speaker_name'])
            user.set_language(user_data['language_code'])
            user.set_recognizes_photo(user_data['model_rec_photo'])
            user.set_generate_pthoto(user_data['model_gen_photo'])
            user.set_text_to_audio(user_data['text_to_audio'])
            user.set_audio_to_text(user_data['audio_to_text'])
            user.set_is_search(user_data['is_search'])  
            user.set_is_think(user_data['is_think'])  
            user.set_location(user_data['location'])  
            user.set_last_login(user_data['last_login'])
            user.set_registration_date(user_data['registration_date'])
            user.set_prompt(user_data['prompt']) 
        
        return user

    def update_user_lang_code(self, userId, code): 
        query = "UPDATE users SET language_code=%s WHERE user_id=%s;"
        values = (code, userId)
        self.db.execute_query(query, values)

    def update_user_search_status(self, userId, status: bool):
        query = "UPDATE users SET is_search=%s WHERE user_id=%s;"
        values = (status, userId)
        self.db.execute_query(query, values)

    def update_user_think_status(self, userId, status: bool):
        query = "UPDATE users SET is_think=%s WHERE user_id=%s;"
        values = (status, userId)
        self.db.execute_query(query, values)


    # old

    def add_context(self, userId, chatId, role, messageId, message, isPhoto):
        query = "INSERT INTO context VALUES (%s,%s,%s,%s,%s,%s);"
        self.db.execute_query(query, (userId, chatId, role, messageId, str(message), isPhoto) )

    def get_context(self, userId, chatId) -> List[Control.context_model.Context_model]:
        query = "SELECT * FROM context WHERE user_id='{}' AND chat_id='{}';".format(userId, chatId)
        data = self.db.execute_query(query)
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
    
    def add_users_in_groups(self, userId, chatId):
        query = "SELECT add_chats_id("+str(userId)+", '{"+str(chatId) +"}');"
        self.db.execute_query(query)

    def get_all_chat(self, userId):
        query = "SELECT * FROM get_chats_id({});".format(userId)
        data = self.db.execute_query(query)
        return data
    
    def isAdmin(self, userId, username) -> bool:
        query = "SELECT * FROM admins WHERE user_id={};".format(userId)
        data = self.db.execute_query(query)
        
        if len(data) == 1:
            if data[0][0] == userId and data[0][1] == username and data[0][2] != 0:
                return True
        return False
    
    def get_assistant_ai(self):
        query = "select * from assistant_ai;"
        data = self.db.execute_query(query)
        array = []

        for i in data:
            am = assistent_model()
            am.set_model(i[0],i[1],i[2],i[3],i[4],i[5],i[6])
            array.append( am )
        return array
        
    def get_languages(self):
        query = "select * from languages;"
        data = self.db.execute_query(query)
        array = []

        for i in data:
            lm = languages_model()
            lm.set_model(i[0],i[1],i[2])
            array.append( lm )
        return array

    # def get_count_char_for_gen_audio(self) -> int:
    #     query = "select * from default_data where key='count_char_for_gen_audio';"
    #     data = self.db.execute_query(query)

    #     for i in data:
    #         return int( i[1] )
                
    #     return 0

    def update_last_login(self, userId) -> None:
        query = "select from update_last_login({});".format(userId)
        self.db.execute_query(query)

    def get_environment(self):
        query = "select * from default_data;"
        data = self.db.execute_query(query)
        data_dict = {row[0]: row[1] for row in data}
        return data_dict
    
    def update_user_prompt(self, userId, prompt) -> None:
        query = "select from set_user_prompt({}, '{}');".format(userId, prompt)
        self.db.execute_query(query)

    def update_user_action(self, userId, action) -> None:
        query = 'UPDATE users SET wait_action = %s WHERE user_id = %s;'
        self.db.execute_query(query, (action, userId))

    def update_user_search_status(self, user_id: int, is_search: bool) -> None:
        query = 'UPDATE users SET is_search = %s WHERE user_id = %s;'
        self.db.execute_query(query, (is_search, user_id))

    def update_user_think_status(self, user_id: int, is_think: bool) -> None:
        query = 'UPDATE users SET is_think = %s WHERE user_id = %s;'
        self.db.execute_query(query, (is_think, user_id))

    def update_user_location(self, user_id: int, location: str) -> None:
        query = 'UPDATE users SET location = %s WHERE user_id = %s;'
        self.db.execute_query(query, (location, user_id))


    def get_payment_systems(self):
        query = "select * from payment_services;"
        data = self.db.execute_query(query)
        array = []
        for i in data:
                pm = payments_model()
                pm.set_model(i[0],i[1],i[2])
                array.append( pm )
        return array
    
    def add_invoice_journal(self, userId, payment_id, label_pay, tarrif_id, status, amount, currency, payment_system, description, created_at, is_test:bool ):
        query = "INSERT INTO invoice_journal(user_id, payment_id, label_pay, tarrif_id, status, amount, currency, payment_system, description, created_at, is_test) " \
                            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        self.db.execute_query(query, (userId, str(payment_id), str(label_pay), tarrif_id, str(status), amount, str(currency), str(payment_system), str(description), str(created_at), is_test))

    def update_invoice_journal(self, payment_id, label_pay, status, card_type, card_number, fee, expires_at):
        query = 'select from update_invoice_journal(%s,%s,%s,%s,%s,%s,%s);'
        self.db.execute_query(query, (payment_id, label_pay, status, card_type, card_number, fee, expires_at))
    
    def add_successful_payments(self, userId, payment_id, tarrif_id, final_amount, currency, payment_system, card_type, email, expires_at):
        query = "INSERT INTO successful_payments VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        self.db.execute_query(query, (userId, payment_id, tarrif_id, final_amount, currency, payment_system, card_type, email, expires_at))

    def upsert_subscription_user(self, userId, userName, tarrif_id, email, hours, last_payment_id):
        query = "select from upsert_subscription_user(%s,%s,%s,%s,%s,%s);"
        self.db.execute_query(query, (userId, userName, tarrif_id, email, hours, last_payment_id))

    def update_status_in_users(self, userId, status):
        query = 'UPDATE users SET status_user = %s WHERE user_id = %s;'
        self.db.execute_query(query, (status, userId))

    def get_tarif_by_paylabel(self, label) -> int:
        query = "select tarrif_id from invoice_journal where label_pay = '{}'".format(label)
        data = self.db.execute_query(query)
        
        if len(data) == 1:
            for i in data:
                return i[0]
        else:
            return 0

    def get_subscription_users(self) -> List[SubscriptionData]:
        query = "SELECT * FROM public.subscription_users"
        data = self.db.execute_query(query)
        array = []

        for i in data:
            sd = SubscriptionData()

            sd.set_userId(i[0])
            sd.set_tarif(i[2])
            sd.set_active_until(i[5])
            sd.set_last_label(i[6])
            sd.set_id(i[7])

            array.append(sd)

        return array
    
    def remove_subscription_ended(self, label):
        query = "delete from subscription_users where last_payment_id='{}';".format(label)
        self.db.execute_query(query)

    def checking_for_duplicate_payment(self, label):
        query = "SELECT EXISTS (    SELECT 1    FROM successful_payments    WHERE payment_id = '{}' ) AS payment_exists;".format(label)
        data = self.db.execute_query(query)
        
        if len(data) == 1:
            if data[0][0] == True:
                return True
            else:
                return False
            
        return False
    
    def get_tariffs(self) -> List[tariffs_model]:
        query = "SELECT * FROM tariffs;"
        data = self.db.execute_query(query)
        array = []

        for i in data:
            tm = tariffs_model()
            tm.set_model(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7])

            array.append(tm)

        return array




    def __del__(self):
        self.db.close_pool()
#     print(1)
