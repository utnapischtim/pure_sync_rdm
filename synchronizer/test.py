from setup import log_days
import os
from datetime import date, timedelta

dirpath = os.path.dirname(os.path.abspath(__file__))
folder = '/reports/full_reports/'

isfile = os.path.isfile
join = os.path.join
onlyfiles = [f for f in os.listdir(dirpath + folder) if isfile(join(dirpath + folder, f))]

date_limit = str(date.today() - timedelta(days=log_days))

for file_name in onlyfiles:
    print('\n' + file_name)
    date = file_name.split('_')[0]
    
    if date <= date_limit:
        os.remove(dirpath + folder + file_name)
        print('Deleted')
    else:
        print('ok')


