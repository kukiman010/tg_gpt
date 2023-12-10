import threading
import requests
import time

import Control.context_model

class Sber_gpt:
    def __init__(self, authorization_data, rq_uid, isSertificat:bool):
        self.authorization_data = authorization_data
        self.rq_uid = rq_uid
        self.stop_event = threading.Event()
        self.sertificat : bool = isSertificat
        self.TIME_GEN=900 # once to timer (900 = 15 minuts)
        self.token = self.create_token()


    def set_serteficat(self, bo):
        self.sertificat  = bo

    def create_token(self) -> str:
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        headers = {
            'Authorization': f'Basic {self.authorization_data}',
            'RqUID': self.rq_uid,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'scope':'GIGACHAT_API_PERS'}

        # if self.isSertificat == True:
        if self.sertificat == 'True':
            response = requests.post(url, headers=headers, data=data)               # for linux
        else:
            response = requests.post(url, headers=headers, data=data, verify=False) # for windows

        status_code = response.status_code

        if status_code == 200:
            json = response.json()
            return json['access_token']
        else:
            return ""
        

    def count_tokens(slef, json, model) -> int:
        return 0


    def post_gpt(self, context, model):
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": 'Bearer {}'.format(self.token)
        }
        data = {
            "model": "{}:latest".format(model),
            # "model": "GigaChat:latest",
            "messages": context,
            "temperature": 0.5
        }

        if self.sertificat == 'True':
            response = requests.post(url, headers=headers, data=data)               # for linux
        else:
            response = requests.post(url, headers=headers, data=data, verify=False) # for windows


        answer = Control.context_model.AnswerAssistent()
        status_code = response.status_code
        json = response.json()

        if status_code == 200:
            content = json["choices"][0]["message"]["content"]
            total_tokens = json["usage"]["total_tokens"]
            answer.set_answer(status_code, content, total_tokens)
        else:
            error_message = json["message"]
            answer.set_answer(status_code, error_message)
            
        return answer


    def start_key_generation(self): # Создаем и запускаем отдельный поток для генерации ключа
        thread = threading.Thread(target=self.generate_keys_periodically)
        thread.start()
        # self._logger.add_info("Запущен сценарий генерации токена")

    def stop_key_generation(self): # Останавливаем генерацию ключей
        self.stop_event.set()
        # self._logger.add_info("Остановлен сценарий генерации токена")

    def generate_keys_periodically(self):
        while not self.stop_event.is_set():
            self.token = self.create_token()
            if self.t_IAM == '':
                self.ready_token = False
                # self._logger.add_critical("Токен IAM не создался ")
                # self._logger.add_info("Сработал планировщик задач для get_yandex_iam. раз в {} ч".format(int(self.TIME_GEN/60)/60))
                time.sleep(self.TIME_GEN) 

