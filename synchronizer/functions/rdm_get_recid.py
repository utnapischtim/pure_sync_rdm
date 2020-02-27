from setup import *
from functions.delete_record import delete_from_list, delete_record

def rdm_get_recid(my_prompt, uuid):

    if len(uuid) != 36:
        print(f'\nERROR - The uuid must have 36 characters. Given: {uuid}\n')
        return False

    # GET request RDM
    params = (('prettyprint', '1'),)
    sort  = 'sort=mostrecent'
    size  = 'size=100'
    page  = 'page=1'
    query = f'q="{uuid}"'
    url = f'{rdm_api_url_records}api/records/?{sort}&{size}&{page}&{query}'
    response = my_prompt.requests.get(url, params=params, verify=False)

    if response.status_code >= 300:
        print(f'\n{uuid} - {response}')
        print(response.content)
        return False

    open(f'{my_prompt.dirpath}/data/temporary_files/rdm_get_recid.txt', "wb").write(response.content)

    # Load response
    resp_json = my_prompt.json.loads(response.content)

    total_recids = resp_json['hits']['total']
    if total_recids == 0:
        print(f'{uuid} - Recid not found in RDM')
        my_prompt.time.sleep(0.6)
        return False

    print(f'RDM get recid\t->\t{response} - total_recids: {total_recids}')

    # Iterate over all records with the same uuid
    # The first record is the most recent (they are sorted)
    count = 0
    for i in resp_json['hits']['hits']:
        count += 1
        recid = i['metadata']['recid']
        
        if count == 1:
            newest_recid = recid
        else:
            # Duplicate records are deleted
            delete_record(my_prompt, recid)

    return newest_recid

