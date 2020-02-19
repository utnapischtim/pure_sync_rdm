from setup import *
from functions.get_from_rdm import get_from_rdm

def pure_get_updates(self):
    try:
        # empty to_delete.log
        open(self.dirpath + '/reports/to_delete.log', 'w').close()

        # empty to_transfer.log
        open(self.dirpath + '/reports/to_transfer.log', 'w').close()

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

        # date_limit = str(date_object + self.timedelta(days=1))       # one day after the last update
        date_limit = str(date_object)

        report = '\n---\n---   ---\n---   ---   ---'
        report += f"\nToday: {date_today}\nLast update: {date_last_update} \nDate limit: {date_limit}\n"
        print(report)
        print(f"See file '/records/full_reports/{date_today}_pure_updates.log'\n")

        # Get all RDM uuids and recids
        get_from_rdm(self)                                  # MIGHT TAKE TOO LONG !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        file_name = self.dirpath + '/reports/full_comparison/rdm_uuids_recids.log'
        uuidRecid_rdm = open(file_name, 'r').readlines()
        to_delete = ''
        cnt_toDel = 0

        # Gets from Pure all new records
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
                ('pageSize',    500),                  # records per page
                ('apiKey',     'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
            )
            # PURE get request
            response = self.requests.get('https://pure01.tugraz.at/ws/api/514/research-outputs', headers=headers, params=params)
            print('Pure resp: ', response)
            open(self.dirpath + "/reports/resp_pure.json", 'wb').write(response.content)
            resp_json = self.json.loads(response.content)

            to_transfer = ''
            cnt  = 0
            cntu = 0

            for item in resp_json['items']:
                if 'info' in item:
                    cnt += 1
                    pure_uuid = item['uuid']

                    record_date_time = item['info']['modifiedDate']
                    record_date = str(record_date_time.split('T')[0])
                    
                    if record_date >= date_limit:
                        to_transfer += pure_uuid + '\n'
                        cntu += 1
                        report += pure_uuid + ' - ' + record_date + ' - To update'

                        # Check if older version of the same uuid is in RDM
                        for rdm_record in uuidRecid_rdm:
                            rdm_uuid = rdm_record.split(' ')[0]
                            if pure_uuid == rdm_uuid:
                                rdm_recid = rdm_record.split(' ')[1]
                                to_delete += rdm_recid
                                cnt_toDel += 1
                                report += ' (and delete old version)\n'
                            else:
                                report += '\n'
                    else:
                        report += pure_uuid + ' - ' + record_date + ' - Ok\n'

            line = f'Tot: {cnt} - To update: {cntu}\n'
            print(line)
            report += line

            open(self.dirpath + '/reports/full_reports/' + str(date_today) + '_pure_updates.log', "a").write(report)

            if cntu == 0:
                print('There are no records to be updated\n')
                return

            # records to transfer
            open(self.dirpath + '/reports/to_transfer.log', "a").write(to_transfer)

            pag += 1
            self.time.sleep(3)

            # if the last record is older then the date_limit then stops the while loop
            if record_date < date_limit:
                break
                
        # records to delete
        if cnt_toDel > 0:
            print(f'Old records to be deleted: {cnt_toDel}\n')
            open(self.dirpath + '/reports/to_delete.log', "a").write(to_delete)

        # PUSH TO RDM
        from functions.rdm_push_byUuid import rdm_push_byUuid
        rdm_push_byUuid(self, 'update')

        # DELETE IN RDM
        from functions.delete_record    import delete_record
        delete_record(self)

    except:
        print('\n   !!!   !!!   Error in get_pure_updates function   !!!   !!!   \n')