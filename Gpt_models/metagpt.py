from groq import Groq
import Control.context_model

# https://console.groq.com/keys


class MetaGpt():
    def __init__(self, token) -> None:
        self._token = token
        self._client = Groq(api_key=token)

    def set_token(self, token):
        self._token = token
        self._client.api_key = token

    def post_gpt(self, context, gpt_model) -> Control.context_model.AnswerAssistent :
        # if len(messages) > 6:
        #     messages = messages[-6:]
        response = self._client.chat.completions.create(model=gpt_model, messages=context, temperature=0)

        answer = Control.context_model.AnswerAssistent()
        # status_code = response.status_code
        if self.validate_response(response):
            text = response.choices[0].message.content
            total_tokens = 0
            answer.set_answer(200, text, total_tokens)
        else:
            # error_message = data['error']['message']
            answer.set_answer(404, "Request processing error!")

        return answer

    def count_tokens(slef, json, model) -> int:
        return 0

    def validate_response(self, response) -> bool:
        try:
            if response and hasattr(response, 'choices') and response.choices:
                if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                    return True
        except Exception as e:
            print(f'Error validating response: {e}')
        return False



# import requests
# import json

# url = 'https://api.aimlapi.com/chat/completions'
# api_token = 'TOKEN_API'  # Замените на ваш API токен

# headers = {
#     'Content-Type': 'application/json',
#     'Accept': 'application/json',
#     'Authorization': f'Bearer {api_token}'  
# }

# data = {
#     #"model": "mistralai/Mistral-7B-Instruct-v0.2",
#     "model": "meta-llama/Meta-Llama-3-70B",
#     "messages": [
#         {
#             "role": "user",
#             "content": "кто был противником в войне 1812 года?"
#         }
#         # ,
#         # {
#         #     "role": "assistant",
#         #     "content": "The Los Angeles Dodgers won the World Series in 2020."
#         # },
#         # {
#         #     "role": "user",
#         #     "content": "Where was it played?"
#         # }
#     ],
#     "temperature": 1,
#     "top_p": 1,
#     "n": 1,
#     "stream": False,
#     "max_tokens": 250,
#     "presence_penalty": 0,
#     "frequency_penalty": 0
# }

# response = requests.post(url, headers=headers, data=json.dumps(data))

# if response.status_code == 200:
#     response_data = response.json()
#     print(json.dumps(response_data, indent=4))
# else:
#     print(f"Failed to get response: {response.status_code}")
#     print(response.text)