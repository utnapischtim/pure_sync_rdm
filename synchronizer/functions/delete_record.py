from setup                          import dirpath, token_rdm, rdm_api_url_records
# from functions.general_functions    import too_many_rdm_requests_check

def delete_from_list(shell_interface):

    from functions.general_functions    import add_to_full_report
    
    # NOTE: the user ACCOUNT related to the used TOKEN must be ADMIN
    
    count_success = 0
    count_total = 0
    shell_interface.count_errors_record_delete        = 0
    shell_interface.count_successful_record_delete    = 0

    file_name = f'{dirpath}/data/to_delete.txt'
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
        response = delete_record(shell_interface, recid)

        # 410 -> "PID has been deleted"
        if response.status_code < 300 or response.status_code == 410:
            count_success += 1
            shell_interface.count_successful_record_delete += 1
        else:
            shell_interface.count_errors_record_delete += 1



#   DELETE_RECORD
def delete_record(shell_interface, recid: str):

    from functions.general_functions    import add_to_full_report, too_many_rdm_requests_check
    
    #   REQUEST
    headers = {
        'Authorization': f'Bearer {token_rdm}',
        'Content-Type': 'application/json',
    }
    url = f'{rdm_api_url_records}api/records/{recid}'
    response = shell_interface.requests.delete(url, headers=headers, verify=False)
    #   ---
    
    report = f'\tRDM delete record     - {response} - Deleted recid:        {recid}'
    add_to_full_report(report)

    # Append to yyyy-mm-dd_records.log
    current_time = shell_interface.datetime.now().strftime("%H:%M:%S")
    report_line = f'{current_time} - delete_from_rdm - {response} - {recid}\n'
    
    file_name = f'{dirpath}/reports/{shell_interface.date.today()}_records.log'
    open(file_name, "a").write(report_line)

    # If the status_code is 429 (too many requests) then it will wait for some minutes
    too_many_rdm_requests_check(response)

    # 410 -> "PID has been deleted"
    if response.status_code >= 300 and response.status_code != 410:
        add_to_full_report(response.content)
        return False

    # remove deleted recid from to_delete.log
    file_name = dirpath + "/data/to_delete.txt"
    with open(file_name, "r") as f:
        lines = f.readlines()
    with open(file_name, "w") as f:
        for line in lines:
            if line.strip("\n") != recid:
                f.write(line)

    # remove record from all_rdm_records.log
    file_name = dirpath + "/data/all_rdm_records.txt"
    with open(file_name, "r") as f:
        lines = f.readlines()
    with open(file_name, "w") as f:
        for line in lines:
            line_recid = line.strip("\n")
            line_recid = line_recid.split(' ')[1]
            if line_recid != recid:
                f.write(line)

    return response