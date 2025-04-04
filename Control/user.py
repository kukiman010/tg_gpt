class User:
    def __init__(self) -> None:
        self._user_id =                 0
        self._login =                   ''
        self._status =                  1  # 0-lock, 1-default user, 2-donater
        self._companyAi =               'openAi'
        self._model =                   "gpt-3.5-turbo"
        self._speakerName =             "alena"
        self._language =                'en_EN'
        
        self._wait_action =             ""
        self._model_recognizes_photo =  "gpt-4o"
        self._model_generate_photo =    "dall-e3"
        self._text_to_audio =           "yandex"
        self._audio_to_text =           "yandex"
        self._registration_date =       ""
        self._last_login =              ""
        self._prompt =                  ""
        self._is_search =               False
        self._is_think =                False
        self._location =                ""
        self._type =                    ""

        #statistics
        # self._send_mess = 0
        # self._send_image = 0
        # self._send_audio = 0
        # self._dropContext = 0
        # self._start_time = None
        # self._lastActivity = None
        # self._donate = 0

    def is_active(self):
        return self._user_id != 0 and self._login != ''
        
    def set_default_data(self, language, permission, company_ai, assistant_model, 
                        recognizes_photo_model, generate_photo_model, 
                        text_to_audio, audio_to_text, speakerName, prompt):
        self._status = permission  
        self._companyAi = company_ai
        self._model = assistant_model
        self._speakerName = speakerName
        self._language = language
        self._model_recognizes_photo = recognizes_photo_model
        self._model_generate_photo = generate_photo_model
        self._text_to_audio = text_to_audio
        self._audio_to_text = audio_to_text
        self._prompt = prompt

    def set_base_info(self, userId, login, status, companyAi, model, speakerName, 
                     language, wait_action, model_recognizes_photo, 
                     model_generate_photo, text_to_audio, audio_to_text, 
                     last_login, reg_date, prompt, is_search=False, 
                     is_think=False, location="", type=""):
        self._user_id = userId
        self._login = login
        self._status = status  
        self._companyAi = companyAi
        self._model = model
        self._speakerName = speakerName
        self._language = language
        self._wait_action = wait_action
        self._model_recognizes_photo = model_recognizes_photo
        self._model_generate_photo = model_generate_photo
        self._text_to_audio = text_to_audio
        self._audio_to_text = audio_to_text
        self._last_login = last_login
        self._registration_date = reg_date
        self._prompt = prompt
        self._is_search = is_search
        self._is_think = is_think
        self._location = location
        self._type = type


    def get_userId(self):
        return self._user_id
    def get_login(self):
        return self._login 
    def get_status(self):
        return self._status
    def get_companyAi(self):
        return self._companyAi 
    def get_model(self):
        return self._model 
    def get_speaker(self):
        return self._speakerName 
    def get_language(self):
        return self._language 
    def get_wait_action(self):
        return self._wait_action
    def get_model_recognizes_photo(self):
        return self._model_recognizes_photo
    def get_model_generate_photo(self):
        return self._model_generate_photo
    def get_text_to_audio(self):
        return self._text_to_audio
    def get_audio_to_text(self):
        return self._audio_to_text
    def get_prompt(self):
        return self._prompt
    def get_last_login(self):
        return self._last_login
    def get_registration_date(self):
        return self._registration_date
    def get_is_search(self) -> bool:
        return self._is_search
    def get_is_think(self) -> bool:
        return self._is_think
    def get_location(self) -> str:
        return self._location
    def get_type(self) -> str:
        return self._type



    def set_user_id(self, value):
        self._user_id = value
    def set_login(self, value):
        self._login = value
    def set_status(self, value):
        self._status = value  
    def set_companyAi(self, company):
        self._companyAi = company
    def set_model(self, model):
        self._model = model
    def set_speaker(self, value):
        self._speakerName = value
    def set_language(self, value):
        self._language = value
    def set_wait_action(self, value):
        self._wait_action = value
    def set_recognizes_photo(self, value):
        self._model_recognizes_photo = value
    def set_generate_pthoto(self, value):
        self._model_generate_photo = value
    def set_text_to_audio(self, value):
        self._text_to_audio = value
    def set_audio_to_text(self, value):
        self._audio_to_text = value
    def set_last_login(self, value):
        self._last_login = value
    def set_registration_date(self, value):
        self._registration_date = value
    def set_prompt(self, value):
        self._prompt = value
    def set_is_search(self, value: bool):
        self._is_search = value
    def set_is_think(self, value: bool):
        self._is_think = value
    def set_location(self, value: str):
        self._location = value
    def set_type(self, value: str):
        self._type = value