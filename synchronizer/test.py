from setup import *

def rdm_get_recid():
    import os
    import requests
    import json
    import time
    from datetime import date, datetime, timedelta

    dirpath = os.path.dirname(os.path.abspath(__file__))

    file_name = dirpath + '/test.txt'
    all_rdm_records = open(file_name, 'r').readlines()

    for uuid in all_rdm_records:
        uuid = uuid.strip('\n')

        # GET request
        params = (('prettyprint', '1'),)
        sort  = 'sort=mostrecent'
        size  = 'size=100'
        page  = 'page=1'
        query = f'q="{uuid}"'
        url = f'{rdm_api_url_records}api/records/?{sort}&{size}&{page}&{query}'
        
        response = requests.get(url, params=params, verify=False)
        # open(dirpath + "/test.json", 'wb').write(response.content)

        resp_json = json.loads(response.content)

        total_recids = resp_json['hits']['total']

        print(f'\n{uuid} - {response} - total_recids: {total_recids}')

        # Iterate over all records with the same uuid
        # The first record is the most recent (they are sorted)
        count = 0
        to_delete = ''
        for i in resp_json['hits']['hits']:
            
            if count == 0:
                recid = i['metadata']['recid']
            else:
                to_delete += f"{i['metadata']['recid']}\n"
            
            count += 1

        print(f'Recid: {recid}')
        if count > 1:
            print(f'To_delete:\n{to_delete}')
            open(dirpath + "/data/to_delete.txt", "a").write(to_delete)

        time.sleep(0.5)

rdm_get_recid()


