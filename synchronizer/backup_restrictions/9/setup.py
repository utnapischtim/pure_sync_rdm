import os
dirpath = os.path.dirname(os.path.abspath(__file__))

db_host     = open(f'{dirpath}/setup_data/db_host.txt', 'r').readline()
db_name     = open(f'{dirpath}/setup_data/db_name.txt', 'r').readline()
db_user     = open(f'{dirpath}/setup_data/db_user.txt', 'r').readline()
db_password = open(f'{dirpath}/setup_data/db_password.txt', 'r').readline()

ip_ranges = [['127.0.0.3', '127.0.0.99'], ['127.0.1.3', '127.0.1.5']]
single_ips = ['127.0.0.3', '127.0.0.8']