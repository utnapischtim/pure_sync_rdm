import requests
import json

dirpath = '/home/bootcamp/src/pure_sync_rdm/synchronizer/'

pure_api_key =      open(f'{dirpath}/data_setup/pure_api_key.txt', 'r').readline()
pure_rest_api_url = 'https://pure01.tugraz.at/ws/api/514/'

headers = {
    'Accept': 'application/json',
    'api-key': pure_api_key,
}
params = (
    ('page', 2),
    ('pageSize', 1000),
    ('apiKey', pure_api_key),
)
# PURE get request
response = requests.get(pure_rest_api_url + 'research-outputs', headers=headers, params=params)
open(dirpath + "/data/temporary_files/resp_pure.json", 'wb').write(response.content)

# resp_json = json.loads(response.content)

# for item in resp_json['items']:
#     print(item['uuid'])
