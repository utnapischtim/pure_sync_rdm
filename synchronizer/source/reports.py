from datetime                   import date, datetime
from setup                      import log_files_name
from source.general_functions   import dirpath

date_today = str(datetime.today().strftime('%Y-%m-%d'))

class Reports:

    def add_to_report(self, file, report):

        file_name = log_files_name[file]
        open(file_name, "a").write(f'{report}\n')