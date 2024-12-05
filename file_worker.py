# тут будет обработчик, который будет читать файлы и вставлять их в контекст. 
# расширения с которыми планирую работать: .txt .pdf .sh .cpp .h .c .sql .json .xml .
# планирую сделать ограничение до 1мб ~= 1.000.000.000 символов, более чем достаточно 

import os
import fitz
import chardet
import threading
from blinker import signal
# fileFormat = ['.txt' '.pdf' '.sh' '.cpp' '.h' '.c' '.sql' '.json' '.xml']


post_signal = signal('post_media')

class MediaWorker(object):
    instance = None
    instance_lock = threading.Lock()

    @classmethod
    def new_instance(cls, *args, **kwargs):
        if not cls.instance:
            with cls.instance_lock:
                if not cls.instance:
                    cls.instance = cls(*args, **kwargs)
                    cls.instance._initialize()
        return cls.instance

    def _initialize(self):
        self._lock = threading.Lock()
        self.data = {}
        self.locks = {}
        self.timers = {}

    def add_data(self, userMedia):
        userId = userMedia._userId

        if userId not in self.data:
            with self._lock:
                if userId not in self.data:
                    self.data[userId] = []
                    self.locks[userId] = threading.Lock()

        with self.locks[userId]:
            self.data[userId].append(userMedia)
            if userId in self.timers:
                self.timers[userId].cancel()

            timer = threading.Timer(2.0, self._process_files, args=(userId,))
            self.timers[userId] = timer
            timer.start()

    def _process_files(self, userId):
        with self.locks[userId]:
            self._post_media(userId, self.data[userId])
            del self.data[userId]
            del self.locks[userId]
            del self.timers[userId]

    def _post_media(self, userId, userMediaList):
        post_signal.send('MediaWorker', userId=userId, mediaList=userMediaList)

    def find_userId(self, user_id: int) -> bool:
        return user_id in self.data





class FileConverter:
    def __init__(self, file_formats=None):
        if file_formats is None:
            file_formats = ['.txt', '.pdf', '.sh', '.cpp', '.h', '.c', '.sql', '.json', '.xml', ".*"]
        self.file_formats = file_formats

    def detect_encoding(self, file_path):
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            return result['encoding']

    def read_file(self, file_path, orig_extension):
        if orig_extension not in self.file_formats:
            raise ValueError(f"Unsupported file format: {orig_extension}")
        
        if orig_extension == '.pdf':
            return self.read_pdf(file_path)
        else:
            encoding = self.detect_encoding(file_path)
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except Exception as e:
                raise ValueError(f"Error reading file {file_path}: {str(e)}")

    def read_pdf(self, file_path):
        try:
            document = fitz.open(file_path)
            text = ''
            for page_num in range(document.page_count):
                page = document.load_page(page_num)
                text += page.get_text()
            return text
        except Exception as e:
            raise ValueError(f"Error reading PDF file {file_path}: {str(e)}")

    def convert_files_to_text(self, file_path, original_name):
        output = ''
        try:
            orig_extension = os.path.splitext(original_name)[1]
            file_text = self.read_file(file_path, orig_extension)
            output += f'```{original_name}\n {file_text}\n```\n'
        except Exception as e:
            output += f'Error processing {file_path}: {str(e)}\n\n'
        return output

