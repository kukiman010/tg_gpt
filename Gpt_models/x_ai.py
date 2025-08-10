# https://docs.x.ai/docs#access
# https://docs.x.ai/api/endpoints

import requests
import json
import sys
import os
from openai import OpenAI
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '..'))

import Control.context_model
# from logger         import LoggerSingleton
from openai         import OpenAI

# _logger = LoggerSingleton.new_instance('logs/log_gpt.log')


class Xai():
    def __init__(self, tokenID) -> None:
        self.TOKEN = tokenID
        self._client = OpenAI(
            api_key=tokenID,
            base_url="https://api.x.ai/v1",
        )

    def post_gpt(self, gpt_model, context):
        completion = self._client.chat.completions.create(
            model=gpt_model,
            messages = context
        )

        answer = Control.context_model.AnswerAssistent()
        data = json.loads( str( completion.model_dump_json() ))
        total_tokens = data['usage']['total_tokens']
        content = data['choices'][0]['message']['content']
        answer.set_answer(200, content, total_tokens)
        return answer


    def gpt_post_view(self, context, gpt_model, MAX_TOLENS):
        answer = Control.context_model.AnswerAssistent()
        answer.set_answer(400, 'no', 0)
        return answer

    def count_tokens(slef, json, model) -> int:
        return 0
