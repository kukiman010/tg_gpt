import openai
import json
import tiktoken

from logger         import LoggerSingleton


_logger = LoggerSingleton.new_instance('log_gpt.log')

class chatgpt():
    def __init__(self, tokenID, folderID) -> None:
        self.TOKEN_GPT = tokenID
        self.TOKEN_FOLDER_ID = folderID
        openai.api_key = tokenID

    
    def gpt_post_view(self, context, MAX_TOLENS):
        completion = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=context,
        max_tokens=MAX_TOLENS,
        )

        answer = str( completion.choices[0].message )
        data = json.loads(answer)
        return data['content']


    def post_gpt(self, context, gpt_model):
        completion = openai.ChatCompletion.create(
            model=gpt_model,
            messages=context
            )
        answer = str( completion.choices[0].message )
        data = json.loads(answer)
        content = data['content']

        return content
    

    def count_tokens(self, text):
        tokenizer = tiktoken.Tokenizer()
        tokens = tokenizer.tokenize(text)
        return len(tokens)

    # def encode_image(self, image_path):
        # with open(image_path, "rb") as image_file:
            # return base64.b64encode(image_file.read()).decode('utf-8')