from setup import *
import requests
import json

recid = 'hya32-x9874'

data = {}
data['title'] = 'Title two2'
data['access_right'] = 'closed'
data['owners'] = [2]
data['language'] =  'eng'
data['contributors'] = [{'name': 'some, researcher'}]
data['_access'] = {'metadata_restricted': True, 'files_restricted': True}

data = json.dumps(data)

data_utf8 = data.encode('utf-8')

headers = {
    'Authorization': f'Bearer {token_rdm}',
    'Content-Type': 'application/json',
}
params = (
    ('prettyprint', '1'),
)

url = f'{rdm_api_url_records}api/records/{recid}'

response = requests.put(url, headers=headers, params=params, data=data_utf8, verify=False)

print(response)

if response.status_code >= 300:
    print(response.content)

