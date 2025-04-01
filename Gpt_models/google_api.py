# https://ai.google.dev/tutorials/python_quickstart

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
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '..'))

import Control.context_model
from logger import LoggerSingleton


_logger = LoggerSingleton.new_instance('log_gpt.log')


class Google:
    def __init__(self, tokenID: str) -> None:
        if not tokenID:
            raise ValueError("API token must be provided")
        
        self.TOKEN = tokenID
        try:
            self.client = OpenAI(
                api_key=self.TOKEN,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        except Exception as e:
            _logger.add_error(f"Source: {str(self.__class__.__name__)}. Client initialization failed: {str(e)}")
            raise

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

    def gpt_post_view(self, context: list, gpt_model: str, MAX_TOKENS: int) ->  Control.context_model.AnswerAssistent:
        answer = Control.context_model.AnswerAssistent()
        
        # Валидация входных параметров
        if not isinstance(context, list) or len(context) == 0:
            answer.set_answer(400, "Invalid context format", 0)
            return answer
            
        if MAX_TOKENS <= 0:
            answer.set_answer(400, "MAX_TOKENS must be positive", 0)
            return answer

        try:
            # Подсчёт токенов
            token_count = self.count_tokens(context, gpt_model)
        except Exception as e:
            _logger.add_error(f"Source: {str(self.__class__.__name__)}. Token counting failed: {str(e)}")
            answer.set_answer(500, "Token counting error", 0)
            return answer

        # Проверка лимита токенов
        if token_count > MAX_TOKENS:
            answer.set_answer(413, f"Context too long ({token_count}/{MAX_TOKENS} tokens)", token_count)
            return answer

        return self.post_gpt(gpt_model, context)

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
                
        return tokens + 3  # Учёт завершающего токена
    

