from datetime                   import date
import os
dirpath = os.path.dirname(os.path.abspath(__file__))

# Pure REST API references
pure_rest_api_url   = open(f'{dirpath}/data_setup/pure_rest_api_url.txt', 'r').readline()
pure_api_key        = open(f'{dirpath}/data_setup/pure_api_key.txt', 'r').readline()
pure_password       = open(f'{dirpath}/data_setup/pure_password.txt', 'r').readline()
pure_username       = open(f'{dirpath}/data_setup/pure_username.txt', 'r').readline()

# RDM
rdm_host_url        = open(f'{dirpath}/data_setup/rdm_host_url.txt', 'r').readline()
token_rdm           = open(f'{dirpath}/data_setup/rdm_token.txt', 'r').readline()
rdm_records_url     = f'{rdm_host_url}api/records/'
push_dist_sec       = 0.5
wait_429            = 900   # Too many requests sent to the server (waits 15 minutes)

# LOG FILES
days_to_keep_log_files   = 2      # Deletes log files after x days (shorten_logfiles.py)
lines_successful_changes = 90     # Reduce the number of lines in successful_changes.txt

# Percentage of updated items to considere the upload task successful
upload_percent_accept = 90

# OTHER
iso6393_file_name = f'{dirpath}/data/iso6393.json'
pure_uuid_length  = 36

# EMAIL
email_receiver        = open(f'{dirpath}/data_setup/email_receiver.txt', 'r').readline()
email_sender          = open(f'{dirpath}/data_setup/email_sender.txt', 'r').readline()
email_sender_password = open(f'{dirpath}/data_setup/email_sender_password.txt', 'r').readline()
email_smtp_server     = 'smtp.gmail.com'
email_smtp_port       = 587
email_subject         = 'Pure file delete 2'
email_message         = """\
Subject: """ + email_subject + """
Please remove from pure uuid {} the file {}."""

# DATABASE
db_host     = open(f'{dirpath}/data_setup/db_host.txt', 'r').readline()
db_name     = open(f'{dirpath}/data_setup/db_name.txt', 'r').readline()
db_user     = open(f'{dirpath}/data_setup/db_user.txt', 'r').readline()
db_password = open(f'{dirpath}/data_setup/db_password.txt', 'r').readline()

# RESTRICTIONS
applied_restrictions_possible_values = ['groups', 'owners', 'ip_range', 'ip_single']

# VERSIONING
versioning_running = False

# REPORT LOGS
base_path = f'{dirpath}/reports/{date.today()}'
log_files_name = {
    'groups':               f'{base_path}_groups.log',
    'owners':               f'{base_path}_owners.log',
    'pages':                f'{base_path}_pages.log',
    'records':              f'{base_path}_records.log',
    'console':              f'{base_path}_console.log',
    'changes':              f'{base_path}_changes.log',
}

# DATA FILES NAME
base_path = f'{dirpath}/data'
data_files_name = {
    'successful_changes':   f'{base_path}/successful_changes.txt',
    'user_ids_match':       f'{base_path}/user_ids_match.txt',
    'all_rdm_records':      f'{base_path}/all_rdm_records.txt',
    'rdm_record_owners':    f'{base_path}/rdm_record_owners.txt',
    'transfer_uuid_list':   f'{base_path}/to_transmit.txt',
    'delete_recid_list':    f'{base_path}/to_delete.txt',
}

# TEMPORARY FILES (used to keep truck of the data received and transmitted)
base_path = f'{dirpath}/data/temporary_files'
temporary_files_name = {
    'base_path':            f'{base_path}',
    'get_pure_metadata':    f'{base_path}/get_pure_metadata.json',
    'get_rdm_metadata':     f'{base_path}/rdm_get_metadata.json',
    'post_rdm_metadata':    f'{base_path}/rdm_post_metadata.json',
}

