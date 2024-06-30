
class UserMedia:
    # def __init__(self, userId, chatId, messageId, name):
    def __init__(self, userId, chatId, name):
        self._userId = userId
        self._chatId = chatId
        # self._messageId = messageId
        self._name = name
        
        self._fileWay = ""
        self._fileName = ""
        self._type = ""
        self._mediaData = None
        self._sizeByte = 0
        
    
    def add_mes(self, text):
        self._type = "message"
        self._mediaData = text
        self._fileWay = ""
        self._sizeByte = len(text)

    def add_photo(self, fileWay, name, fileSize = None, data = None):
        self._type = "photo"
        self._fileWay = fileWay
        self._fileName = name
        self._sizeByte = fileSize
        self._mediaData = data

    def add_document(self, fileWay, name, fileSize = None, data = None):
        self._type = "document"
        self._fileWay = fileWay
        self._fileName = name
        self._sizeByte = fileSize
        self._mediaData = data

    def add_audio(self, fileWay, name, fileSize = None, data = None):
        self._type = "audio"
        self._fileWay = fileWay
        self._fileName = name
        self._sizeByte = fileSize
        self._mediaData = data