from setup import *
from functions.delete_record import delete_from_list, delete_record


def rdm_get_recid(shell_interface, uuid):

    shell_interface.time.sleep(1)
    
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
    response = shell_interface.requests.get(url, params=params, verify=False)

    if response.status_code >= 300:
        print(f'\n{uuid} - {response}')
        print(response.content)
        return False

    open(f'{shell_interface.dirpath}/data/temporary_files/rdm_get_recid.txt', "wb").write(response.content)

    # Load response
    resp_json = shell_interface.json.loads(response.content)

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
            delete_record(shell_interface, recid)

    shell_interface.recid = newest_recid
    return newest_recid



def report_records_summary(shell_interface, process_type: str):
    
    current_datetime = shell_interface.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if shell_interface.count_total == 0:
        report =  f'{process_type} - success\n'
        report += f"{current_datetime}\n"
        report += "Nothing to transmit\n"
    else:
        percent_success = shell_interface.count_successful_push_metadata * 100 / shell_interface.count_total

        if percent_success >= upload_percent_accept:
            report = f"\n{process_type} - success\n"

            # SUCCESSFUL_UPDATES.TXT
            if hasattr(shell_interface, 'changes_date'):
                file_records     = f'{shell_interface.dirpath}/data/successful_updates.txt'
                file_records_str = f'{shell_interface.changes_date}\n'
                open(file_records, "a").write(file_records_str)
        else:
            report = f"\n{process_type} - error\n"

        metadata_succs  = shell_interface.count_successful_push_metadata
        metadata_error  = shell_interface.count_errors_push_metadata
        file_succs      = shell_interface.count_successful_push_file
        file_error      = shell_interface.count_errors_put_file

        report += f"{current_datetime}\n"
        report += f"Metadata       ->  successful: {add_spaces(metadata_succs)} - "        # Metadata
        report += f"errors: {metadata_error}\n"
        report += f"File           ->  successful: {add_spaces(file_succs)} - "            # File
        report += f"errors: {file_error}"
        
        if process_type != 'Pages':
            delete_succs = shell_interface.count_successful_record_delete
            delete_error = shell_interface.count_errors_record_delete
            report += f"\nDelete         ->  successful: {add_spaces(delete_succs)} - "    # Delete
            report += f"errors: {delete_error}"

    print(report)

    # RECORDS.LOG
    file_records = f'{shell_interface.dirpath}/reports/{shell_interface.date.today()}_records.log'
    open(file_records, "a").write(report)

    # SUMMARY.LOG
    file_summary = f'{shell_interface.dirpath}/reports/{shell_interface.date.today()}_summary.log'
    open(file_summary, "a").write(report)


def add_spaces(value: int):
    max_length = 6                              # 6 is the maximum length of the given value
    spaces = max_length - len(str(value))
    return ''.ljust(spaces) + str(value)        # ljust -> adds spaces after a string


def initialize_count_variables(shell_interface):
    """ Initialize variables that will be used in report_records_summary method """
    shell_interface.count_total                       = 0
    shell_interface.count_errors_push_metadata        = 0
    shell_interface.count_errors_put_file             = 0
    shell_interface.count_errors_record_delete        = 0
    shell_interface.count_successful_push_metadata    = 0
    shell_interface.count_successful_push_file        = 0
    shell_interface.count_successful_record_delete    = 0
    shell_interface.count_uuid_not_found_in_pure      = 0