from setup import log_files, log_lines, log_days
from datetime import date, timedelta
import os

dirpath = os.path.dirname(os.path.abspath(__file__))

# SHORTEN LOG FILES
print('\n# SHORTEN LOG FILES')
for log_name in log_files:
    file_name = f'{dirpath}/reports/{log_name}'
    file_data = open(file_name)

    num_lines = sum(1 for line in file_data)
    print(f'\n{log_name}: {num_lines}')

    if num_lines > log_lines:
        file_data = open(file_name)
        lines = file_data.read().splitlines()
        data = ''

        for i in range (log_lines, 0, -1):
            last_line = lines[-i]
            data += last_line + '\n'

        open(file_name, 'w').close()
        open(file_name, "w").write(data)
        print('Reduced')
    else:
        print('ok')
    
# DELETE OLD full_reports FILES
print('\n# DELETE OLD full_reports FILES')
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


