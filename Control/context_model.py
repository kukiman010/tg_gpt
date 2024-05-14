from typing import List
import Control.context_model

class Context_model():
    def __init__(self) -> None:
        self.user_id = 0
        self.chat_id = 0
        self.role    = ""
        self.message_id = 0
        self.message = ""
        self.isPhoto = False

    def set_data(self, userid, chatId, role, messageId, message, isPhoto):
        self.user_id = userid
        self.chat_id = chatId
        self.role    = role
        self.message_id = messageId
        self.message = message
        self.isPhoto = isPhoto

    def get_userId(self):
        return self.user_id
    def get_chatId(self):
        return self.chat_id
    def get_role(self):
        return self.role
    def get_messegeId(self):
        return self.message_id
    def get_message(self):
        return self.message
    def get_isPhoto(self):
        return self.isPhoto
    

class AnswerAssistent():
    def __init__(self) -> None:
        self.code = 0
        self.result = ""
        self.token = 0

    def set_answer(self, code:int, result:str, token:int=0):
        self.code = code
        self.result = result
        self.token = token

    def get_code(self):
        return self.code
    def get_result(self) -> str:
        return self.result
    def get_token(self):
        return self.token


# class convert_context_to_struct():
    # def convert(self, company:str, context:List[Context_model]) -> List:

def convert(company:str, context:List[Context_model], isPhoto:bool = False) -> List:
    dict = []

    if str(company).upper() == str("OpenAi").upper():
        for i in context:
            if i.get_isPhoto() == True :
                if isPhoto == False:
                    continue
                dict.append( {"role": i.get_role(),"content": [
            {"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{i.get_message()}"},},  ]} )
            else:
                dict.append( {"role": i.get_role(), "content": i.get_message()}, )

    elif str(company).upper() == str("Yandex").upper():
        for i in context:
            dict.append( {"role": i.get_role(),"text": i.get_message()} ) 

    elif str(company).upper() == str("Sber").upper():
        for i in context:
            dict.append( {"role": i.get_role(),"content": i.get_message()} )

    elif str(company).upper() == str("Meta").upper():
        for i in context:
            dict.append( {"role": i.get_role(),"content": i.get_message()} )

    return dict

# def rm_photos_in_dict(dict:List[Context_model]):
#     dict = list(filter(lambda x: not x.get_isPhoto(), dict))
#     return dict
