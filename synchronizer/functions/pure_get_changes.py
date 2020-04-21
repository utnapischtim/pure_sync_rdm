from setup                              import dirpath, pure_rest_api_url, upload_percent_accept
from functions.general_functions        import add_to_full_report, initialize_count_variables, add_spaces
from functions.rdm_general_functions    import rdm_get_metadata_verified, rdm_get_recid
from functions.delete_record            import delete_record, delete_from_list
from functions.rdm_push_by_uuid         import rdm_push_by_uuid
from functions.rdm_push_record          import rdm_push_record

from datetime                           import date, datetime, timedelta

import json

# To execute preferably between 22:30 and 23:30

#       ---     ---     ---
def pure_get_changes(shell_interface):
    """ Gets from Pure API all changes that took place of a certain date
        and modifies accordingly the RDM repository """
    
    # Get date of last update
    missing_updates = get_missing_updates(shell_interface)
    
    # missing_updates = ['2020-03-11']      # TEMPORARY !!!!!!!!!!!!!!!
    
    if missing_updates == []:
        add_to_full_report('\nNothing to update.\n')
        return

    for date_to_update in reversed(missing_updates):

        # Get from pure all chenges of a certain date
        pure_get_changes_by_date(shell_interface, date_to_update)


#       ---     ---     ---
def pure_get_changes_by_date(shell_interface, changes_date: str):

    current_time = datetime.now().strftime("%H:%M:%S")
    shell_interface.count_http_responses = {}
    
    file_records = f'{dirpath}/reports/{date.today()}_records.log'
    file_changes = f'{dirpath}/reports/{date.today()}_changes.log'

    page = 'page=1'
    size = 'pageSize=100'

    url = f'{pure_rest_api_url}changes/{changes_date}?{size}&{page}'
    response = rdm_get_metadata_verified(url)

    # ---- --- -------

    # Write data into resp_pure_changes
    file_name = f'{dirpath}/data/temporary_files/resp_pure_changes.json'
    open(file_name, 'wb').write(response.content)

    if response.status_code >= 300:
        add_to_full_report(response.content)

    # Load response json
    resp_json = json.loads(response.content)

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
    add_to_full_report(report_intro)

    #   ---     DELETE      ---
    # for item in resp_json['items']:

    #     if 'changeType' not in item or 'uuid' not in item:
    #         continue
    #     elif item['familySystemName'] != 'ResearchOutput':
    #         continue
    #     elif item['changeType'] != 'DELETE':
    #         continue

    #     count_delete += 1
    #     uuid = item['uuid']

    #     report = f"\n{count_delete} - {item['changeType']} - {uuid}"
    #     add_to_full_report(report)

    #     duplicated_uuid.append(uuid)         

    #     # Gets the record recid
    #     recid = rdm_get_recid(shell_interface, uuid)

    #     if recid != False:
    #         delete_record(shell_interface, recid)
    #     else:
    #         shell_interface.count_successful_record_delete += 1   # the record is not in RDM

    #   ---     DELETE      ---
    response = process_delete_changes(shell_interface, resp_json, count_delete, duplicated_uuid)
    count_delete    = response[0]
    duplicated_uuid = response[1]


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

        report = f"\n{count} - {item['changeType']} - {uuid}"
        add_to_full_report(report)

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
        open(file_changes, "a").write(f'{report_intro}Nothing to transfer.\n\n')
        return

    # Calculates if the process was successful
    percent_success = shell_interface.count_successful_push_metadata * 100 / shell_interface.count_total
    data         = f'{changes_date}\n'
    
    # If the percentage of successfully transmitted records is higher then the limit specified in setup.py
    # And changes_date is not in successful_changes.txt
    if (percent_success >= upload_percent_accept and data not in open(file_name, 'r').read()):
        
        file_success = f'{dirpath}/data/successful_changes.txt'
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
    add_to_full_report(report)

    # RECORDS.LOG
    open(file_records, "a").write(report)
    
    # CHANGES.LOG
    open(file_changes, "a").write(report_intro + report)
    return


#       ---     ---     ---
def process_delete_changes(shell_interface: object, resp_json: dict, count_delete: int, duplicated_uuid: list):

    for item in resp_json['items']:

        if 'changeType' not in item or 'uuid' not in item:
            continue
        elif item['familySystemName'] != 'ResearchOutput':
            continue
        elif item['changeType'] != 'DELETE':
            continue

        count_delete += 1
        uuid = item['uuid']

        report = f"\n{count_delete} - {item['changeType']} - {uuid}"
        add_to_full_report(report)

        duplicated_uuid.append(uuid)         

        # Gets the record recid
        recid = rdm_get_recid(shell_interface, uuid)

        if recid != False:
            delete_record(shell_interface, recid)
        else:
            shell_interface.count_successful_record_delete += 1   # the record is not in RDM

    return [count_delete, duplicated_uuid]


#       ---     ---     ---
def get_missing_updates(shell_interface):
    """ Search for missing updates in the last 7 days """

    file_name = f'{dirpath}/data/successful_changes.txt'

    missing_updates = []
    count = 0
    days_span = 7

    date_today = str(datetime.today().strftime('%Y-%m-%d'))
    date_check = datetime.strptime(date_today, "%Y-%m-%d").date()

    while count < days_span:

        if str(date_check) not in open(file_name, 'r').read():
            missing_updates.append(str(date_check))        

        date_check = date_check - timedelta(days=1)
        count += 1

    return missing_updates