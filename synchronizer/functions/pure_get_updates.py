from setup import *
from functions.get_from_rdm import get_from_rdm

def pure_get_updates(my_prompt):
    # try:
    date_today = my_prompt.date.today()

    # empty to_delete.log
    open(my_prompt.dirpath + '/data/to_delete.txt', 'w').close()

    # empty to_transfer.log
    open(my_prompt.dirpath + '/data/to_transfer.txt', 'w').close()

    # Get date of last update
    file_name = f'{my_prompt.dirpath}/reports/{str(date_today)}_updates.log'

    # Check if file exists
    if not my_prompt.os.path.exists(file_name):
        print(f'\nERROR:\nFile {file_name} not found\n')
        return

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
                date_last_update = str(date_today - my_prompt.timedelta(days = 3))

    
    date_object = my_prompt.datetime.strptime(date_last_update, '%Y-%m-%d').date()

    # date_limit = str(date_object + my_prompt.timedelta(days=1))       # one day after the last update
    date_limit = str(date_object)

    report = '\n---\n---   ---\n---   ---   ---'
    report += f"\nToday: {date_today}\nLast update: {date_last_update} \nDate limit: {date_limit}\n"
    print(report)
    print(f"See file '/records/{date_today}_updates_check.log'\n")

    # Get all RDM uuids and recids
    get_from_rdm(my_prompt)                                  # MIGHT TAKE TOO LONG !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    file_name = my_prompt.dirpath + '/reports/full_comparison/rdm_uuids_recids.log'
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
        url = f'{pure_rest_api_url}research-outputs'
        response = my_prompt.requests.get(url, headers=headers, params=params)
        
        print('Pure resp: ', response)
        open(my_prompt.dirpath + "/data/temporary_files/resp_pure.json", 'wb').write(response.content)
        resp_json = my_prompt.json.loads(response.content)

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

        open(f'{my_prompt.dirpath}/reports/{str(date_today)}_updates_check.log', "a").write(report)

        if cntu == 0:
            print('There are no records to be updated\n')
            return

        # records to transfer
        open(my_prompt.dirpath + '/data/to_transfer.txt', "a").write(to_transfer)

        pag += 1
        my_prompt.time.sleep(3)

        # if the last record is older then the date_limit then stops the while loop
        if record_date < date_limit:
            break
            
    # records to delete
    if cnt_toDel > 0:
        print(f'Old records to be deleted: {cnt_toDel}\n')
        open(my_prompt.dirpath + '/data/to_delete.txt', "a").write(to_delete)

    # PUSH TO RDM
    from functions.rdm_push_byUuid import rdm_push_byUuid
    rdm_push_byUuid(my_prompt, 'update')

    # DELETE IN RDM
    from functions.delete_record    import delete_record
    delete_record(my_prompt)

    # except:
    #     print('\n   !!!   !!!   Error in get_pure_updates function   !!!   !!!   \n')