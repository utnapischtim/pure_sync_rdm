from setup import *


def delete_from_list(my_prompt):
    # NOTE: the user ACCOUNT related to the used TOKEN must be ADMIN
    # pipenv run invenio roles add admin@invenio.org admin
    # try:
    print('\n---   ---   ---\nDELETE RECORDS\n')
    count_success = 0
    count_total = 0
    my_prompt.count_errors_record_delete        = 0
    my_prompt.count_successful_record_delete    = 0

    file_name = my_prompt.dirpath + '/data/to_delete.txt'
    records_to_del = open(file_name, 'r').readlines()

    for recid in records_to_del:

        count_total += 1
        recid = recid.strip('\n')

        if len(recid) != 11:
            print(f'\n{recid} -> Wrong recid lenght! \n')
            continue
        
        # -- REQUEST --
        response = delete_record(my_prompt, recid)

        # 410 -> "PID has been deleted"
        if response.status_code < 300 or response.status_code == 410:
            count_success += 1
            my_prompt.count_successful_record_delete += 1
        else:
            my_prompt.count_errors_record_delete += 1

    current_time = my_prompt.datetime.now().strftime("%H:%M:%S")
    report = f"\n{current_time}\nDelete - {my_prompt.date.today()} - "

    if count_total == 0:
        report += "success\nNothing to trasmit\n"
    else:
        percent_success = count_success * 100 / count_total

        if percent_success >= upload_percent_accept:
            report += "success\n"
        else:
            report += "error\n"

    report += f"Tot records: {count_total} - Success transfer: {count_success}\n"

    date_today = str(my_prompt.date.today())
    open(f'{my_prompt.dirpath}/reports/{date_today}_summary.log', "a").write(report)
    
    print(report)

    # except:
    #     print('\n---   !!!   Error in delete_record   !!!   ---\n')


#   DELETE_RECORD
def delete_record(my_prompt, recid):

    #   REQUEST
    headers = {
        'Authorization': 'Bearer ' + token_rdm,         # token from setup.py
        'Content-Type': 'application/json',
    }
    url = f'{rdm_api_url_records}api/records/{recid}'
    response = my_prompt.requests.delete(url, headers=headers, verify=False)
    #   ---
    
    print(f'\tRDM delete\t->\t{response} - {recid}')

    # Append to yyyy-mm-dd_records.log
    current_time = my_prompt.datetime.now().strftime("%H:%M:%S")
    report_line = f'{current_time} - delete_from_rdm - {response} - {recid}\n'
    
    file_name = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_records.log'
    open(file_name, "a").write(report_line)
    
    # 410 -> "PID has been deleted"
    if response.status_code < 300 or response.status_code == 410:

        # remove deleted recid from to_delete.log
        file_name = my_prompt.dirpath + "/data/to_delete.txt"
        with open(file_name, "r") as f:
            lines = f.readlines()
        with open(file_name, "w") as f:
            for line in lines:
                if line.strip("\n") != recid:
                    f.write(line)

        # remove record from all_rdm_records.log
        file_name = my_prompt.dirpath + "/data/all_rdm_records.txt"
        with open(file_name, "r") as f:
            lines = f.readlines()
        with open(file_name, "w") as f:
            for line in lines:
                line_recid = line.strip("\n")
                line_recid = line_recid.split(' ')[1]
                if line_recid != recid:
                    f.write(line)

    elif response.status_code == 429:           # http 429 -> too many requests
        my_prompt.time.sleep(wait_429)          # wait for ~ 15 min
    else:
        print(response.content)

    # Makes a push request every ~ 3 sec
    my_prompt.time.sleep(push_dist_sec)

    return response