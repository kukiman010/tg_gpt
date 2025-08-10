from openai import (
    OpenAI,
    APIError,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    APIStatusError
)
import tiktoken
import json
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '..'))

import Control.context_model
from logger         import LoggerSingleton

_logger = LoggerSingleton.new_instance('logs/log_gpt.log')


class chatgpt():
    def __init__(self, tokenID: str) -> None:
        
        self.TOKEN = tokenID
        try:
            self.client = OpenAI(api_key=self.TOKEN)
        except Exception as e:
            _logger.add_error(f"Source: {str(self.__class__.__name__)}. Client initialization failed: {str(e)}")
            raise

    
    def gpt_post_view(self, context, gpt_model, MAX_TOLENS):
        completion = self.client.chat.completions.create(
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


    def post_gpt(self, context: str, gpt_model: list, web_search: bool = False) -> Control.context_model.AnswerAssistent:
        answer = Control.context_model.AnswerAssistent()
        tool = None

        if not gpt_model:
            answer.set_answer(400, "Model name is required", 0)
            return answer
            
        if not isinstance(context, list) or len(context) == 0:
            answer.set_answer(400, "Context must be a non-empty list", 0)
            return answer

        if web_search:
            tool=[{
                    "type": "web_search_preview",
                    "search_context_size": "medium",
                }]
        

        try:
            if web_search:
                response = self.client.responses.create(
                    model=gpt_model,
                    tools=tool,
                    input=context
                )
            else:
                response = self.client.chat.completions.create(
                    model=gpt_model,
                    messages=context
                )
                

        except AuthenticationError as e:
            _logger.add_error(f"Source: {str(self.__class__.__name__)}. Authentication failed: {str(e)}")
            answer.set_answer(401, "Invalid API token", 0)
            return answer
        except RateLimitError as e:
            _logger.add_error(f"Source: {str(self.__class__.__name__)}. Rate limit exceeded: {str(e)}")
            answer.set_answer(429, "API rate limit exceeded", 0)
            return answer
        except APIConnectionError as e:
            _logger.add_error(f"Source: {str(self.__class__.__name__)}. Connection error: {str(e)}")
            answer.set_answer(503, "Network connection error", 0)
            return answer
        except APITimeoutError as e:  # Исправлено: используем APITimeoutError вместо Timeout
            _logger.add_error(f"Source: {str(self.__class__.__name__)}. Request timeout: {str(e)}")
            answer.set_answer(504, "Request timeout", 0)
            return answer
        except APIStatusError as e:  
            error_msg = f"API Error: {e.message}"
            if e.status_code == 402:
                error_msg = "Insufficient API balance"
            _logger.add_error(f"Source: {str(self.__class__.__name__)}. HTTP Error {e.status_code}: {error_msg}")
            answer.set_answer(e.status_code, error_msg, 0)
            return answer
        except APIError as e:
            _logger.add_error(f"Source: {str(self.__class__.__name__)}. Generic API error: {str(e)}")
            answer.set_answer(500, "Internal API error", 0)
            return answer
        except Exception as e:
            _logger.add_error(f"Source: {str(self.__class__.__name__)}. Unexpected error: {str(e)}")
            answer.set_answer(500, "Unknown error occurred", 0)
            return answer

        try:
            total_tokens = 0
            if web_search:
                content = response.output_text
            else:
                content = response.choices[0].message.content
                total_tokens = response.usage.total_tokens
        except (AttributeError, IndexError, KeyError) as e:
            _logger.add_error(f"Source: {str(self.__class__.__name__)}. Invalid API response format: {str(e)}")
            answer.set_answer(500, "Invalid API response format", 0)
            return answer

        answer.set_answer(200, content, total_tokens)
        return answer
        


    # def encode_image(self, image_path):
        # with open(image_path, "rb") as image_file:
            # return base64.b64encode(image_file.read()).decode('utf-8')

    def count_tokens(self, messages: list, model: str) -> int:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        
        tokens_per_message = 3  # Базовая настройка для большинства моделей
        tokens = 0
        
        for message in messages:
            tokens += tokens_per_message
            for key, value in message.items():
                tokens += len(encoding.encode(str(value)))
                
        return tokens + 3 # Учёт завершающего токена

