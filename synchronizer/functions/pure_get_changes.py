from setup import *

def pure_get_changes(my_prompt):
    
    date_today = str(my_prompt.datetime.today().strftime('%Y-%m-%d'))
    
    isfile = my_prompt.os.path.isfile
    join = my_prompt.os.path.join
    reports_files = [f for f in my_prompt.os.listdir(f'{my_prompt.dirpath}/reports/') if isfile(join(f'{my_prompt.dirpath}/reports/', f))]
    reports_files = sorted(reports_files, reverse=True)

    # Iterates over all the files in /reports folder
    for file_name in reports_files:

        file_split = file_name.split('_')

        if file_split[1] != 'summary.log':
            continue

        # It will check first the most up to date files
        # If no successful update is found then will check older files
        if search_successful_change(my_prompt, file_name):
            print(f'\nSuccessful Check update found in {file_name}\n')
            last_update = file_split[0]
            break
    
    if not last_update:
        print('No successful update found among all report logs\n')
        return
    
    elif last_update == date_today:
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


def search_successful_change(my_prompt, file_name):
    """ Search for the date of the last successful update """

    file_name = f'{my_prompt.dirpath}/reports/{file_name}'
    file_data = open(file_name, 'r').read().splitlines()
    
    for line in reversed(file_data):
        if 'Changes - success' in line:
            return True

    # If that day there was no successful update
    return False



def pure_get_changes_by_date(my_prompt, changes_date):
    # try:
    from functions.get_from_rdm     import get_from_rdm
    from functions.rdm_get_recid    import rdm_get_recid
    from functions.delete_record    import delete_record

    headers = {
        'Accept': 'application/json',
    }
    params = (
        ('page', '1'),
        ('pageSize', '1000'),
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
    number_elements = resp_json['count']

    my_prompt.count_total = 0
    my_prompt.count_errors_push_metadata = 0
    my_prompt.count_errors_put_file = 0
    my_prompt.count_successful_push_metadata = 0
    my_prompt.count_successful_push_file = 0
    my_prompt.count_uuid_not_found_in_pure = 0

    report =  f'\n- Changes date: {changes_date} -\n'
    report += f'Pure get CHANGES: {response}\n'
    report += f'Elements in response: {number_elements}\n'
    print(report)

    # append to yyyy-mm-dd_rdm-push-records.log
    file_records = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_rdm-push-records.log'
    open(file_records, "a").write(report)

    to_transfer = ''
    check_duplicates = []
    count_to_transfer = 0
    my_prompt.count_http_response_codes = {}

    for item in resp_json['items']:

        if 'changeType' not in item:
            continue
        
        elif item['familySystemName'] != 'ResearchOutput':
            continue

        uuid = item['uuid']

        if uuid in check_duplicates:
            continue

        check_duplicates.append(uuid)
        
        print(f"\n{item['changeType']} - {item['uuid']}")

        #   ---     UPDATE      ---
        if item['changeType'] == 'UPDATE':
    
            # Adds the record to be transfered
            count_to_transfer += 1
            to_transfer += f'{uuid}\n'
            
            # Gets the record recid for deletion
            recid = rdm_get_recid(my_prompt, uuid)
            if not recid:
                continue
            
            # Deletes the record so that the new version is added
            delete_record(my_prompt, recid)


        #   ---     ADD / CREATE      ---
        if item['changeType'] == 'ADD' or item['changeType'] == 'CREATE':       # REVIEW !!!!!!!!!!! difference between add and create?

            # Adds the record to be transfered
            count_to_transfer += 1
            to_transfer += uuid + '\n'


        #   ---     DELETE      ---
        if item['changeType'] == 'DELETE':

            # Gets the record recid
            recid = rdm_get_recid(my_prompt, uuid)

            # Deletes the record so that the new version is added
            delete_record(my_prompt, recid)


    date_today = str(my_prompt.date.today())
    file_update = f'{my_prompt.dirpath}/reports/{date_today}_summary.log'

    # - TRANSFER -
    if count_to_transfer == 0:
        # Adds report to yyyy-mm-dd_summary.log
        open(file_update, "a").write(report)
        print(report)
        return

    print(f"\n\n-- Records to transfer: {count_to_transfer}")

    file_name = my_prompt.dirpath + '/data/to_transfer.txt'
    open(file_name, 'w').close()                    # empty file
    open(file_name, "a").write(to_transfer)         # append to file

    #    ---     ---
    from functions.rdm_push_by_uuid import rdm_push_by_uuid
    rdm_push_by_uuid(my_prompt)
    #    ---     ---
    
    print('\n---------------------')

    if my_prompt.count_total == 0:
        report = '\nChanges - success\nNothing to transmit\n'
    else:
        percent_success = my_prompt.count_successful_push_metadata * 100 / my_prompt.count_total

        if percent_success >= upload_percent_accept:
            report = "\nChanges - success\n"
        else:
            report = "\nChanges - error\n"

        current_datetime = my_prompt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report += f"{current_datetime}\n"

        report += f"Total records:\t\t\t\t{my_prompt.count_total}\n"
        report += f"Successful push metadata:\t{my_prompt.count_successful_push_metadata}\n"
        report += f"Errors push metadata:\t\t{my_prompt.count_errors_push_metadata}\n"
        report += f"Successful put file: \t\t{my_prompt.count_successful_push_file}\n"
        report += f"Error put file:\t\t\t\t{my_prompt.count_errors_put_file}\n"
        report += f"Uuid not found in pure: \t{my_prompt.count_uuid_not_found_in_pure}\n"


    # Adds report to yyyy-mm-dd_summary.log
    open(file_update, "a").write(report)
    print(report)

    # Adding count http respons to report records
    report_records = 'RDM HTTP response codes:\n'
    for key in my_prompt.count_http_response_codes:
        report_records += f'{str(key)}: {str(my_prompt.count_http_response_codes[key])},\n'
    open(file_records, "a").write(report_records)


    # except:
    #     print('\n!!!      !!!     Error in get_pure_changes     !!!   !!!\n')


