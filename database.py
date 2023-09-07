import psycopg2

class Database:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.isWork = False
        
    def connect(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            isWork = True
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            isWork = False
            print('Error while connecting to the database:', error)
            return False
            
    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print('Error executing query:', error)
            return False
    
    def fetch_all(self):
        return self.cursor.fetchall()
    
    def commit(self):
        self.connection.commit()
    
    def close(self):
        self.cursor.close()
        self.connection.close()

    def status(self):
        return self.isWork

    def __del__(self):
        if self.isWork == False:
            self.close()


