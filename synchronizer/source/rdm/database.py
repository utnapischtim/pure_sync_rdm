import psycopg2
from setup          import db_host, db_name, db_user, db_password

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

    def db_query2(self, query, args = []):

        queries = {
            'logged_in_user_id':"SELECT user_id, ip FROM accounts_user_session_activity",
            'get_group_id':     "SELECT id FROM accounts_role WHERE name = '{}';",
            'get_group_users':  "SELECT user_id FROM accounts_userrole WHERE role_id = {};"
        }

        print(queries['query'].format())
        exit()

        self.cursor.execute(queries['query'])
        if self.cursor.rowcount == 0:
            return False
        return self.cursor.fetchall()
