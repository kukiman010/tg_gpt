from database import Database


class dbApi:
    def __init__(self, dbname, user, password, host, port):
        self.db = Database(dbname,user, password, host, port)


    def find_user(self, userId):
        self.db.connect()
        query = "SELECT * FROM users WHERE user_id='{}';".format(userId)
        self.db.execute_query(query)
        data = self.db.fetch_all()
        self.db.commit()
        self.db.close()
        # print(data)

        if len(data) == 1:
            # return data[0][0]
            if data[0][0] == userId:
                return True

        return False

    def create_user(self, userId, username, status, type):
        self.db.connect()
        query = "INSERT INTO users VALUES ({},'{}', {}, '{}');".format(userId,username,status,type)
        self.db.execute_query(query)
        # data = self.db.fetch_all()
        self.db.commit()
        self.db.close()
    
    


    def add_context(self, userId, chatId, role, messageId, message):
        self.db.connect()
        query = "INSERT INTO context VALUES ({},{}, '{}', {}, '{}');".format(userId, chatId, role, messageId, message)
        self.db.execute_query(query)
        self.db.commit()
        self.db.close()

    def get_context(self, userId, chatId):
        self.db.connect()
        query = "SELECT * FROM context WHERE user_id='{}' AND chat_id='{}';".format(userId, chatId)
        self.db.execute_query(query)
        data = self.db.fetch_all()
        self.db.commit()
        self.db.close()
        return data
    
    def delete_user_context(self, userId, chatId):
        self.db.connect()
        query = "DELETE FROM context WHERE user_id='{}' AND chat_id='{}';".format(userId, chatId)
        self.db.execute_query(query)
        self.db.commit()
        self.db.close()
    



    def add_users_in_groups(self, userId, chatId):
        self.db.connect()
        query = "SELECT add_chats_id({}, '\{{}\}');".format(userId, chatId)
        self.db.execute_query(query)
        self.db.commit()
        self.db.close()

    def get_all_chat(self, userId):
        self.db.connect()
        query = "SELECT * FROM get_chats_id({});".format(userId)
        self.db.execute_query(query)
        self.db.commit()
        self.db.close()


    
    # def (self):
    #     print('')

    # def (self):
    #     print('')

    
