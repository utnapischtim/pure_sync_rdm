from setup import *

def pure_get_updates(my_prompt):
    
    from functions.general_functions        import last_successful_update, rdm_get_recid, report_records_summary
    from functions.delete_record            import delete_record
    from functions.rdm_push_record          import rdm_push_record
    
    date_today = my_prompt.date.today()

    # Get date of last update
    last_update = last_successful_update(my_prompt, 'Update')

    # if last_update was not found, updates the last 3 days
    if not last_update:
        last_update = 'Not found'
        date_update = str(date_today - my_prompt.timedelta(days=3))

    # if last update was today
    elif last_update == str(date_today):
        print('Last update check happened today. Nothing to update.\n')
        return
    
    # if last_update was found, updates from the day after
    else:
        last_update_object = my_prompt.datetime.strptime(last_update, '%Y-%m-%d').date()
        date_update = last_update_object + my_prompt.timedelta(days=1)       # one day after the last update
        print(f'Updating from {date_update}')

    report = '\n---   ---   ---\n'
    report += f"\nToday: {date_today}\nLast update: {last_update} \nDate update: {date_update}\n"
    print(report)

    file_updates = f'{my_prompt.dirpath}/reports/{str(date_today)}_updates.log'
    open(file_updates, "a").write(report)

    # Records.log Report
    file_summary = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_records.log'
    open(file_summary, "a").write('\n\n- UPDATES -\n')

    report = ''
    pag = 1

    # Gets from Pure all new records
    while True:
    
        my_prompt.count_total                       = 0
        my_prompt.count_errors_push_metadata        = 0
        my_prompt.count_errors_put_file             = 0
        my_prompt.count_errors_record_delete        = 0
        my_prompt.count_successful_push_metadata    = 0
        my_prompt.count_successful_push_file        = 0
        my_prompt.count_successful_record_delete    = 0
        my_prompt.count_uuid_not_found_in_pure      = 0

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
        file_name = my_prompt.dirpath + "/data/temporary_files/resp_pure.json"
        open(file_name, 'wb').write(response.content)
        resp_json = my_prompt.json.loads(response.content)

        # to_transfer = ''
        count_all    = 0
        count_update = 0
        count_old    = 0

        for item in resp_json['items']:
            if 'info' in item:
                count_all += 1
                uuid = item['uuid']

                record_date_time = item['info']['modifiedDate']
                record_date = str(record_date_time.split('T')[0])
                
                if record_date >= date_update:
                    
                    print(f'\n{uuid} - Updated on {record_date}')
                    rdm_push_record(my_prompt, uuid)
                    count_update += 1
                    report += f'{uuid} - {record_date} - To update\n'

                else:
                    count_old += 1

        report += f'\nTot: {count_all} - To update: {count_update} - Up to date: {count_old}\n'
        open(file_updates, "a").write(report)

        if count_update == 0:
            print('There are no records to be updated\n')
            return

        # records to transfer
        # open(my_prompt.dirpath + '/data/to_transfer.txt', "a").write(to_transfer)

        pag += 1
        my_prompt.time.sleep(2)

        # if the last record is older then the date_update then stops the while loop
        if count_old > 0:
            break

    # Records.log Report
    file_summary = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_summary.log'
    open(file_summary, "a").write('\n\n')

    # ---   ---   ---   ---
    # rdm_push_by_uuid(my_prompt)
    report_records_summary(my_prompt, 'Updates')
    # ---   ---   ---   ---

