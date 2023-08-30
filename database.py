import psycopg2

class DB:
    def __init__(self):
        self.host = 1
        self.port = 2
        self.dbname = 3
        self.user = 4 
        self.password = 5


    # def set_settings(self, host, port, dbname, user, password):
    #     self.host = host
    #     self.port = port
    #     self.dbname = dbname
    #     self.user = user
    #     self.password = password

    # def connect(self):
    #     self.conn = psycopg2.connect(
    #     host = self.host,
    #     port = self.port,
    #     database = self.dbname,
    #     user = self.user,
    #     password = self.password,
    #     )
