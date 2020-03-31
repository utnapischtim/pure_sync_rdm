import psycopg2
db_host = 'localhost'
db_name = 'invenio-app-rdm'
db_user = 'invenio-app-rdm'
db_password = 'invenio-app-rdm'

# TEMPORARY  TEMPORARY  TEMPORARY  TEMPORARY

connection = psycopg2.connect(f"""\
    host={db_host} \
    dbname={db_name} \
    user={db_user} \
    password={db_password} \
    """)
cursor = connection.cursor()
cursor.execute("SELECT ip FROM accounts_user_session_activity;")

user_ip = cursor.fetchall()[0][0]
print(user_ip)