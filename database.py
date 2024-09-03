import psycopg2
import threading

class Database:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.is_work = False
        self._lock = threading.Lock()
        self.connect()

    def connect(self):
        with self._lock:
            try:
                self.connection = psycopg2.connect(
                    dbname=self.dbname,
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    port=self.port,
                    client_encoding="utf8"
                )
                self.cursor = self.connection.cursor()
                self.is_work = True
                return True
            except (Exception, psycopg2.DatabaseError) as error:
                self.is_work = False
                print('Error while connecting to the database:', error)
                return False

    def execute_query(self, query, params=None):
        with self._lock:
            try:
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)
                return True
            except (Exception, psycopg2.DatabaseError) as error:
                print('Error executing query:', error)
                return False

    def custom_execute_query(self, query, args):
        return self.execute_query(query, args)

    def fetch_all(self):
        with self._lock:
            try:
                if self.cursor.rowcount == 0:
                    return []
                return self.cursor.fetchall()
            except (Exception, psycopg2.DatabaseError) as error:
                print("Ошибка при получении данных:", error)
                raise

    def commit(self):
        with self._lock:
            try:
                self.connection.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print("Ошибка при выполнении коммита:", error)
                self.connection.rollback()

    def close(self):
        with self._lock:
            self.cursor.close()
            self.connection.close()
            self.is_work = False

    def status(self):
        return self.is_work

    def delete(self):
        self.close()