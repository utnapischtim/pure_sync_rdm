import os
dirpath = os.path.dirname(os.path.abspath(__file__))

# Pure REST API references
pure_rest_api_url   = open(f'{dirpath}/data_setup/pure_rest_api_url.txt', 'r').readline()
pure_api_key        = open(f'{dirpath}/data_setup/pure_api_key.txt', 'r').readline()

pure_username       = 'ws_grosso'     # credentials for pure files download
pure_password       = open(f'{dirpath}/data_setup/pure_password.txt', 'r').readline()

# RDM
rdm_api_url_records = open(f'{dirpath}/data_setup/rdm_api_url_records.txt', 'r').readline()
token_rdm           = open(f'{dirpath}/data_setup/rdm_token.txt', 'r').readline()
push_dist_sec       = 3
wait_429            = 900

# LOG FILES
days_to_keep_log_files   = 2      # Deletes log files after x days (shorten_logfiles.py)
lines_successful_changes = 30     # Reduce the number of lines in successful_changes.txt

# Percentage of updated items to considere the upload task successful
upload_percent_accept = 90

# EMAIL
email_receiver        = open(f'{dirpath}/data_setup/email_receiver.txt', 'r').readline()
email_sender          = open(f'{dirpath}/data_setup/email_sender.txt', 'r').readline()
email_sender_password = open(f'{dirpath}/data_setup/email_sender_password.txt', 'r').readline()
email_subject         = 'Pure file delete 2'
email_message         = """\
Subject: """ + email_subject + """
Please remove from pure uuid {} the file {}."""