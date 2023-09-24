import subprocess
import threading
import requests
import base64
# import sched
import time
import json
import re

class speaker:
    def __init__(self, TOKEN_FOLDER_ID):
        self.t_folder_id = TOKEN_FOLDER_ID
        self.stop_event = threading.Event()
        self.ready_token = True

        self.t_IAM = self.create_iam()
        if self.t_IAM == '':
            self.ready_token = False

        # scheduler = sched.scheduler(time.monotonic, time.sleep)


    def get_IAM(self):
        return self.t_IAM
    
    def get_filder_id(self):
        return self.t_folder_id
    
    def get_time_string(self):
        current_time = time.time()
        time_struct = time.localtime(current_time)
        return time.strftime("%Y%m%d_%H%M%S", time_struct)
    
    
    def create_iam(self):
        output = subprocess.check_output('yc iam create-token', shell=True, universal_newlines=True)
        lines = output.split("\n")
        pattern = r"^(t1.+)$"

        if len(lines) >2:
            print("Не ожаданный результат, нужно проверить вывод \'yc iam create-token\' \nВывод: {}".format(lines))
        
        for line in lines:
            match = re.findall(pattern, line)
            if match:
                return str(match[0])
            
        return ""
    

    def voice_synthesis_v1(self, text, user):
        url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
        headers = {
            "Authorization": f"Bearer {self.t_IAM}"
        }
        data = {
            "text": text,
            "lang": "ru-RU",
            # "lang": "auto",
            "voice": "filipp",
            "folderId": self.t_folder_id
        }

        response = requests.post(url, headers=headers, data=data)

      
        formatted_datetime = self.get_time_string()

        filename = 'send_voice_{}_{}.ogg'.format(user, formatted_datetime)

        with open('./ready/' + filename, "wb") as file:
            file.write(response.content)

        return str('./ready/' + filename)


    def voice_synthesis_v3(self, text, user): #, voice, language,
        json_str =  json.dumps({
            "text": text,
            "outputAudioSpec": {
            "containerAudio": {"containerAudioType": "WAV"}
            },
            "hints": [
                {"voice": "alena"},
                {"role": "neutral"}
            ],
            "loudnessNormalizationType": "LUFS"
        })
        json_obj = json.loads(json_str)

        command = [
            'grpcurl',
            '-H', f'authorization: Bearer {self.t_IAM}',
            '-H', f'x-folder-id: {self.t_folder_id}',
            '-d', '@',
            'tts.api.cloud.yandex.net:443',
            'speechkit.tts.v3.Synthesizer/UtteranceSynthesis'
        ]
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(json_str.encode('utf-8'))

        json_obj = json.loads(stdout)
        audio_data = json_obj['audioChunk']['data']

        formatted_datetime = self.get_time_string()
        filename = 'send_voice_{}_{}.ogg'.format(user, formatted_datetime)
        # filename = 'send_voice_{}_{}.wav'.format(user, formatted_datetime)

        # Конвертация из base64 в wav
        audio_bytes = base64.b64decode(audio_data)
        with open('./ready/' + filename, 'wb') as file:
            file.write(audio_bytes)

        return str('./ready/' + filename)


    def gen_voice_v1(self, data, user):
        formatted_datetime = self.get_time_string()
        filename = 'voice_{}_{}.ogg'.format(user, formatted_datetime)
        with open('./voice/' + filename, 'wb') as f:
            f.write(data)


        url = f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?folderId={self.t_folder_id}&lang=auto"
        headers = {"Authorization": f"Bearer {self.t_IAM}"}
        binary_data = open('./voice/' + filename, "rb").read()

        response = requests.post(url, headers=headers, data=binary_data)
        
        if response.status_code == 200:
            response_data = response.json()
            return str( response_data['result'] )
        else:
            return ''
        
    # def gen_voice_v3(self, data, user):
        # print("none")




    def start_key_generation(self):
        # Создаем и запускаем отдельный поток для генерации ключа
        thread = threading.Thread(target=self.generate_keys_periodically)
        thread.start()

    def stop_key_generation(self):
        # Останавливаем генерацию ключей
        self.stop_event.set()

    def generate_keys_periodically(self):
        while not self.stop_event.is_set():
            # self.generate_key()
            self.t_IAM = self.create_iam()
            if self.t_IAM == '':
                self.ready_token = False

            print("Сработал планировщик задач для get_yandex_iam. дата: {}".format(self.get_time_string()))
            print(self.t_IAM)
            time.sleep(3600) # 1 hour
