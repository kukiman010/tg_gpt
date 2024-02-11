
class assistent_model:
    def __init__(self):
        self.company_ai = ""
        self.model_name = ""
        self.description = ""
        self.token_size = 0
        self.last_update = ""
        self.status_lvl = 0
        self.isView =  False

    def set_model(self, company, model, description, token_size, last_update, status_lvl, isView):
        self.company_ai = company
        self.model_name = model
        self.description = description
        self.token_size = token_size
        self.last_update = last_update
        self.status_lvl = status_lvl
        self.isView = isView

    def get_company_ai(self):
        return self.company_ai
    def get_model_name(self):
        return self.model_name
    def get_description(self):
        return self.description
    def get_token_size(self):
        return self.token_size
    def get_last_update(self):
        return self.last_update
    def get_status_lvl(self):
        return self.status_lvl
    def get_isView(self):
        return self.isView
    

class assistent_api:
    def __init__(self, a_model):
        self.model = a_model
        self.button_name = []
        self.text_to_button = {}

        for i in range(len(self.model)):
            self.button_name.append( "set_model_" + str(i) )
            self.text_to_button[i] = str( self.model[i].get_company_ai() + ":\n" + self.model[i].get_model_name())

    def find_button(self, key):
        if self.button_name[key] != None:
            return self.button_name[key]
        else:
            return None

    def find_text_to_button(self, key):
        if key in self.text_to_button:
            return self.text_to_button[key]
        else:
            return None
        
    def size(self):
        return len( self.model )
    
    def available_by_status(self):
        button = {}
        for i in range(len(self.model)):
            if self.model[i].get_isView():
                button[ self.find_button(i) ] = self.find_text_to_button(i)

        return button
    
    def find_assistent(self, button_key):
        asstent = {}
        asstent[ self.model[button_key].get_model_name()]  = self.model[button_key].get_company_ai()
        return asstent
    
    def isAvailable(self, button_key, user_status):
        if self.model[button_key].get_status_lvl() <= user_status :
            return True
        else:
            return False
        
    def getToken(self, model):
        for i in range(len(self.model)):
            if self.model[i].get_model_name() == model:
                return self.model[i].get_token_size()
        return 0



    # def get_all_models(self):
    #     return self.models

    # def get_model_by_name(self, model_name):
    #     for model in self.models:
    #         if model.get_model_name() == model_name:
    #             return model
    #     return None
    

    # def available_by_status(self, user_status):
    #     button = {}
    #     for i in range(len(self.model)):
    #         # if user_status == 2 and self.model[i].get_isView():
    #         if user_status == 2 :
    #             button[ self.find_button(i) ] = self.find_text_to_button(i)
    #         # elif self.model[i].get_status_lvl() <= 1 and self.model[i].get_isView():
    #         elif self.model[i].get_status_lvl() <= 1 :
    #             button[ self.find_button(i) ] = self.find_text_to_button(i)
    #     return button
        


    # def add_model(self, model):
    #     if isinstance(model, assistent_model):
    #         self.models.append(model)

    # def remove_model(self, model):
    #     if model in self.models:
    #         self.models.remove(model)
        





class languages_model:
    def __init__(self) -> None:
        self.language = ""
        self.code = ""
        self.isView = False

    def set_model(self, language, code, isView):
        self.language = language
        self.code = code
        self.isView = isView

    def get_language(self):
        return self.language
    def get_code(self):
        return self.code
    def get_isView(self):
        return self.isView
    

class languages_api:
    def __init__(self, a_model):
        self.model = a_model
        self.button_name = []
        self.text_to_button = {}

        for i in range(len(self.model)):
            self.button_name.append( "set_lang_model_" + str(i) )
            self.text_to_button[i] = str( self.model[i].get_language() )

    def find_button(self, key):
        if self.button_name[key] != None:
            return self.button_name[key]
        else:
            return None

    def find_text_to_button(self, key):
        if key in self.text_to_button:
            return self.text_to_button[key]
        else:
            return None
        
    def size(self):
        return len( self.model )
    
    def available_by_status(self):
        button = {}
        for i in range(len(self.model)):
            if self.model[i].get_isView():
                button[ self.find_button(i) ] = self.find_text_to_button(i)

        return button
    
    def find_bottom(self, button_key):
        return self.model[button_key].get_code() 
    
    # def isAvailable(self, button_key, user_status):
    #     if self.model[button_key].get_status_lvl() <= user_status :
    #         return True
    #     else:
    #         return False
        
    # def getToken(self, model):
    #     for i in range(len(self.model)):
    #         if self.model[i].get_model_name() == model:
    #             return self.model[i].get_token_size()
    #     return 0