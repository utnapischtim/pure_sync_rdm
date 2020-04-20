from setup                   import db_host, db_name, db_user, db_password
import psycopg2

class RdmDatabase:

    # def db_connect(self):
    def __init__(self):
        connection = psycopg2.connect(f"""\
            host={db_host} \
            dbname={db_name} \
            user={db_user} \
            password={db_password} \
            """)
        self.cursor = connection.cursor()

    def db_query(self, query):
        self.cursor.execute(query)
        if self.cursor.rowcount > 0:
            return self.cursor.fetchall()
        return False