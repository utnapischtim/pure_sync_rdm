from setup import *

def shorten_log_files(my_prompt):
    try:
        # DELETE OLD REPORTS
        print('\n---   ---   ---\nDELETE OLD REPORTS\n')
        folder = '/reports/'

        # Get file names from folder
        isfile = my_prompt.os.path.isfile
        join = my_prompt.os.path.join
        onlyfiles = [f for f in my_prompt.os.listdir(my_prompt.dirpath + folder) if isfile(join(my_prompt.dirpath + folder, f))]

        date_limit = str(my_prompt.date.today() - my_prompt.timedelta(days=days_to_keep_log_files))

        for file_name in onlyfiles:
            date = file_name.split('_')[0]

            tabs = '\t'
            if len(file_name) < 25:
                tabs += '\t'

            if date <= date_limit:
                my_prompt.os.remove(my_prompt.dirpath + folder + file_name)
                print(f'{file_name}{tabs}Deleted')
            else:
                print(f'{file_name}{tabs}Ok')

        print('\n')

    except:
        print('\n!!!    !!!     ERROR in shorten_log_files      !!!     !!!\n')

