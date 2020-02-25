from setup import *

def rdm_push_by_uuid(my_prompt):
    # try:

    # read to_transfer.log
    retrans_data = open(my_prompt.dirpath + '/data/to_transfer.txt', 'r')

    if not my_prompt.count_http_response_codes:
        my_prompt.count_http_response_codes = {}

    uuid = retrans_data.readline()
    
    while uuid:
                    
        if (len(uuid.strip()) != 36):
            print('Invalid uuid lenght.\n')
            uuid = retrans_data.readline()
            continue
        
        #   ---     ---
        get_pure_by_id(my_prompt, uuid.strip())
        #   ---     ---
        
        uuid = retrans_data.readline()

    return
    
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
        my_prompt.count_uuid_not_found_in_pure += 1
        print(response.content)

        file_name = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_rdm-push-records.log'
        report = f'Get metadata from Pure - {response.content}\n'
        open(file_name, "a").write(report)

        my_prompt.time.sleep(1)
        return 

    open(my_prompt.dirpath + "/data/temporary_files/resp_pure.json", 'wb').write(response.content)
    my_prompt.item = my_prompt.json.loads(response.content)
    
    # Creates data to push to InvenioRDM
    return create_invenio_data(my_prompt)

    # except:
    #     print('\n!!!   !!!   ERROR in get_pure_by_id method   !!!   !!!\n')