from logger         import LoggerSingleton

_logger = LoggerSingleton.new_instance('log_gpt.log')

class Environment():
    def __init__(self):
        self._language = ''
        self._company_ai = ''
        self._permission = ''
        self._assistant_model = ''
        self._recognizes_photo_model = ''
        self._generate_photo_model = ''
        self._text_to_audio = ''
        self._audio_to_text = ''
        self._speakerName = ''
        self._count_char_for_gen_audio = ''
        self._sum_max_file_size = ''
        self._prompt = ''

    def is_valid(self):
        if self._sum_max_file_size and self._count_char_for_gen_audio and self._language:
            return True
        else:
            return False

    def update(self, data_dict):
        if data_dict is None:
            _logger.add_critical('Нет данных для обновления.')
            return False

        self._language = data_dict.get("language", self._language)
        self._company_ai = data_dict.get("company_ai", self._company_ai)
        self._permission = data_dict.get("permission", self._permission)
        self._assistant_model = data_dict.get("assistant_model", self._assistant_model)
        self._recognizes_photo_model = data_dict.get("recognizes_photo_model", self._recognizes_photo_model)
        self._generate_photo_model = data_dict.get("generate_photo_model", self._generate_photo_model)
        self._text_to_audio = data_dict.get("text_to_audio", self._text_to_audio)
        self._audio_to_text = data_dict.get("audio_to_text", self._audio_to_text)
        self._speakerName = data_dict.get("speakerName", self._speakerName)
        self._count_char_for_gen_audio = data_dict.get("count_char_for_gen_audio", self._count_char_for_gen_audio)
        self._sum_max_file_size = data_dict.get("sum_max_file_size", self._sum_max_file_size)
        self._prompt = data_dict.get("prompt", self._prompt)
        
        return self.is_valid()
    
    def show_differences(self, data_dict, template):
        if data_dict is None:
            _logger.add_error('Нет данных для сверки.')
            return ""

        mes =''
        for key, new_value in data_dict.items():
            current_value = getattr(self, f'_{key}', None)
            if current_value != new_value:
                mes += str(template.format(key,current_value, new_value) +'\n')
        
        return mes


    def get_language(self):
        return self._language
    
    def get_company_ai(self):
        return self._company_ai
    
    def get_permission(self):
        return self._permission
    
    def get_assistant_model(self):
        return self._assistant_model
    
    def get_recognizes_photo_model(self):
        return self._recognizes_photo_model
    
    def get_generate_pthoto_model(self):
        return self._generate_pthoto_model
    
    def get_text_to_audio(self):
        return self._text_to_audio
    
    def get_audio_to_text(self):
        return self._audio_to_text
    
    def get_speakerName(self):
        return self._speakerName
    
    def get_count_char_for_gen_audio(self):
        return self._count_char_for_gen_audio
    
    def get_sum_max_file_size(self):
        return self._sum_max_file_size
    
    def get_prompt(self):
        return self._prompt