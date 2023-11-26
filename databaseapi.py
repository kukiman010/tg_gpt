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
            if data[0][0] == userId:
                return True

        return False

    # def create_user(self, userId, username, status, type):
    #     self.db.connect()
    #     query = "INSERT INTO users VALUES ({},'{}', {}, '{}');".format(userId,username,status,type)
    #     self.db.execute_query(query)
    #     # data = self.db.fetch_all()
    #     self.db.commit()
    #     self.db.close()
    

    def create_user(self, userId, username, isAdmin, status_user, type, companyAI,model, speaker_name, contextSize, language_code):
        self.db.connect()
        query = "INSERT INTO users VALUES ({}, '{}', {}, {}, '{}', '{}', '{}', '{}', {}, '{}');".format(userId,username,isAdmin,status_user,type,companyAI,model,speaker_name,contextSize,language_code)
        self.db.execute_query(query)
        self.db.commit()
        self.db.close()   


    def add_context(self, userId, chatId, role, messageId, message, isPhoto):
        self.db.connect()
        query = "INSERT INTO context VALUES (%s,%s,%s,%s,%s,%s);"
        self.db.custom_execute_query(query, (userId, chatId, role, messageId, str(message), isPhoto) )

        self.db.commit()
        self.db.close()

    def get_context(self, userId, chatId):
        self.db.connect()
        query = "SELECT * FROM context WHERE user_id='{}' AND chat_id='{}';".format(userId, chatId)
        self.db.execute_query(query)
        data = self.db.fetch_all()
        self.db.commit()
        self.db.close()

        result = []

        for i in data:
            role = str(i[2])
            content = i[4]

            if i[5] == False:
                result.append({"role": role, "content": content})
            else:
                result.append( {"role": role,"content": [
            {"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{content}"},},
            ]} )
            # json_string = i[4].replace("\'", '"').replace('\\', '')
            # data = 
            # result.append( json.loads(json_string) )

        # print( result )
        return result
    
    def delete_user_context(self, userId, chatId):
        self.db.connect()
        query = "DELETE FROM context WHERE user_id='{}' AND chat_id='{}';".format(userId, chatId)
        self.db.execute_query(query)
        self.db.commit()
        self.db.close()
    

    def add_users_in_groups(self, userId, chatId):
        self.db.connect()
        query = "SELECT add_chats_id("+str(userId)+", '{"+str(chatId) +"}');"
        self.db.execute_query(query)
        self.db.commit()
        self.db.close()

    def get_all_chat(self, userId):
        self.db.connect()
        query = "SELECT * FROM get_chats_id({});".format(userId)
        self.db.execute_query(query)
        data = self.db.fetch_all()
        self.db.commit()
        self.db.close()
        return data
    

    def isAdmin(self, userId, username):
        self.db.connect()
        query = "SELECT * FROM admins WHERE user_id={};".format(userId)
        self.db.execute_query(query)
        data = self.db.fetch_all()
        self.db.commit()
        self.db.close()
        if len(data) == 1:
            if data[0][0] == userId and data[0][1] == username and data[0][2] != 0:
                return True
        return False

    # def get_user(self)

    # def (self):
    #     print('')

    