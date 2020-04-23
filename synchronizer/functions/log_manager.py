from setup import dirpath, days_to_keep_log_files, lines_successful_changes
from functions.general_functions    import add_to_full_report
from datetime                       import date, datetime, timedelta
import os

def delete_old_log_files():
    
    current_time = datetime.now().strftime("%H:%M:%S")
    add_to_full_report(f'\n - Delete old log files - {current_time}\n')

    # DELETE OLD LOG FILES
    folder = '/reports/'

    # Get file names from folder
    isfile = os.path.isfile
    join = os.path.join
    onlyfiles = [f for f in os.listdir(dirpath + folder) if isfile(join(dirpath + folder, f))]

    date_limit = str(date.today() - timedelta(days=days_to_keep_log_files))

    for file_name in onlyfiles:
        file_date = file_name.split('_')[0]

        tabs = '\t'
        if len(file_name) < 25:
            tabs += '\t'

        if file_date <= date_limit:
            os.remove(dirpath + folder + file_name)
            add_to_full_report(f'{file_name}{tabs}Deleted')
        else:
            add_to_full_report(f'{file_name}{tabs}Ok')

    # SHORTEN SUCCESSFUL_CHANGES.TXT
    file_name = f'{dirpath}/data/successful_changes.txt'
    file_data = open(file_name)

    num_lines = sum(1 for line in file_data)
    report = 'successful_changes.txt\t\t'

    if num_lines > lines_successful_changes:
        file_data = open(file_name)
        lines = file_data.read().splitlines()
        data = ''

        for i in range (lines_successful_changes, 0, -1):
            last_line = lines[-i]
            data += f'{last_line}\n'

        open(file_name, 'w').close()
        open(file_name, "w").write(data)

        report += f'Reduced from {num_lines} to {lines_successful_changes} lines\n'
        add_to_full_report(report)
    else:
        report += f'Ok\n'
        add_to_full_report(report)