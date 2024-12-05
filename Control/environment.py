

class Environment():
    def __init__(self):
        self._language = ''
        self._company_ai = ''
        self._permission = ''
        self._assistant_model = ''
        self._recognizes_photo_model = ''
        self._generate_pthoto_model = ''
        self._text_to_audio = ''
        self._audio_to_text = ''
        self._speakerName = ''
        self._count_char_for_gen_audio = ''
        self._sum_max_file_size = ''
        self._prompt = ''

    def set_(self):
        print()

    def get_(self):
        print()

    def is_valid(self):
        if self._sum_max_file_size and self._count_char_for_gen_audio and self._language:
            return True
        else:
            return False

    def update(self, data_dict):
        if data_dict is None:
            print("Нет данных для обновления.")
            return None

        # Обновление переменных на основе данных из словаря
        self._language = data_dict.get("language", self._language)
        self._company_ai = data_dict.get("company_ai", self._company_ai)
        self._permission = data_dict.get("permission", self._permission)
        self._assistant_model = data_dict.get("assistant_model", self._assistant_model)
        self._recognizes_photo_model = data_dict.get("recognizes_photo_model", self._recognizes_photo_model)
        self._generate_pthoto_model = data_dict.get("generate_photo_model", self._generate_pthoto_model)
        self._text_to_audio = data_dict.get("text_to_audio", self._text_to_audio)
        self._audio_to_text = data_dict.get("audio_to_text", self._audio_to_text)
        self._speakerName = data_dict.get("speakerName", self._speakerName)
        self._count_char_for_gen_audio = data_dict.get("count_char_for_gen_audio", self._count_char_for_gen_audio)
        self._sum_max_file_size = data_dict.get("sum_max_file_size", self._sum_max_file_size)
        self._prompt = data_dict.get("prompt", self._prompt)