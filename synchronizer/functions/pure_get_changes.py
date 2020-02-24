from setup import *

def pure_get_changes(my_prompt):
    
    date_today = str(my_prompt.date.today())
    
    isfile = my_prompt.os.path.isfile
    join = my_prompt.os.path.join
    onlyfiles = [f for f in my_prompt.os.listdir(f'{my_prompt.dirpath}/reports/') if isfile(join(f'{my_prompt.dirpath}/reports/', f))]

    for file in onlyfiles:
        file_date = file.split()
    print(onlyfiles)
    
def pure_get_changes_by_date(my_prompt, date):
    # try:
    from functions.get_from_rdm     import get_from_rdm
    from functions.rdm_get_recid    import rdm_get_recid
    from functions.delete_record    import delete_record

    headers = {
        'Accept': 'application/json',
    }
    params = (
        ('page', '1'),
        ('pageSize', '250'),
        ('apiKey', 'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
    )
    # # PURE get request
    url = f'{pure_rest_api_url}changes/{date}'
    response = my_prompt.requests.get(url, headers=headers, params=params)
    # # ---- --- -------

    if response.status_code >= 300:
        print(response.content)

    # Write data into resp_pure_changes
    file_name = f'{my_prompt.dirpath}/data/temporary_files/resp_pure_changes.json'
    open(file_name, 'wb').write(response.content)

    # Load response json
    resp_json = my_prompt.json.loads(response.content)
    number_elements = resp_json['count']

    report =  f'\nPure CHANGES response: {response}\n'
    report += f'Elements in response: {number_elements}\n'
    print(report)

    # append to yyyy-mm-dd_rdm-push-records.log
    file_report = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_rdm-push-records.log'
    open(file_report, "a").write(report)

    to_transfer = ''
    count_to_transfer = 0
    my_prompt.count_http_response_codes = {}

    for item in resp_json['items']:

        my_prompt.time.sleep(1.5)   # TEMP!!!


        if 'changeType' not in item:
            continue
        
        uuid = item['uuid']
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


    # - TRANSFER -
    if count_to_transfer > 0:
        print(f"\n\n-- Records to transfer: {count_to_transfer}")

        file_name = my_prompt.dirpath + '/data/to_transfer.txt'
        open(file_name, 'w').close()                    # empty file
        open(file_name, "a").write(to_transfer)         # append to file

        from functions.rdm_push_by_uuid import rdm_push_by_uuid
        rdm_push_by_uuid(my_prompt)

    
    # Adding count http respons to report
    report = 'RDM HTTP response codes:\n'
    for key in my_prompt.count_http_response_codes:
        report += f'{str(key)}: {str(my_prompt.count_http_response_codes[key])},\n'
    open(file_report, "a").write(report)

    # except:
    #     print('\n!!!      !!!     Error in get_pure_changes     !!!   !!!\n')


