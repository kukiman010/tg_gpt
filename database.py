import psycopg2
from psycopg2 import OperationalError, pool

class Database:
    def __init__(self, database, user, password, host='localhost', port=5432, minconn=1, maxconn=100):
        self.db_config = {
            'database': database,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
        self.minconn = minconn
        self.maxconn = maxconn
        self.connection_pool = None
        self.initialize_pool()

    def initialize_pool(self):
        try:
            # Инициализация пула соединений
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                self.minconn,
                self.maxconn,
                **self.db_config
            )
            print("Connection pool created successfully")
        except (Exception, OperationalError) as e:
            print(f"Error initializing connection pool: {e}")

    def get_connection(self):
        if not self.connection_pool:
            raise Exception("Connection pool is not initialized")
        return self.connection_pool.getconn()

    def release_connection(self, connection):
        if connection:
            self.connection_pool.putconn(connection)

    def reconnect(self):
        if self.connection_pool:
            self.connection_pool.closeall()
        self.initialize_pool()

    def execute_query(self, query, params=None):
        try:
            connection = self.get_connection()
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall() if cursor.description else None
            connection.commit()
            return result
        except (Exception, OperationalError) as e:
            print(f"Error executing query: {e}")
            if isinstance(e, OperationalError):
                print("Attempting to reconnect to the database...")
                self.reconnect()
            connection.rollback()  # Откат только в случае реального исключения
            return None
        finally:
            if 'connection' in locals():
                self.release_connection(connection)

    def close_pool(self):
        if self.connection_pool:
            self.connection_pool.closeall()