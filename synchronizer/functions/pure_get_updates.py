from setup import *
from functions.last_successful_update import last_successful_update

def pure_get_updates(my_prompt):

    # try:
    date_today = my_prompt.date.today()

    # empty to_delete.log
    open(my_prompt.dirpath + '/data/to_delete.txt', 'w').close()

    # empty to_transfer.log
    open(my_prompt.dirpath + '/data/to_transfer.txt', 'w').close()

    # Get date of last update
    last_update = last_successful_update(my_prompt, 'Update')

    # if last_update was not found, updates the last 3 days
    if not last_update:
        date_update = str(date_today - my_prompt.timedelta(days=3))

    # if last update was today
    elif last_update == str(date_today):
        print('Last update check happened today. Nothing to update.\n')
        return
    
    # if last_update was found, updates from the day after
    else:
        last_update_object = my_prompt.datetime.strptime(last_update, '%Y-%m-%d').date()
        date_update = str(last_update_object + my_prompt.timedelta(days=1))       # one day after the last update
        print(f'Updating from {date_update}')
        

    report = '\n---\n---   ---\n---   ---   ---'
    report += f"\nToday: {date_today}\nLast update: {last_update} \nDate update: {date_update}\n"
    print(report)
    print(f"See file '/records/{date_today}_updates_check.log'\n")

    exit()

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
                
                if record_date >= date_update:
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

        # if the last record is older then the date_update then stops the while loop
        if record_date < date_update:
            break
            
    # records to delete
    if cnt_toDel > 0:
        print(f'Old records to be deleted: {cnt_toDel}\n')
        open(my_prompt.dirpath + '/data/to_delete.txt', "a").write(to_delete)

    # PUSH TO RDM
    from functions.rdm_push_by_uuid import rdm_push_by_uuid
    rdm_push_by_uuid(my_prompt, 'update')

    # DELETE IN RDM
    from functions.delete_record    import delete_record
    delete_record(my_prompt)

    # except:
    #     print('\n   !!!   !!!   Error in get_pure_updates function   !!!   !!!   \n')



