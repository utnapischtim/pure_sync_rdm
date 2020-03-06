from setup                              import *
from functions.general_functions        import add_spaces, rdm_get_recid, initialize_count_variables
from functions.delete_record            import delete_record, delete_from_list
from functions.rdm_push_by_uuid         import rdm_push_by_uuid
from functions.rdm_push_record          import rdm_push_record

# To execute preferably between 22:30 and 23:30

#       ---     ---     ---
def pure_get_changes(shell_interface):
    """ Gets from Pure API all changes that took place in a certain date
        and modifies accordingly the RDM repository """
    
    # Get date of last update
    missing_updates = get_missing_updates(shell_interface)
    
    missing_updates = ['2020-03-06']      # TEMPORARY !!!!!!!!!!!!!!!
    
    if missing_updates == []:
        print('\nNothing to update.\n')
        return

    for date_to_update in reversed(missing_updates):
        #   ---     ---
        pure_get_changes_by_date(shell_interface, date_to_update)
        #   ---     ---


#       ---     ---     ---
def pure_get_changes_by_date(shell_interface, changes_date: str):

    current_time = shell_interface.datetime.now().strftime("%H:%M:%S")
    shell_interface.count_http_responses = {}
    
    file_records = f'{shell_interface.dirpath}/reports/{shell_interface.date.today()}_records.log'
    file_changes = f'{shell_interface.dirpath}/reports/{shell_interface.date.today()}_changes.log'

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
    response = shell_interface.requests.get(url, headers=headers, params=params)
    # ---- --- -------

    # Write data into resp_pure_changes
    file_name = f'{shell_interface.dirpath}/data/temporary_files/resp_pure_changes.json'
    open(file_name, 'wb').write(response.content)

    if response.status_code >= 300:
        print(response.content)

    # Load response json
    resp_json = shell_interface.json.loads(response.content)

    initialize_count_variables(shell_interface)

    # used to check if there are doubled tasks (e.g. update uuid and delete same uuid)
    duplicated_uuid  = []
    
    count_update             = 0
    count_create             = 0
    count_delete             = 0
    count_incomplete         = 0
    count_duplicated         = 0
    count_not_ResearchOutput = 0

    report_intro = f"""

--   --   --

{current_time}
Changes date: {changes_date}
Number of items in response: {resp_json["count"]}

"""
    # append to yyyy-mm-dd_records.log
    open(file_records, "a").write(report_intro)
    print(report_intro)

    #   ---     DELETE      ---
    for item in resp_json['items']:

        if 'changeType' not in item or 'uuid' not in item:
            continue
        elif item['familySystemName'] != 'ResearchOutput':
            continue
        elif item['changeType'] != 'DELETE':
            continue

        count_delete += 1
        uuid = item['uuid']

        print(f"\n{count_delete} - {item['changeType']} - {uuid}")

        duplicated_uuid.append(uuid)         

        # Gets the record recid
        recid = rdm_get_recid(shell_interface, uuid)

        if recid != False:
            delete_record(shell_interface, recid)
        else:
            shell_interface.count_successful_record_delete += 1   # the record is not in RDM

    #   ---     CREATE / ADD / UPDATE      ---
    count = 0
    for item in resp_json['items']:
        
        if 'changeType' not in item or 'uuid' not in item:
            count_incomplete += 1
            continue
        elif item['familySystemName'] != 'ResearchOutput':
            count_not_ResearchOutput += 1
            continue
        elif item['changeType'] == 'DELETE':
            continue

        uuid = item['uuid']
        if uuid in duplicated_uuid:
            count_duplicated += 1
            continue
        
        count += 1

        print(f"\n{count} - {item['changeType']} - {uuid}")

        if item['changeType'] == 'ADD' or item['changeType'] == 'CREATE':
            count_create += 1

        if item['changeType'] == 'UPDATE':
            count_update += 1
        
        # Checks if this uuid has already been created / updated / deleted
        duplicated_uuid.append(uuid)
        
        #   ---       ---       ---
        rdm_push_record(shell_interface, uuid)
        #   ---       ---       ---

    # If there are no changes
    if shell_interface.count_total == 0:
        nothing_to_transfer(shell_interface, report_intro, file_changes)
        return

    # Calculates if the process was successful
    percent_success = shell_interface.count_successful_push_metadata * 100 / shell_interface.count_total
    if percent_success >= upload_percent_accept:
        # SUCCESSFUL_CHANGES.TXT
        file_success = f'{shell_interface.dirpath}/data/successful_changes.txt'
        data         = f'{changes_date}\n'
        open(file_success, "a").write(data)

    metadata_succs              = add_spaces(shell_interface.count_successful_push_metadata)
    metadata_error              = add_spaces(shell_interface.count_errors_push_metadata)
    file_succs                  = add_spaces(shell_interface.count_successful_push_file)
    file_error                  = add_spaces(shell_interface.count_errors_put_file)
    delete_succs                = add_spaces(shell_interface.count_successful_record_delete)
    delete_error                = add_spaces(shell_interface.count_errors_record_delete)
    count_update                = add_spaces(count_update)
    count_create                = add_spaces(count_create)
    count_delete                = add_spaces(count_delete)
    count_incomplete            = add_spaces(count_incomplete)          # Incomplete:  when the uuid or changeType are not specified
    count_duplicated            = add_spaces(count_duplicated)          # Duplicated:  e.g. when a record has been modified twice in a day
    count_not_ResearchOutput    = add_spaces(count_not_ResearchOutput)  # Irrelevant:  when familySystemName is not ResearchOutput

    report = f"""
Metadata         ->  successful: {metadata_succs} - errors:   {metadata_error}
File             ->  successful: {file_succs} - errors:   {file_error}
Delete           ->  successful: {delete_succs} - errors:   {delete_error}
Pure changes:
Update:     {count_update} - Create:     {count_create} - Delete:    {count_delete}
Incomplete: {count_incomplete} - Duplicated: {count_duplicated} - Irrelevant:{count_not_ResearchOutput}
    """
    print(report)

    # RECORDS.LOG
    open(file_records, "a").write(report)
    
    # CHANGES.LOG
    open(file_changes, "a").write(report_intro + report)
    return
    

#       ---     ---     ---
def nothing_to_transfer(shell_interface, report_intro, file_changes):

    open(file_changes, "a").write(report_intro + 'Nothing to transfer.\n\n')
    return


#       ---     ---     ---
def get_missing_updates(shell_interface):
    """ Search for missing updates in the last 7 days """

    file_name = '/home/bootcamp/src/pure_sync_rdm/synchronizer/data/successful_changes.txt'

    missing_updates = []
    count = 0
    days_span = 7

    date_today = str(shell_interface.datetime.today().strftime('%Y-%m-%d'))
    date_check = shell_interface.datetime.strptime(date_today, "%Y-%m-%d").date()

    while count < days_span:

        if str(date_check) not in open(file_name, 'r').read():
            missing_updates.append(str(date_check))        

        date_check = date_check - shell_interface.timedelta(days=1)
        count += 1

    return missing_updates