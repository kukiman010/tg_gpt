
class User:
    def __init__(self) -> None:
        self._user_id = 0
        # self._userChats_id = []
        self._login = ''
        self._isAdmin = False
        self._status = 1  # 0-lock, 1-default user, 2-donater
        # self._name = ''
        self._companyAi = 'openAi'
        self._model = "gpt-3.5-turbo"
        self._speakerName = "alena"
        self._contextSize = 0
        self._language = 'en_EN'

        #statistics
        # self.gender = ''
        self._send_mess = 0
        self._send_image = 0
        self._send_audio = 0
        self._dropContext = 0
        self._start_time = None
        self._lastActivity = None
        self._donate = 0


    def is_active(self):
        if self._user_id != 0 and self._login != '':
            return True
        else:
            return False

    def set_base_info(self, userId, login, isAdmin, status, companyAi, model, speakerName, contextSize, language):
        self._user_id = userId
        # self._userChats_id = chatsId
        self._login = login
        self._isAdmin = isAdmin
        self._status = status  
        # self._name = name
        self._companyAi = companyAi
        self._model = model
        self._speakerName = speakerName
        self._contextSize = contextSize
        self._language = language

    def set_statistics(self,c_message, c_image, c_audio, c_dropContext, createTime, lastQueryTime, donate):
        self._send_mess = c_message
        self._send_image = c_image
        self._send_audio = c_audio
        self._dropContext = c_dropContext
        self._start_time = createTime
        self._lastActivity = lastQueryTime
        self._donate = donate


    def get_userId(self):
        return self._user_id
    # def get_userChatsId(self):
        # return self._userChats_id
    def get_login(self):
        return self._login 
    def get_isAdmin(self):
        return self._isAdmin 
    def get_status(self):
        return self._status
    # def get_name(self):
        # return self._name 
    def get_companyAi(self):
        return self._companyAi 
    def get_model(self):
        return self._model 
    def get_speaker(self):
        return self._speakerName 
    def get_contextSize(self):
        return self._contextSize 
    def get_language(self):
        return self._language 
    

    def get_count_mess(self):
        return self._send_mess 
    def get_count_image(self):
        return self._send_image 
    def get_count_audio(self):
        return self._send_audio 
    def get_count_cropcontext(self):
        return self._dropContext 
    def get_createTime(self):
        return self._start_time 
    def get_lastActivity(self):
        return self._lastActivity 
    def get_donate(self):
        return self._donate


    def set_companyAi(self, company):
        self._companyAi = company
    def set_model(self, model):
        self._model  = model
