import requests
import json
import time
import os
from datetime import date
from pprint import pprint     

dirpath = os.path.dirname(os.path.abspath(__file__))

pag = 2
pag_size = 500

headers = {
    'Accept': 'application/json',
}
params = (
    ('page', pag),
    ('pageSize', pag_size),
    ('apiKey', 'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
)
# PURE get request
response = requests.get('https://pure01.tugraz.at/ws/api/514/research-outputs', headers=headers, params=params)
open(dirpath + "/reports/resp_pure.json", 'wb').write(response.content)
resp_json = json.loads(response.content)

data = ''

for item in resp_json['items']:
    if 'openAccessPermissions' in item:
        pure_value =    item['openAccessPermissions'][0]['value']
        uuid =          item['uuid']
        print(uuid + '\t' + pure_value)
        data += str(uuid + '\t' + pure_value + '\n')

open(dirpath + "/reports/OAP.log", 'a').write(data)