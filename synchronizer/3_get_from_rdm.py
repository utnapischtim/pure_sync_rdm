import requests
import json
import time
from pprint import pprint

params = (('prettyprint', '1'),)

go_on = True
pag = 1
uuid_rdm = []

while go_on == True:

    response = requests.get(
        f'https://localhost:5000/api/records/?sort=mostrecent&size=100&page={pag}', 
        params=params, 
        verify=False
        )
    open("./reports/resp_rdm.json", 'wb').write(response.content)
    print(response)

    if response.status_code >= 300:
        print(response.content)
        exit()

    resp_json = json.loads(response.content)

    for i in resp_json['hits']['hits']:
        pprint(i['metadata']['uuid'])
        uuid_rdm.append(i['metadata']['uuid'])

    if 'next' not in resp_json['links']:
        print('\nNo pore pages available..\n')
        go_on = False

    time.sleep(3)
    pag += 1
    

print('\n- All uuids -\n')
pprint(uuid_rdm)