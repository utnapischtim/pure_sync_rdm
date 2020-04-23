from datetime                   import date, datetime
from source.general_functions   import dirpath

date_today = str(datetime.today().strftime('%Y-%m-%d'))

file_names = {
    'successful changes':   '{dirpath}/data/successful_changes.txt',
    'user_ids_match':       '{dirpath}/data/user_ids_match.txt',
    'groups':               '',
    'pages':                '',
    'records':              f'{dirpath}/reports/{date.today()}_records.log',
    'records_full':         '',
    'changes':              f'{dirpath}/reports/{date.today()}_changes.log',
}