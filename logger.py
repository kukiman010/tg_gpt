import os
import logging


base_way = os.path.abspath(os.curdir)
base_way += "/"
LOGFILE = base_way + 'log.log'

# logging.basicConfig(filename=LOGFILE, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# def logger_add_debug(str):
#     logging.debug(str)

# def logger_add_info(str):
#     logging.info(str)

# def logger_add_warning(str):
#     logging.warning(str)

# def logger_add_error(str):
#     logging.error(str)

# def logger_add_critical(str):
#     logging.critical(str)


# def logger_get_last_messages(count):
#     logs = ''
#     with open(LOGFILE) as file:
#         for line in (file.readlines() [-count:]):
#             logs += line
#     return logs


# def count_lines(filename, chunk_size=1<<13):
#     with open(filename) as file:
#         return sum(chunk.count('\n')
#                    for chunk in iter(lambda: file.read(chunk_size), ''))



# class LoggerSingleton:
#     instance = None

#     def __new__(cls, *args, **kwargs):
#         if not cls.instance:
#             cls.instance = super(LoggerSingleton, cls).__new__(cls, *args, **kwargs)
#         return cls.instance

#     def shared_method(self):
#         print("This is a shared method")

    # def __init__(self, log_file, name):
        # # Создание экземпляра логгера
        # self.logger = logging.getLogger(name)
        # self.logger.setLevel(logging.DEBUG)

        # # Создание файла для хранения логов
        # file_handler = logging.FileHandler(log_file)
        # file_handler.setLevel(logging.DEBUG)

        # # Создание форматтера для логов
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # file_handler.setFormatter(formatter)

        # # Добавление обработчика файлового логгера к логгеру
        # self.logger.addHandler(file_handler)



#     def log_message(self, level, message):
#         # Логирование сообщения с указанным уровнем
#         levels = {
#             'debug': logging.DEBUG,
#             'info': logging.INFO,
#             'warning': logging.WARNING,
#             'error': logging.ERROR,
#             'critical': logging.CRITICAL
#         }
#         self.logger.log(levels[level], message)




class LoggerSingleton(object):
    instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(LoggerSingleton, cls).__new__(cls)
        return cls.instance
    
    def __init__(self, log_file):
        self.log_file = log_file
        # Создание экземпляра логгера
        self.logger = logging.getLogger(log_file)
        self.logger.setLevel(logging.DEBUG)

        # Создание файла для хранения логов
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Создание форматтера для логов
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler.setFormatter(formatter)

        # Добавление обработчика файлового логгера к логгеру
        self.logger.addHandler(file_handler)

    # def log_message(self, level, message):
    #     with open(self.log_file, 'a') as file:
    #         file.write(f'[{level.upper()}] {message}\n')

    def add_debug(self, str):
        self.logger.debug(str)

    def add_info(self, str):
        self.logger.info(str)

    def add_warning(self, str):
        self.logger.warning(str)

    def add_error(self, str):
        self.logger.error(str)

    def add_critical(self, str):
        self.logger.critical(str)


    def get_last_messages(self, count):
        logs = ''
        with open(self.log_file) as file:
            for line in (file.readlines() [-count:]):
                logs += line
        return logs


    def count_lines(self, chunk_size=1<<13):
        with open(self.log_file) as file:
            return sum(chunk.count('\n')
                    for chunk in iter(lambda: file.read(chunk_size), ''))


    

# my_logger = LoggerSingleton('log_file.log')
# my_logger.log_message('info', 'This is an informational message.')
# my_logger.log_message('warning', 'This is a warning message.')
# my_logger.logger_add_info('This is an informational message.')
# my_logger.logger_add_warning('This is a warning message.')

# print( my_logger.get_last_messages(2) )
# print( my_logger.count_lines() ) 