import requests
import Control.context_model

class YandexGpt():
    def __init__(self, token, folder) -> None:
        self._token = token
        self._folder = folder

    def set_token(self, token):
        self._token = token

    def post_gpt(self, context, gpt_model) -> Control.context_model.AnswerAssistent() :
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self._token}',
            'x-data-logging-enabled': 'false',
            'x-folder-id': self._folder
        }

        data = {
        # "modelUri": f"gpt://{self._folder}/{gpt_model}/latest",
        "modelUri": f"gpt://{self._folder}/{gpt_model}",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "2000"
        },
        "messages": context
        }

        response = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            headers=headers,
            json=data
        )

        answer = Control.context_model.AnswerAssistent()
        status_code = response.status_code

        if status_code == 200:
            json = response.json()
            text = json['result']['alternatives'][0]['message']['text']
            total_tokens = json['result']['usage']['totalTokens']
            # model_version = json['result']['modelVersion']
            answer.set_answer(status_code, text, total_tokens)
        else:
            error_message = data['error']['message']
            answer.set_answer(status_code, error_message)

        return answer


    def count_tokens(slef, json, model) -> int:
        return 0
