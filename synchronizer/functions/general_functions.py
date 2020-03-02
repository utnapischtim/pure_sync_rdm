from setup import *
from functions.delete_record import delete_from_list, delete_record


def rdm_get_recid(my_prompt, uuid):

    my_prompt.time.sleep(1)
    
    if len(uuid) != 36:
        print(f'\nERROR - The uuid must have 36 characters. Given: {uuid}\n')
        return False

    # GET request RDM
    params = (('prettyprint', '1'),)
    sort  = 'sort=mostrecent'
    size  = 'size=100'
    page  = 'page=1'
    query = f'q="{uuid}"'
    url = f'{rdm_api_url_records}api/records/?{sort}&{size}&{page}&{query}'
    response = my_prompt.requests.get(url, params=params, verify=False)

    if response.status_code >= 300:
        print(f'\n{uuid} - {response}')
        print(response.content)
        return False

    open(f'{my_prompt.dirpath}/data/temporary_files/rdm_get_recid.txt', "wb").write(response.content)

    # Load response
    resp_json = my_prompt.json.loads(response.content)

    total_recids = resp_json['hits']['total']
    if total_recids == 0:
        print(f'\tRecid not found in RDM')
        return False

    print(f'\tRDM get recid\t->\t{response} - total_recids: {total_recids}')

    # Iterate over all records with the same uuid
    # The first record is the most recent (they are sorted)
    count = 0
    for i in resp_json['hits']['hits']:
        count += 1
        recid = i['metadata']['recid']
        
        if count == 1:
            newest_recid = recid
        else:
            # Duplicate records are deleted
            delete_record(my_prompt, recid)

    my_prompt.recid = newest_recid
    return newest_recid



def report_records_summary(my_prompt, process_type):
    
    current_datetime = my_prompt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if my_prompt.count_total == 0:
        report =  f'{process_type} - success\n'
        report += f"{current_datetime}\n"
        report += "Nothing to transmit\n"
    else:
        percent_success = my_prompt.count_successful_push_metadata * 100 / my_prompt.count_total

        if percent_success >= upload_percent_accept:
            report = f"\n{process_type} - success\n"

            # ALL_CHANGES.LOG
            if hasattr(my_prompt, 'changes_date'):
                file_records     = f'{my_prompt.dirpath}/data/all_changes.txt'
                file_records_str = f'{my_prompt.changes_date} - success\n'
                open(file_records, "a").write(file_records_str)
        else:
            report = f"\n{process_type} - error\n"

        metadata_succs  = my_prompt.count_successful_push_metadata
        metadata_error  = my_prompt.count_errors_push_metadata
        file_succs      = my_prompt.count_successful_push_file
        file_error      = my_prompt.count_errors_put_file

        report += f"{current_datetime}\n"
        report += f"Metadata       ->  successful: {give_spaces(metadata_succs)} - "        # Metadata
        report += f"errors: {metadata_error}\n"
        report += f"File           ->  successful: {give_spaces(file_succs)} - "            # File
        report += f"errors: {file_error}"
        
        if process_type != 'Pages':
            delete_succs = my_prompt.count_successful_record_delete
            delete_error = my_prompt.count_errors_record_delete
            report += f"\nDelete         ->  successful: {give_spaces(delete_succs)} - "    # Delete
            report += f"errors: {delete_error}"

    print(report)

    # RECORDS.LOG
    file_records = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_records.log'
    open(file_records, "a").write(report)

    # SUMMARY.LOG
    file_summary = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_summary.log'
    open(file_summary, "a").write(report)



def last_successful_update(my_prompt, process_type):
    """ Search for the date of the last successful update """

    directory_path = f'{my_prompt.dirpath}/reports/'

    # Gets the list of all the files in the folder /reports/
    isfile = my_prompt.os.path.isfile
    join = my_prompt.os.path.join

    reports_files = [f for f in my_prompt.os.listdir(directory_path) if isfile(join(directory_path, f))]
    reports_files = sorted(reports_files, reverse=True)

    # Iterates over all the files in /reports folder
    for file_name in reports_files:

        file_split = file_name.split('_')

        if file_split[1] != 'summary.log':
            continue

        # It will check first the newest files
        # If no successful update is found then will check older files
        file_name = f'{my_prompt.dirpath}/reports/{file_name}'
        file_data = open(file_name, 'r').read().splitlines()
        
        for line in reversed(file_data):
            if f'{process_type} - success' in line:
                print(f'\nSuccessful Check update found in {file_name}\n')
                last_update = file_split[0]
                return last_update
    
    print(f'\nNo successful {process_type} found among all report logs\n')
    return False


def give_spaces(var):
    """ Add spaces to variables that will be used in log files """
    if   var < 10:     spaces = f'    {var}'
    elif var < 100:    spaces = f'   {var}'
    elif var < 1000:   spaces = f'  {var}'
    elif var < 10000:  spaces = f' {var}'
    else:              spaces = f'{var}'
    return spaces


def initialize_count_variables(my_prompt):
    """ Initialize variables that will be used in report_records_summary method """
    my_prompt.count_total                       = 0
    my_prompt.count_errors_push_metadata        = 0
    my_prompt.count_errors_put_file             = 0
    my_prompt.count_errors_record_delete        = 0
    my_prompt.count_successful_push_metadata    = 0
    my_prompt.count_successful_push_file        = 0
    my_prompt.count_successful_record_delete    = 0
    my_prompt.count_uuid_not_found_in_pure      = 0