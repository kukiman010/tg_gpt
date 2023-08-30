import configparser
import os


class Settings:
    def __init__(self):
        self.base_way = os.path.dirname(os.path.realpath(__file__)) + '/'

        self.config = configparser.ConfigParser()
        self.isInitDB = False        

        self.config['Database'] = {'host': 'localhost', 'port': '5432', 'user': 'postgres', 'password': '123'}

        if self.folder_exist(self.base_way + 'conf/') == False:
            self.folder_create(self.base_way + 'conf')

        if self.file_exist(self.base_way + 'conf/tg_token.txt') == False:
            self.file_create(self.base_way + 'conf/tg_token.txt')

        if self.file_exist(self.base_way + 'conf/tg_chatgpt.txt') == False:
            self.file_create(self.base_way + 'conf/tg_chatgpt.txt')

        if self.file_exist(self.base_way + 'conf/db_config.ini') :
            isInitDB = self.db_conf_read()
        else:
            isInitDB = self.db_conf_create()

        
        

    def get_path(self):
        # self.baseway
        return self.base_way
    

    # get telegram bot token
    def get_tgToken(self):
        TOKEN_TG = ""
        if not( os.path.exists(self.base_way + "/tg_token.txt") ):
            file = open(self.base_way + "/tg_token.txt", 'w')
            file.close()
            print("Файл был создан для tg bot!")
        else:
            file = open(self.base_way + "/tg_token.txt", 'r')
            TOKEN_TG = file.read()
            if TOKEN_TG == '':
                print("Не задан токен для tg bot!") 
            file.close()
            return TOKEN_TG
        

    # get chatgpt token
    def get_cGptToken(self):
        TOKEN_GPT = ""
        if not( os.path.exists(self.base_way + "/tg_chatgpt.txt") ):
            file = open(self.base_way + "/tg_chatgpt.txt", 'w')
            file.close()
            print("Файл был создан для chatgpt!")
        else:
            file = open(self.base_way + "/tg_chatgpt.txt", 'r')
            TOKEN_GPT = file.read()
            if TOKEN_GPT == '':
                print("Не задан токен для chatgpt!") 
            file.close()
        return TOKEN_GPT


    def file_exist(self, file_path):
        if os.path.exists(file_path):
            return True
        else:
            return False

    def file_create(self, file_path):
        with open(file_path, 'w') as file:
            file.write('')
        


    def folder_exist(self, folder_path):
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            return True
        else:
            return False

    def folder_create(self, folder_path):
        os.mkdir(folder_path)



    def db_conf_create(self):
        with open(self.base_way + 'conf/db_config.ini', 'w') as configfile:
            self.config.write(configfile)
        
        return self.file_exist(self.base_way + 'conf/db_config.ini') 
            

    def db_conf_read(self):
        if self.base_way + 'conf/db_config.ini' in self.config.read(self.base_way + 'conf/db_config.ini'):
            return True
        else:
            return False


    def get_db_host(self):
        return self.config['Database']['host']

    def get_db_port(self):
        return self.config['Database']['port']

    def get_db_user(self):
        return self.config['Database']['user']

    def get_db_pass(self):
        return self.config['Database']['password']



