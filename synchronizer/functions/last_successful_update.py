

def last_successful_update(my_prompt, process_type):
    """ Search for the date of the last successful update """

    directory_path = f'{my_prompt.dirpath}/reports/'

    # Gets the list of all the files in the folder /reports/
    isfile = my_prompt.os.path.isfile
    join = my_prompt.os.path.join

    reports_files = [f for f in my_prompt.os.listdir(directory_path) if isfile(join(directory_path, f))]
    reports_files = sorted(reports_files, reverse=True)

    # Iterates over all the files in /reports folder
    for file_name in reports_files:

        file_split = file_name.split('_')

        if file_split[1] != 'summary.log':
            continue

        # It will check first the most up to date files
        # If no successful update is found then will check older files
        file_name = f'{my_prompt.dirpath}/reports/{file_name}'
        file_data = open(file_name, 'r').read().splitlines()
        
        for line in reversed(file_data):
            if f'{process_type} - success' in line:
                print(f'\nSuccessful Check update found in {file_name}\n')
                last_update = file_split[0]
                return last_update
    
    print(f'\nNo successful {process_type} found among all report logs\n')
    return False