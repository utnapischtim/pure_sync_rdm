import requests
import json
import time
import os
from pprint import pprint     
            
pag = 1
pag_size = 100

headers = {
    'Accept': 'application/json',
    'api-key': 'ca2f08c5-8b33-454a-adc4-8215cfb3e088',
}
params = (
    ('page', pag),
    ('pageSize', pag_size),
    ('apiKey', 'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
)
# PURE get request
response = requests.get('https://pure01.tugraz.at/ws/api/514/research-outputs', headers=headers, params=params)
dirpath = os.path.dirname(os.path.abspath(__file__))
open(dirpath + "/reports/resp_pure.json", 'wb').write(response.content)
resp_json = json.loads(response.content)

# resp_json = open(self.dirpath + '/reports/resp_pure.json', 'r')             # -- TEMPORARY -- 
# resp_json = json.load(resp_json)                                            # -- TEMPORARY -- 

for item in resp_json['items']:
    if 'info' in item:
        print(item['uuid'] + ' - ' + item['info']['modifiedDate'])
    else:
        print(item['uuid'])