import logging
import re


# base_way = os.path.abspath(os.curdir)
# base_way += "/"
# LOGFILE = base_way + 'log.log'


class LoggerSingleton(object):
    instance = None
    
    @classmethod
    def new_instance(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = cls(*args, **kwargs)
        return cls.instance
    
    def __init__(self, log_file):
        self.log_file = log_file
        self.logger = logging.getLogger(log_file)
        self.logger.setLevel(logging.DEBUG)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
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
