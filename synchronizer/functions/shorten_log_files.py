from setup import *

def shorten_log_files(shell_interface):

    # DELETE OLD REPORTS
    print()
    folder = '/reports/'

    # Get file names from folder
    isfile = shell_interface.os.path.isfile
    join = shell_interface.os.path.join
    onlyfiles = [f for f in shell_interface.os.listdir(shell_interface.dirpath + folder) if isfile(join(shell_interface.dirpath + folder, f))]

    date_limit = str(shell_interface.date.today() - shell_interface.timedelta(days=days_to_keep_log_files))

    for file_name in onlyfiles:
        date = file_name.split('_')[0]

        tabs = '\t'
        if len(file_name) < 25:
            tabs += '\t'

        if date <= date_limit:
            shell_interface.os.remove(shell_interface.dirpath + folder + file_name)
            print(f'{file_name}{tabs}Deleted')
        else:
            print(f'{file_name}{tabs}Ok')
    print()

    # SHORTEN SUCCESSFUL_CHANGES.TXT
    file_name = f'{shell_interface.dirpath}/data/successful_changes.txt'
    file_data = open(file_name)

    num_lines = sum(1 for line in file_data)

    if num_lines > lines_successful_changes:
        file_data = open(file_name)
        lines = file_data.read().splitlines()
        data = ''

        for i in range (lines_successful_changes, 0, -1):
            last_line = lines[-i]
            data += f'{last_line}\n'

        open(file_name, 'w').close()
        open(file_name, "w").write(data)

        print(f'successful_changes.txt\t\tReduced from {num_lines} to {lines_successful_changes} lines')
    else:
        print(f'successful_changes.txt\t\tOk')

    print('\n')