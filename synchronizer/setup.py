import os
dirpath = os.path.dirname(os.path.abspath(__file__))

# Pure REST API references
pure_rest_api_url =     'https://pure01.tugraz.at/ws/api/514/'
pure_api_key =          'ca2f08c5-8b33-454a-adc4-8215cfb3e088'

pure_username = 'ws_grosso'     # credentials for pure files download
pure_password = 'U+0n0#yI'

# Invenio RDM
token_rdm = 'rDPTu0oINctF1QSwjnDXY3g4vjSIXOxPI3GOAc6lrHf6rxZmi6igUcqncL2a'

# -   -   -
# LOG FILES
log_files = [                   # d_ files
    'd_daily_updates.log', 
    'd_rdm_push_report.log', 
    ]
log_lines = 80                  # number of lines in d_ log files
log_days = 2                    # days to keep /full_reports files

# Percentage of updated items to considere the upload task successful
upload_percent_accept = 90