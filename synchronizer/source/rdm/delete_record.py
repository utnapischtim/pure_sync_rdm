from setup                          import rdm_host_url, token_rdm, data_files_name, log_files_name
from source.general_functions       import current_time
from source.rdm.requests            import Requests
from source.reports                 import Reports

rdm_requests = Requests()
reports = Reports()

def delete_from_list():
    
    count_success                  = 0
    count_total                    = 0
    count_errors_record_delete     = 0
    count_successful_record_delete = 0

    file_name = data_files_name['delete_recid_list']
    recids = open(file_name, 'r').readlines()

    if len(recids) == 0:
        reports.add(['console'], '\nThere is nothing to delete.\n')
        return

    for recid in recids:

        recid = recid.strip('\n')

        # Ignore empty lines
        if len(recid) == 0:
            continue

        count_total += 1

        if len(recid) != 11:
            reports.add(['console'], f'\n{recid} -> Wrong recid lenght! \n')
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
    response = rdm_requests.rdm_delete_metadata(recid)

    report = f'\tRDM delete record     - {response} - Deleted recid:        {recid}'
    reports.add(['console'], report)

    report_line = f'{current_time()} - delete_from_rdm - {response} - {recid}\n'
    reports.add(['records'], report)

    # 410 -> "PID has been deleted"
    if response.status_code >= 300 and response.status_code != 410:
        return False

    # Remove deleted recid from to_delete.txt
    file_name = data_files_name['delete_recid_list']
    with open(file_name, "r") as f:
        lines = f.readlines()
    with open(file_name, "w") as f:
        for line in lines:
            if line.strip("\n") != recid:
                f.write(line)

    # remove record from all_rdm_records.txt
    file_name = data_files_name['all_rdm_records']
    with open(file_name, "r") as f:
        lines = f.readlines()
    with open(file_name, "w") as f:
        for line in lines:
            line_recid = line.strip("\n")
            line_recid = line_recid.split(' ')[1]
            if line_recid != recid:
                f.write(line)
    return True



def delete_all_records():

    file_data = open(data_files_name['all_rdm_records']).readlines()
    for line in file_data:
        recid = line.split(' ')[1].strip('\n')
        delete_record(recid)