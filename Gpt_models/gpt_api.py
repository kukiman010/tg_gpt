import openai
import json
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '..'))

import Control.context_model
# from logger         import LoggerSingleton

# _logger = LoggerSingleton.new_instance('log_gpt.log')


class chatgpt():
    def __init__(self, tokenID) -> None:
        self.TOKEN_GPT = tokenID
        openai.api_key = tokenID

    
    def gpt_post_view(self, context, gpt_model, MAX_TOLENS):
        completion = openai.chat.completions.create(
        model=gpt_model,
        messages=context,
        max_tokens=MAX_TOLENS,
        )

        answer = Control.context_model.AnswerAssistent()
        data = json.loads( str( completion.json() ) )
        total_tokens = data['usage']['total_tokens']
        content = data['choices'][0]['message']['content']
        answer.set_answer(200, content, total_tokens)
        return answer


    def post_gpt(self, context, gpt_model, web_search):
        create_args = {
            'model': gpt_model,
            'messages': context
        }
        
        if web_search:
            create_args['tools'] = [{
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Perform a web search to find recent information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }]
            create_args['tool_choice'] = {"type": "function", "function": {"name": "web_search"}}
        
        completion = openai.chat.completions.create(**create_args)

        answer = Control.context_model.AnswerAssistent()
        data = json.loads( str( completion.model_dump_json() ) )
        total_tokens = data['usage']['total_tokens']
        content = data['choices'][0]['message']['content']
        answer.set_answer(200, content, total_tokens)
        return answer

    # def encode_image(self, image_path):
        # with open(image_path, "rb") as image_file:
            # return base64.b64encode(image_file.read()).decode('utf-8')

    def count_tokens(slef, json, model) -> int:
        return 0

