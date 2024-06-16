# тут будет обработчик, который будет читать файлы и вставлять их в контекст. 
# расширения с которыми планирую работать: .txt .pdf .sh .cpp .h .c .sql .json .xml .
# планирую сделать ограничение до 1мб ~= 1.000.000.000 символов, более чем достаточно 


# # importing required modules 
# from pypdf import PdfReader 
  
# # creating a pdf reader object 
# reader = PdfReader('example.pdf') 
  
# # printing number of pages in pdf file 
# print(len(reader.pages)) 
  
# # getting a specific page from the pdf file 
# page = reader.pages[0] 
  
# # extracting text from page 
# text = page.extract_text() 
# print(text) 


# import threading


# class FileWorker(object):
#     instance = None
    
#     @classmethod
#     def new_instance(cls, *args, **kwargs):
#         if not cls.instance:
#             cls.instance = cls(*args, **kwargs)
#         return cls.instance
    
#     def __init__(self, fileFormat):
#         self._lock = threading.Lock()
        


#     def add_file(self, userId, file):
#         with self._lock:
#             try:
#                 print()
#             except (Exception) as error:
#                 print("Ошибка при получении данных:", error)
#                 # raise


# fileFormat = ['.txt' '.pdf' '.sh' '.cpp' '.h' '.c' '.sql' '.json' '.xml']


import threading
import time



class FileWorker(object):
    instance = None
    instance_lock = threading.Lock()
    
    @classmethod
    def new_instance(cls, *args, **kwargs):
        if not cls.instance:
            with cls.instance_lock:
                if not cls.instance:
                    cls.instance = cls(*args, **kwargs)
        return cls.instance

    def __init__(self, fileFormat=None):
        self._lock = threading.Lock()
        self.data = {}
        self.locks = {}
        self.timers = {}
        self.fileFormat = fileFormat
        self.start_time = time.time()
    
    def add_file(self, userId, fileName, fileText):
        if self.fileFormat and not fileName.endswith(self.fileFormat):
            print(f"File {fileName} does not match the required format {self.fileFormat}")
            return

        message = f"{fileName}: {fileText}"
        
        if userId not in self.data:
            with self._lock:
                if userId not in self.data:
                    self.data[userId] = []
                    self.locks[userId] = threading.Lock()
                    self._notify_start(userId)
        
        with self.locks[userId]:
            self.data[userId].append(message)
            if userId in self.timers:
                self.timers[userId].cancel()
        
            timer = threading.Timer(2.0, self._process_files, args=(userId,))
            self.timers[userId] = timer
            timer.start()
    
    def _notify_start(self, userId):
        print(f"Started receiving data from user {userId}")
    
    def _process_files(self, userId):
        with self.locks[userId]:
            message = "\n".join(self.data[userId])
            self._post_gpt(userId, message)
            del self.data[userId]
            del self.locks[userId]
            del self.timers[userId]
    
    def _post_gpt(self, userId, message):
        print(f"\nSending data for user \n {userId}: {message}")
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        print(f"Время выполнения функции: {execution_time} секунд")
        # global.end_time = time.time()
        # Здесь можно добавить код для отправки данных в GPT, например:
        # _gpt.post_gpt(userId, message)

# Пример использования:
# worker = FileWorker.new_instance()




# worker.add_file(1, "C:/Users/kukim/OneDrive/Рабочий\ стол/f1.txt", "Content of file 1")
# time.sleep(1)
# worker.add_file(1, "C:/Users/kukim/OneDrive/Рабочий\ стол/f.txt", "Content of file 2")
# time.sleep(1)
# worker.add_file(1, "C:/Users/kukim/OneDrive/Рабочий\ стол/f.txt", "Content of file 3")
# # Если в течении 10 секунд новых файлов не будет, данные отправятся в GPT










#  pip install blinker


from blinker import signal
from threading import Timer

# Сигнал, который будет использоваться для связи между классами
tick_signal = signal('tick')

class TimerClass:
    def __init__(self, interval):
        self.interval = interval

    def start_timer(self):
        # Метод, который будет запускать таймер и посылать сигнал
        t = Timer(self.interval, self._send_signal)
        t.start()

    def _send_signal(self):
        print("Timer expired, sending signal with arguments...")
        # Отправка сигнала с аргументами
        tick_signal.send(self, message="Hello, World!", counter=10)

class MethodClass:
    def __init__(self):
        # Подписка на сигнал
        tick_signal.connect(self.my_method)

    def my_method(self, sender, **kwargs):
        # Обработка принятых аргументов
        message = kwargs.get('message', '')
        counter = kwargs.get('counter', 0)
        print(f"MethodClass: Signal received with message='{message}' and counter={counter}")

# Пример использования:
timer = TimerClass(interval=2)  # Таймер с интервалом 2 секунды
method = MethodClass()

timer.start_timer()  # Запуск таймера