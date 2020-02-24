from setup import *

def rdm_push_by_uuid(my_prompt):
    # try:

    # read to_transfer.log
    retrans_data = open(my_prompt.dirpath + '/data/to_transfer.txt', 'r')

    if not my_prompt.count_http_response_codes:
        my_prompt.count_http_response_codes = {}

    my_prompt.cnt_errors = 0
    cnt_tot = 0
    cnt_true = 0

    uuid = retrans_data.readline()
    
    while uuid:
        cnt_tot += 1
                    
        if (len(uuid.strip()) != 36):
            print('Invalid uuid lenght.\n')
            uuid = retrans_data.readline()
            continue

        response = get_pure_by_id(my_prompt, uuid.strip())

        if response == True:        cnt_true += 1
        
        uuid = retrans_data.readline()

    
    print('\n---------------------')
    report = f"\nChanges - {my_prompt.date.today()} - "

    if cnt_tot == 0:
        report += "success\nNothing to trasmit\n"
    else:
        percent_success = cnt_true * 100 / cnt_tot

        if percent_success >= upload_percent_accept:
            report += "success\n"
        else:
            report += "error\n"

        current_time = my_prompt.datetime.now().strftime("%H:%M:%S")
        report += f"{current_time}\nTot records: {cnt_tot} - Success transfer: {cnt_true}\n"

    # Adds report to yyyy-mm-dd_updates.log
    date_today = str(my_prompt.date.today())
    file_name = f'{my_prompt.dirpath}/reports/{date_today}_updates.log'
    open(file_name, "a").write(report)

    print(report)

    # except:
    #     print('\n!!!   !!!   ERROR in rdm_push_by_uuid   !!!   !!!\n')



def get_pure_by_id(my_prompt, uuid):
    """ Method used to get the metadata information about the record from Pure """
    
    # try:
    from functions.rdm_push import create_invenio_data
    my_prompt.exec_type = 'by_id'
    
    headers = {
        'Accept': 'application/json',
        'api-key': pure_api_key,
    }
    params = (
        ('apiKey', pure_api_key),
    )
    response = my_prompt.requests.get(pure_rest_api_url + 'research-outputs/' + uuid, headers=headers, params=params)
    print(f'\nPure get metadata\t->\t{response}')
    if response.status_code >= 300:
        print(response.content)
        file_name = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_rdm-push-records.log'
        report = f'Get metadata from Pure - {response.content}\n'
        open(file_name, "a").write(report)
        my_prompt.time.sleep(1.5)
        
        # adds metadata http response codes into array
        if response.status_code not in my_prompt.count_http_response_codes:
            my_prompt.count_http_response_codes[response.status_code] = 0

        my_prompt.count_http_response_codes[response.status_code] += 1
        return
        # raise Exception

    open(my_prompt.dirpath + "/data/temporary_files/resp_pure.json", 'wb').write(response.content)
    my_prompt.item = my_prompt.json.loads(response.content)
    
    # Creates data to push to InvenioRDM
    return create_invenio_data(my_prompt)

    # except:
    #     print('\n!!!   !!!   ERROR in get_pure_by_id method   !!!   !!!\n')