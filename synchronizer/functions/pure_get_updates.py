from setup import *

def get_pure_updates(self):
    try:
        # Get date of last update
        file_name = self.dirpath + "/reports/d_daily_updates.log"

        date_today = self.date.today()

        # Finds last date when the update successfully happened
        with open(file_name, 'r') as f:
            lines = f.read().splitlines()
            for line in reversed(lines):
                if 'Update - ' in line:
                    line =              line.split('Update - ')[1]
                    line =              line.split(' - ')
                    date_last_update =  line[0]
                    result =            line[1]
                    if result !=        'success':  continue
                    else:                           break
                else:
                    # if 'Update - ' is not found then it starts updating from 3 days before
                    date_last_update = str(date_today - self.timedelta(days = 3))

        
        date_object = self.datetime.strptime(date_last_update, '%Y-%m-%d').date()

        # date_limit = str(date_object + timedelta(days=1))         # one day after the last update
        date_limit = str(date_object)

        report = '\n---\n---   ---\n---   ---   ---'
        report += f"\nToday: {date_today}\nLast update: {date_last_update} \nDate limit: {date_limit}\n"
        print(report)
        print(f"See file '/records/full_reports/{date_today}_pure_updates.log'\n")

        pag = 1
        while True:
            report += f'- Pag: {pag} -\n'
            print(f'Pag: {pag}')
            headers = {
                'Accept': 'application/json',
            }
            params = (
                ('order',      'modified'),
                ('orderBy',    'descending'),
                ('page',        pag),                  # page
                ('pageSize',    250),                  # records per page
                ('apiKey',     'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
            )
            # PURE get request
            response = self.requests.get('https://pure01.tugraz.at/ws/api/514/research-outputs', headers=headers, params=params)
            print('Pure resp: ', response)
            open(self.dirpath + "/reports/resp_pure.json", 'wb').write(response.content)
            resp_json = self.json.loads(response.content)

            # resp_json = open(dirpath + '/reports/resp_pure.json', 'r')                  # -- TEMPORARY --
            # resp_json = json.load(resp_json)                                            # -- TEMPORARY --

            to_re_trans = ''
            cnt  = 0
            cntu = 0

            for item in resp_json['items']:
                if 'info' in item:
                    cnt += 1

                    record_date_time = item['info']['modifiedDate']
                    record_date = str(record_date_time.split('T')[0])
                    
                    if record_date >= date_limit:
                        report += item['uuid'] + ' - ' + record_date + ' - To update ---\n'
                        to_re_trans += item['uuid'] + '\n'
                        cntu += 1
                    else:
                        report += item['uuid'] + ' - ' + record_date + ' - ok\n'

            line = f'Tot: {cnt} - To update: {cntu}\n'
            print(line)
            report += line

            open(self.dirpath + '/reports/full_reports/' + str(date_today) + '_pure_updates.log', "a").write(report)

            if cntu == 0:
                print('There are no records to be updated\n')
                return

            open(self.dirpath + '/reports/to_transfer.log', "a").write(to_re_trans)

            pag += 1
            self.time.sleep(3)

            # - while loop condition -
            # if the last record is older then the date_limit then it stops
            if record_date < date_limit:
                break

        # from f_uuid_transfer import uuid_transfer
        # uuid_transfer('update')

    except:
        print('\n   !!!   !!!   Error in get_pure_updates function   !!!   !!!   \n')