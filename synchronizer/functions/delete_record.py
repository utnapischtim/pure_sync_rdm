from setup import *


def delete_from_list(shell_interface):
    # NOTE: the user ACCOUNT related to the used TOKEN must be ADMIN
    """
    pipenv run invenio roles add admin@invenio.org admin
    """
    
    count_success = 0
    count_total = 0
    shell_interface.count_errors_record_delete        = 0
    shell_interface.count_successful_record_delete    = 0

    file_name = f'{shell_interface.dirpath}/data/to_delete.txt'
    recids = open(file_name, 'r').readlines()

    if len(recids) == 0:
        print('\nThere is nothing to delete.\n')
        return

    for recid in recids:

        recid = recid.strip('\n')

        # Ignore empty lines
        if len(recid) == 0:
            continue

        count_total += 1

        if len(recid) != 11:
            print(f'\n{recid} -> Wrong recid lenght! \n')
            continue
        
        # -- REQUEST --
        response = delete_record(shell_interface, recid)

        # 410 -> "PID has been deleted"
        if response.status_code < 300 or response.status_code == 410:
            count_success += 1
            shell_interface.count_successful_record_delete += 1
        else:
            shell_interface.count_errors_record_delete += 1



#   DELETE_RECORD
def delete_record(shell_interface, recid: str):

    #   REQUEST
    headers = {
        'Authorization': f'Bearer {token_rdm}',
        'Content-Type': 'application/json',
    }
    url = f'{rdm_api_url_records}api/records/{recid}'
    response = shell_interface.requests.delete(url, headers=headers, verify=False)
    #   ---
    
    print(f'\tRDM delete record  - {response} - Deleted recid:        {recid}')

    # Append to yyyy-mm-dd_records.log
    current_time = shell_interface.datetime.now().strftime("%H:%M:%S")
    report_line = f'{current_time} - delete_from_rdm - {response} - {recid}\n'
    
    file_name = f'{shell_interface.dirpath}/reports/{shell_interface.date.today()}_records.log'
    open(file_name, "a").write(report_line)
    
    # 410 -> "PID has been deleted"
    if response.status_code < 300 or response.status_code == 410:

        # remove deleted recid from to_delete.log
        file_name = shell_interface.dirpath + "/data/to_delete.txt"
        with open(file_name, "r") as f:
            lines = f.readlines()
        with open(file_name, "w") as f:
            for line in lines:
                if line.strip("\n") != recid:
                    f.write(line)

        # remove record from all_rdm_records.log
        file_name = shell_interface.dirpath + "/data/all_rdm_records.txt"
        with open(file_name, "r") as f:
            lines = f.readlines()
        with open(file_name, "w") as f:
            for line in lines:
                line_recid = line.strip("\n")
                line_recid = line_recid.split(' ')[1]
                if line_recid != recid:
                    f.write(line)

    elif response.status_code == 429:           # http 429 -> too many requests
        shell_interface.time.sleep(wait_429)          # wait for ~ 15 min
    else:
        print(response.content)

    # Makes a push request every ~ 3 sec
    shell_interface.time.sleep(push_dist_sec)

    return response