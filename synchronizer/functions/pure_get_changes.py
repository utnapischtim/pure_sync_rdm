from setup                          import *
from functions.general_functions    import last_successful_update

# To execute preferibly between 22:30 and 23:30

def pure_get_changes(my_prompt):
    """ Gets from Pure API all changes that took place in a certain date
        and modifies accordingly the RDM repository """
    
    date_today = str(my_prompt.datetime.today().strftime('%Y-%m-%d'))
    
    # Get date of last update
    last_update = last_successful_update(my_prompt, 'Changes')

    last_update = '2020-02-27'      # TEMPORARY !!!!!!!!!!!!!!!
    
    if last_update == date_today:
        print('Last changes check happened today. Nothing to update.\n')
        return

    # Converts last_update string to object
    last_update = my_prompt.datetime.strptime(str(last_update), "%Y-%m-%d").date()

    while str(last_update) < date_today:
        # Adds one day to to_update, 
        last_update = last_update + my_prompt.timedelta(days=1)
        #   ---     ---
        pure_get_changes_by_date(my_prompt, last_update)
        #   ---     ---


def pure_get_changes_by_date(my_prompt, changes_date):
    # try:
    from functions.general_functions        import rdm_get_recid
    from functions.delete_record            import delete_record, delete_from_list
    from functions.rdm_push_by_uuid         import rdm_push_by_uuid
    from functions.general_functions        import report_records_summary

    headers = {
        'Accept': 'application/json',
    }
    params = (
        ('page', '1'),
        ('pageSize', '5000'),
        ('apiKey', 'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
    )
    # PURE get request
    url = f'{pure_rest_api_url}changes/{changes_date}'
    response = my_prompt.requests.get(url, headers=headers, params=params)
    # ---- --- -------

    if response.status_code >= 300:
        print(response.content)

    # Write data into resp_pure_changes
    file_name = f'{my_prompt.dirpath}/data/temporary_files/resp_pure_changes.json'
    open(file_name, 'wb').write(response.content)

    # Load response json
    resp_json = my_prompt.json.loads(response.content)

    my_prompt.count_total                       = 0
    my_prompt.count_errors_push_metadata        = 0
    my_prompt.count_errors_put_file             = 0
    my_prompt.count_errors_record_delete        = 0
    my_prompt.count_successful_push_metadata    = 0
    my_prompt.count_successful_push_file        = 0
    my_prompt.count_successful_record_delete    = 0
    my_prompt.count_uuid_not_found_in_pure      = 0

    # used to check if there are doubled tasks (e.g. update uuid and delete same uuid)
    to_delete_uuid  = []
    
    count_update             = 0
    count_create             = 0
    count_delete             = 0
    count_incomplete_info    = 0
    count_duplicated         = 0
    count_not_ResearchOutput = 0

    report_records  = '\n\n--   --   --\n'
    report_records +=  f'\n- Changes date: {changes_date} -\n'
    report_records += f'Pure get CHANGES: {response}\n'
    report_records += f'Number of items in response: {resp_json["count"]}\n'
    print(report_records)

    # append to yyyy-mm-dd_records.log
    file_records = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_records.log'
    open(file_records, "a").write(report_records)


    #   ---     DELETE      ---
    for item in resp_json['items']:

        if 'changeType' not in item:
            count_incomplete_info += 1
            continue
        
        elif item['familySystemName'] != 'ResearchOutput':
            count_not_ResearchOutput += 1
            continue

        elif item['changeType'] != 'DELETE':
            continue

        count_delete += 1
        uuid = item['uuid']
        print(f"\n{count_delete} - {item['changeType']} - {uuid}")

        to_delete_uuid.append(uuid)         

        # Gets the record recid
        recid = rdm_get_recid(my_prompt, uuid)

        if recid != False:
            delete_record(my_prompt, recid)

        else:
            my_prompt.count_successful_record_delete += 1   # the record is not in RDM



    #   ---     CREATE / ADD / UPDATE      ---
    to_transfer = []
    count = 0
    for item in resp_json['items']:
        
        uuid = item['uuid']

        if 'changeType' not in item:
            continue
        elif item['familySystemName'] != 'ResearchOutput':
            continue
        elif item['changeType'] == 'DELETE':
            continue
        elif uuid in to_delete_uuid or uuid in to_transfer:
            count_duplicated += 1
            continue

        count += 1
        print(f"\n{count} - {item['changeType']} - {uuid}")

        if item['changeType'] == 'ADD' or item['changeType'] == 'CREATE':
            count_create += 1

        if item['changeType'] == 'UPDATE':
    
            count_update += 1

        to_transfer.append(uuid)
        
        # Gets the record recid for deletion
        recid = rdm_get_recid(my_prompt, uuid)

        # Deletes the record so that the new version is added
        if recid != False:
            delete_record(my_prompt, recid)

    # - TRANSFER -
    # If there is nothing to transmit
    if len(to_transfer) > 0:
        file_name = my_prompt.dirpath + '/data/to_transfer.txt'
        to_transfer_str = ''
        for i in to_transfer:
            to_transfer_str += f'{i}\n'
        open(file_name, 'w').close()                    # empty file
        open(file_name, "a").write(to_transfer_str)     # append to file

        rdm_push_by_uuid(my_prompt)                     # --------------

    file_summary = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_summary.log'
    open(file_summary, "a").write('\n\n')

    #    ---     ---
    report_records_summary(my_prompt, 'Changes')
    #    ---     ---

    report = '\nPure changes:\n'
    report += f'Update:     {count_update} - '
    report += f'Create:     {count_create} - '
    report += f'Delete:     {count_delete}\n'
    report += f'Incomplete: {count_incomplete_info} - '     # e.g. when the uuid is not specified
    report += f'Duplicated: {count_duplicated} - '          # for istance when a record has been modified twice in a day
    report += f'Irrelevant: {count_not_ResearchOutput}'   # when familySystemName is not ResearchOutput

    open(file_summary, "a").write(report)

    file_records = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_records.log'
    open(file_records, "a").write(report)

    print(report)