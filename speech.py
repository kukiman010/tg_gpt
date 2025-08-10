# https://pypi.org/project/yandex-speechkit/
import subprocess
import threading
import time
import re

from speechkit import model_repository, configure_credentials, creds
from speechkit.stt import AudioProcessingType
from logger         import LoggerSingleton


class speaker:
    def __init__(self):
        self.stop_event = threading.Event()
        self._logger = LoggerSingleton.new_instance('logs/log_gpt.log')
        self.ready_token = True
        self.TIME_GEN=18000 # once to timer (18000 = 5 hours)

        self.t_IAM = self.create_iam()
        if self.t_IAM == '':
            self.ready_token = False
            self._logger.add_critical("Токен IAM не создался ")
        else:
            self._logger.add_info("Токен IAM cоздан!")


        with open("conf/yandex_api.key", "r", encoding="utf-8") as file:
            self.api_key = file.read()
        configure_credentials(
            yandex_credentials=creds.YandexCredentials(
                api_key=self.api_key
            )
        )

    def get_IAM(self):
        return self.t_IAM
    
    # def get_filder_id(self):
        # return self.t_folder_id

    
    def get_time_string(self):
        current_time = time.time()
        time_struct = time.localtime(current_time)
        milliseconds = int((current_time - int(current_time)) * 1000)
        return time.strftime("%Y%m%d_%H%M%S", time_struct) + f"_{milliseconds:03d}"
    
    
    def create_iam(self):
        output = subprocess.check_output('yc iam create-token', shell=True, universal_newlines=True)
        lines = output.split("\n")
        pattern = r"^(t1.+)$"

        if len(lines) >2:
            self._logger.add_warning("Не ожаданный результат, нужно проверить вывод \'yc iam create-token\' \nВывод: {}".format(lines))
        
        for line in lines:
            match = re.findall(pattern, line)
            if match:
                return str(match[0])
            
        return ""
    
    def start_key_generation(self): # Создаем и запускаем отдельный поток для генерации ключа
        thread = threading.Thread(target=self.generate_keys_periodically)
        thread.start()
        self._logger.add_info("Запущен сценарий генерации токена")

    def stop_key_generation(self): # Останавливаем генерацию ключей
        self.stop_event.set()
        self._logger.add_info("Остановлен сценарий генерации токена")

    def generate_keys_periodically(self):
        while not self.stop_event.is_set():
            self.t_IAM = self.create_iam()
            if self.t_IAM == '':
                self.ready_token = False
                self._logger.add_critical("Токен IAM не создался ")

            self._logger.add_info("Сработал планировщик задач для get_yandex_iam. раз в {} ч".format(int(self.TIME_GEN/60)/60))
            time.sleep(self.TIME_GEN) 

    

    def split_text(self, text):
        max_message_length = 4250
        hard_break_point = 3900
        soft_break_point = 3500
        results = []

        while len(text) > max_message_length:
            offset = text[soft_break_point:hard_break_point].rfind('\n')
            if offset == -1:
                offset = text[soft_break_point:max_message_length].rfind(' ')
            if offset == -1:
                results.append(text[:max_message_length])
                text = text[max_message_length:]
            else:
                original_index = offset + soft_break_point
                results.append(text[:original_index])
                text = text[original_index:]

        if text:
            results.append(text)

        return results


    def speach(self, text, user, speaker='alena'):
        model = model_repository.synthesis_model()

        model.voice = speaker
        model.model = 'general'
        model.role = 'good'

        split_text = []
        if len(text) > 4500:
            # split_text = self.split_text_sentences(text)
            split_text = self.split_text(text)
        else: 
            split_text.append(text)

        result_paths = []

        for chunk in split_text:
            result = model.synthesize(chunk, raw_format=False)  # returns audio as pydub.AudioSegment

            formatted_datetime = self.get_time_string()
            filename_ogg = f'send_voice_{user}_{formatted_datetime}.ogg'  
            file_path = f'./users_media/ready/{filename_ogg}'

            result.export(file_path, format="ogg")
            result_paths.append(file_path)


        return result_paths
    


    def recognize(self, file) -> str:
        model = model_repository.recognition_model()

        model.model = 'general:rc'
        # model.language = 'ru-RU'
        model.audio_processing_type = AudioProcessingType.Full

        result = model.transcribe_file(file)
        result_text = ''
        for c, res in enumerate(result):
            result_text += res.normalized_text

        return result_text
    


