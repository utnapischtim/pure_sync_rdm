import requests
from datetime                       import date, datetime
from setup                          import rdm_host_url, token_rdm
from setup                          import dirpath, data_files_name
from source.general_functions       import add_to_full_report, dirpath
from source.rdm.general_functions   import too_many_rdm_requests_check
from source.rdm.requests            import Requests

rdm_requests = Requests()

def delete_from_list():
    
    count_success                  = 0
    count_total                    = 0
    count_errors_record_delete     = 0
    count_successful_record_delete = 0

    file_name = data_files_name['delete_recid_list']
    recids = open(file_name, 'r').readlines()

    if len(recids) == 0:
        add_to_full_report('\nThere is nothing to delete.\n')
        return

    for recid in recids:

        recid = recid.strip('\n')

        # Ignore empty lines
        if len(recid) == 0:
            continue

        count_total += 1

        if len(recid) != 11:
            add_to_full_report(f'\n{recid} -> Wrong recid lenght! \n')
            continue
        
        # -- REQUEST --
        response = delete_record(recid)

        # 410 -> "PID has been deleted"
        if response.status_code < 300 or response.status_code == 410:
            count_success += 1
            count_successful_record_delete += 1
        else:
            count_errors_record_delete += 1



#       ---     ---     ---
def delete_record(recid: str):
    
    # NOTE: the user ACCOUNT related to the used TOKEN must be ADMIN

    # Delete record request
    # url = f'{rdm_host_url}api/records/{recid}'
    response = rdm_requests.rdm_delete_metadata(recid)

    report = f'\tRDM delete record     - {response} - Deleted recid:        {recid}'
    add_to_full_report(report)

    # Append to yyyy-mm-dd_records.log
    current_time = datetime.now().strftime("%H:%M:%S")
    report_line = f'{current_time} - delete_from_rdm - {response} - {recid}\n'
    
    file_name = f'{dirpath}/reports/{date.today()}_records.log'
    open(file_name, "a").write(report_line)

    # If the status_code is 429 (too many requests) then it will wait for some minutes
    too_many_rdm_requests_check(response)

    # 410 -> "PID has been deleted"
    if response.status_code >= 300 and response.status_code != 410:
        add_to_full_report(response.content)
        return False

    # remove deleted recid from to_delete.log
    file_name = data_files_name['delete_recid_list']
    with open(file_name, "r") as f:
        lines = f.readlines()
    with open(file_name, "w") as f:
        for line in lines:
            if line.strip("\n") != recid:
                f.write(line)

    # remove record from all_rdm_records.log
    file_name = data_files_name['all_rdm_records']
    with open(file_name, "r") as f:
        lines = f.readlines()
    with open(file_name, "w") as f:
        for line in lines:
            line_recid = line.strip("\n")
            line_recid = line_recid.split(' ')[1]
            if line_recid != recid:
                f.write(line)

    return response