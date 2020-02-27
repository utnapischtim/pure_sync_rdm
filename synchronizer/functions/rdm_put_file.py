from setup import *

def rdm_put_file(my_prompt, file_name):
    # try:
    file_path = my_prompt.dirpath + '/data/temporary_files/'

    # GET from RDM recid of last added record
    get_recid(my_prompt)

    # - PUT FILE TO RDM -
    headers = {
        'Content-Type': 'application/octet-stream',
    }
    data = open(file_path + file_name, 'rb').read()
    url = f'{rdm_api_url_records}api/records/{my_prompt.recid}/files/{file_name}'
    response = my_prompt.requests.put(url, headers=headers, data=data, verify=False)

    # Report
    report = ''
    print(f'\tPut file\t->\t{response}')

    current_time = my_prompt.datetime.now().strftime("%H:%M:%S")

    report += f'{current_time} - file_put_to_rdm - {response} - {my_prompt.recid}\n'

    if response.status_code >= 300:

        my_prompt.count_errors_put_file += 1
        my_prompt.file_success = False

        report += f'{response.content}\n'

    else:
        my_prompt.count_successful_push_file += 1
        my_prompt.file_success = True

        # if the upload was successful then delete file from /reports/temporary_files
        my_prompt.os.remove(file_path + file_name) 

    file_name = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_records.log'
    open(file_name, "a").write(report)
    
    return response.status_code

    # HAVING PURE ADMIN ACCOUNT REMOVE FILE FROM PURE

    # except:
    #     print('\n- Error in rdm_put_file method -\n')


def get_recid(my_prompt):
    # try:
    # GET from RDM recid of last added record
    cnt = 0
    while True:
        cnt += 1
        my_prompt.time.sleep(cnt * 2)
        response = my_prompt.requests.get(
            f'{rdm_api_url_records}api/records/?sort=mostrecent&size=1&page=1', 
            params=(('prettyprint', '1'),), 
            verify=False
            )
        resp_json = my_prompt.json.loads(response.content)

        for i in resp_json['hits']['hits']:
            my_prompt.recid  = i['metadata']['recid']
            rdm_uuid    = i['metadata']['uuid']
        
        if my_prompt.uuid == rdm_uuid:
            # print(f'Found recid: {my_prompt.recid}')
            break
        elif cnt > 10:
            print('Having troubles getting the recid of the newly added record\n')
            break
    # except:
    #     print('\n!!!    !!!  Error in get_recid method   !!!       !!!\n')
 