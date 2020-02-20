
# Pure REST API references
pure_rest_api_url =     'https://pure01.tugraz.at/ws/api/514/'
pure_api_key =          'ca2f08c5-8b33-454a-adc4-8215cfb3e088'

pure_username = 'ws_grosso'     # credentials for pure files download
pure_password = 'U+0n0#yI'

# pure_password = load_from_file("data/pure_password.txt")
# base_url = load_from_file("data/base_url.txt") # http://localhost:5000/

# Invenio RDM
token_rdm       = '46EChpZ50XI66quYG3ZAIF3OR9rUoCSsfGviDOwOyF1jXBDwvg8SerBYF7Ju'
push_dist_sec   = 1.6
wait_429        = 900

# -   -   -
# LOG FILES
log_files = [                   # d_ files
    'd_daily_updates.log', 
    'd_rdm_push_report.log', 
    ]
log_lines   = 120                   # number of lines in d_ log files
log_days    = 2                     # days to keep /full_reports files

# Percentage of updated items to considere the upload task successful
upload_percent_accept = 90

