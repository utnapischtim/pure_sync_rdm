import os
dirpath = os.path.dirname(os.path.abspath(__file__))

# Pure REST API references
pure_rest_api_url = 'https://pure01.tugraz.at/ws/api/514/'
pure_api_key =      open(f'{dirpath}/data_setup/pure_api_key.txt', 'r').readline()

pure_username = 'ws_grosso'     # credentials for pure files download
pure_password = open(f'{dirpath}/data_setup/pure_password.txt', 'r').readline()

# Invenio RDM
token_rdm       = open(f'{dirpath}/data_setup/rdm_token.txt', 'r').readline()
push_dist_sec   = 1.6
wait_429        = 900

# LOG FILES
log_files = [                   # d_ files
    'd_daily_updates.log', 
    'd_rdm_push_report.log', 
    ]
log_lines   = 120                   # number of lines in d_ log files
log_days    = 2                     # days to keep /full_reports files

# Percentage of updated items to considere the upload task successful
upload_percent_accept = 90

