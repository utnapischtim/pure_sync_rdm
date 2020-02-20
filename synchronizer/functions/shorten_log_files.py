from setup import *

def shorten_log_files(self):
    try:
        # SHORTEN LOG FILES
        print('\n---   ---   ---\nSHORTEN LOG FILES')
        for log_name in log_files:
            file_name = f'{self.dirpath}/reports/{log_name}'
            file_data = open(file_name)

            num_lines = sum(1 for line in file_data)
            print(f'\n{log_name} -> length: {num_lines}')

            if num_lines > log_lines:
                file_data = open(file_name)
                lines = file_data.read().splitlines()
                data = ''

                for i in range (log_lines, 0, -1):
                    last_line = lines[-i]
                    data += last_line + '\n'

                open(file_name, 'w').close()
                open(file_name, "w").write(data)
                print(f'Reduced to {log_lines} lines.')
            else:
                print('ok')
            
        print('\n---   ---   ---\nDELETE OLD  FILES')
        folder = '/reports/'

        # Get file names from folder
        isfile = self.os.path.isfile
        join = self.os.path.join
        onlyfiles = [f for f in self.os.listdir(self.dirpath + folder) if isfile(join(self.dirpath + folder, f))]

        date_limit = str(self.date.today() - self.timedelta(days=log_days))

        for file_name in onlyfiles:
            date = file_name.split('_')[0]
            
            if date <= date_limit:
                self.os.remove(self.dirpath + folder + file_name)
                print(f'{file_name}\t\tDeleted')
            else:
                print(f'{file_name}\t\tOk')

    except:
        print('\n!!!    !!!     ERROR in shorten_log_files      !!!     !!!\n')

