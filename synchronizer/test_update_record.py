from setup import *
import requests
import json

recid = '8qm11-45q51'

data = {}
data['title'] = 'Title 756'
data = json.dumps(data)
print(data)

data_utf8 = data.encode('utf-8')

headers = {
    'Authorization': f'Bearer {token_rdm}',
    'Content-Type': 'application/json',
}
params = (
    ('prettyprint', '1'),
)
url = f'{rdm_api_url_records}api/records/{recid}'
response = requests.post(url, headers=headers, params=params, data=data_utf8, verify=False)
print(response)
print(response.content)