from datetime                   import date, datetime
from setup                      import log_files_name
from source.general_functions   import dirpath

date_today = str(datetime.today().strftime('%Y-%m-%d'))

class Reports:

    def add_to_report(self, file, report):

        file_name = log_files_name[file]
        open(file_name, "a").write(f'{report}\n')


# log_files_name = {
#     'successful changes':   f'{dirpath}/data/successful_changes.txt',
#     'user_ids_match':       f'{dirpath}/data/user_ids_match.txt',
#     'groups':               f'{dirpath}/reports/{date.today()}_groups.log',
#     'pages':                f'{dirpath}/reports/{date.today()}_pages.log',
#     'records':              f'{dirpath}/reports/{date.today()}_records.log',
#     'records_full':         f'{dirpath}/reports/{date.today()}_records_full.log',
#     'changes':              f'{dirpath}/reports/{date.today()}_changes.log',
# }