import requests
import json
import time
import os
from pprint import pprint

dirpath = os.path.dirname(os.path.abspath(__file__))
params = (('prettyprint', '1'),)

go_on = True
pag = 1
pag_size = 250

uuid_str = ''
recid_str = ''

while go_on == True:

    response = requests.get(
        f'https://localhost:5000/api/records/?sort=mostrecent&size={pag_size}&page={pag}', 
        params=params, 
        verify=False
        )
    open(dirpath + "/reports/resp_rdm.json", 'wb').write(response.content)
    print(response)

    if response.status_code >= 300:
        print(response.content)
        exit()

    resp_json = json.loads(response.content)

    for i in resp_json['hits']['hits']:
        pprint(i['metadata']['uuid'])
        uuid_str += i['metadata']['uuid'] + '\n'
        recid_str += i['metadata']['recid'] + '\n'

    if 'next' not in resp_json['links']:
        print('\n- End - No more pages available\n')
        go_on = False

    time.sleep(3)
    pag += 1
    
    
open(dirpath + "/reports/all_rdm_uuids.log", 'w+').write(uuid_str)
open(dirpath + "/reports/all_rdm_recids.log", 'w+').write(recid_str)