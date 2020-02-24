import os
dirpath = os.path.dirname(os.path.abspath(__file__))

# Pure REST API references
pure_rest_api_url = 'https://pure01.tugraz.at/ws/api/514/'
pure_api_key =      open(f'{dirpath}/data_setup/pure_api_key.txt', 'r').readline()

pure_username = 'ws_grosso'     # credentials for pure files download
pure_password = open(f'{dirpath}/data_setup/pure_password.txt', 'r').readline()

# RDM
rdm_api_url_records = 'https://127.0.0.1:5000/'
token_rdm           = open(f'{dirpath}/data_setup/rdm_token.txt', 'r').readline()
push_dist_sec       = 1.6
wait_429            = 900

# LOG FILES
days_to_keep_log_files = 7      # Deletes log files after x days (shorten_logfiles.py)

# Percentage of updated items to considere the upload task successful
upload_percent_accept = 90

