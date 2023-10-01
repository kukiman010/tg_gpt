import logging
import re


# base_way = os.path.abspath(os.curdir)
# base_way += "/"
# LOGFILE = base_way + 'log.log'


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


    def read_file_from_end(self, num_lines, tag=None):
        if tag == 'critical':
            pattern = r'^(\d+-\d+-\d+\s*\d+:\d+:\d+,\d+)\s*-\s* CRITICAL \s*-\s*.*$'
        elif tag == 'error':
            pattern = r'^(\d+-\d+-\d+\s*\d+:\d+:\d+,\d+)\s*-\s* ERROR \s*-\s*.*$'
        elif tag == 'warning':
            pattern = r'^(\d+-\d+-\d+\s*\d+:\d+:\d+,\d+)\s*-\s* WARNING \s*-\s*.*$'
        elif tag == 'debug':
            pattern = r'^(\d+-\d+-\d+\s*\d+:\d+:\d+,\d+)\s*-\s* DEBUG \s*-\s*.*$'
        elif tag == 'info':
            pattern = r'^(\d+-\d+-\d+\s*\d+:\d+:\d+,\d+)\s*-\s* INFO \s*-\s*.*$'

        data = ''
        with open(self.log_file, 'r') as file:
            lines = file.readlines()
            if num_lines > len(lines):  
                num_lines = len(lines) 

            for line in reversed(lines):
                if tag != None:
                    if num_lines == 0:
                        return data
                    
                    match = re.findall(pattern, line)
                    if match:
                         data += line
                         num_lines -= 1

                else:
                    if num_lines == 0:
                        return data
                    data += line
                    num_lines -= 1

        return data

 
    def count_lines(self, chunk_size=1<<13):
        with open(self.log_file) as file:
            return sum(chunk.count('\n')
                    for chunk in iter(lambda: file.read(chunk_size), ''))


    

# _logger = LoggerSingleton('log_gpt.log')
# print( my_logger.get_last_messages(2) )
# print( my_logger.count_lines() ) 
# _logger.add_critical("test")
# _logger.add_debug("test")
# _logger.add_error("test")
# _logger.add_info("test")
# _logger.add_warning("test")



# message = "/debug 25"
# message = "/debug 5 info "
# words = message.split()

    
# if len(words) == 2:
#     second_word = words[1]
#     if second_word.isdigit():
#         text = _logger.read_file_from_end1(int(second_word))

#         print("Ваши последние {} лог(ов)\n\n{}".format(second_word, text))

# elif len(words) == 3:
#     second_word = words[1]
#     type_log = words[2]

#     if second_word.isdigit():
#         text = _logger.read_file_from_end1(int(second_word), type_log)

#         print("Ваши последние {} лог(ов) по запроссу {}\n\n{}".format(second_word, type_log, text))
# else:
#     print("Не верный синтаксис\n подробнее в /help")
