import configparser
# import subprocess
import os
# import re


class Settings:
    def __init__(self):
        self.base_way = os.path.dirname(os.path.realpath(__file__)) + '/'

        self.config = configparser.ConfigParser()
        self.sberConfig = configparser.ConfigParser()
        self.isInitDB = False
        self.isInitSber = False   

        self.config['Database'] = {'host': 'localhost', 'port': '5432', 'dbname': 'base', 'user': 'postgres', 'password': '123'}
        self.sberConfig['Conf'] = {'reg_data': -1, 'guid': -1, 'certificate': True}

        if self.folder_exist(self.base_way + 'conf/') == False:
            self.folder_create(self.base_way + 'conf')

        if self.folder_exist(self.base_way + 'voice/') == False:
            self.folder_create(self.base_way + 'voice')

        if self.folder_exist(self.base_way + 'photos/') == False:
            self.folder_create(self.base_way + 'photos')

        if self.folder_exist(self.base_way + 'ready/') == False:
            self.folder_create(self.base_way + 'ready')

        if self.folder_exist(self.base_way + 'locale/') == False:
            self.folder_create(self.base_way + 'locale')

        if self.folder_exist(self.base_way + 'files/') == False:
            self.folder_create(self.base_way + 'files')

        if self.folder_exist(self.base_way + 'static/') == False:
            self.folder_create(self.base_way + 'static')

        if self.file_exist(self.base_way + 'conf/tg_token.txt') == False:
            self.file_create(self.base_way + 'conf/tg_token.txt')

        if self.file_exist(self.base_way + 'conf/tg_chatgpt.txt') == False:
            self.file_create(self.base_way + 'conf/tg_chatgpt.txt')

        if self.file_exist(self.base_way + 'conf/yandex_folderId.txt') == False:
            self.file_create(self.base_way + 'conf/yandex_folderId.txt')

        if self.file_exist(self.base_way + 'conf/meta_config.ini') == False:
            self.file_create(self.base_way + 'conf/meta_config.ini')

        if self.file_exist(self.base_way + 'conf/db_config.ini') :
            self.isInitDB = self.db_conf_read()
        else:
            self.isInitDB = self.db_conf_create()

        if self.file_exist(self.base_way + 'conf/sber_config.ini') :
            self.isInitSber = self.sber_conf_read()
        else:
            self.isInitSber = self.sber_conf_create()
        

    def get_path(self):
        # self.baseway
        return self.base_way
    

    # get telegram bot token
    def get_tgToken(self):
        TOKEN_TG = ""
        if not( os.path.exists(self.base_way + "conf/tg_token.txt") ):
            file = open(self.base_way + "conf/tg_token.txt", 'w')
            file.close()
        else:
            file = open(self.base_way + "conf/tg_token.txt", 'r')
            TOKEN_TG = file.read()
            file.close()
            return TOKEN_TG
        

    # get chatgpt token
    def get_cGptToken(self):
        TOKEN_GPT = ""
        if not( os.path.exists(self.base_way + "conf/tg_chatgpt.txt") ):
            file = open(self.base_way + "conf/tg_chatgpt.txt", 'w')
            file.close()
        else:
            file = open(self.base_way + "conf/tg_chatgpt.txt", 'r')
            TOKEN_GPT = file.read()
            file.close()
        return TOKEN_GPT
    

    # get yandex folder id
    def get_yandex_folder(self):
        TOKEN_FOLDER = ""
        if not( os.path.exists(self.base_way + "conf/yandex_folderId.txt") ):
            file = open(self.base_way + "conf/yandex_folderId.txt", 'w')
            file.close()
        else:
            file = open(self.base_way + "conf/yandex_folderId.txt", 'r')
            TOKEN_FOLDER = file.read()
            file.close()
        return TOKEN_FOLDER
    

    def get_meta_gpt(self):
        TOKEN_FOLDER = ""
        if not( os.path.exists(self.base_way + "conf/meta_config.ini") ):
            file = open(self.base_way + "conf/meta_config.ini", 'w')
            file.close()
        else:
            file = open(self.base_way + "conf/meta_config.ini", 'r')
            TOKEN_FOLDER = file.read()
            file.close()
        return TOKEN_FOLDER


    # def get_yandex_iam(self):
    #     output = subprocess.check_output('yc iam create-token', shell=True, universal_newlines=True)
    #     lines = output.split("\n")
    #     pattern = r"^(t1.+)$"

    #     if len(lines) >2:
    #         print("Не ожаданный результат, нужно проверить вывод \'yc iam create-token\' \nВывод: {}".format(lines))
       
    #     for line in lines:
    #         match = re.findall(pattern, line)
    #         if match:
    #             return str(match[0])


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
        

    def sber_conf_create(self):
        with open(self.base_way + 'conf/sber_config.ini', 'w') as configfile:
            self.sberConfig.write(configfile)
        
        return self.file_exist(self.base_way + 'conf/sber_config.ini') 
    
    def sber_conf_read(self):
        if self.base_way + 'conf/sber_config.ini' in self.sberConfig.read(self.base_way + 'conf/sber_config.ini'):
            return True
        else:
            return False


    def get_db_host(self):
        return self.config['Database']['host']

    def get_db_port(self):
        return self.config['Database']['port']
    
    def get_db_dbname(self):
        return self.config['Database']['dbname']

    def get_db_user(self):
        return self.config['Database']['user']

    def get_db_pass(self):
        return self.config['Database']['password']
    

    def get_sber_regData(self):
        return self.sberConfig['Conf']['reg_data']
    
    def get_sber_guid(self):
        return self.sberConfig['Conf']['guid']
    
    def get_sber_certificate(self) -> bool:
        return self.sberConfig['Conf']['certificate']



