import requests
import json
import time
from setup      import *

# c0a3f804-fb58-4bbb-9ee4-0a3f7276c0c8 martin ebner
uuid = 'c0a3f804-fb58-4bbb-9ee4-0a3f7276c0c8'

import requests

headers = {
    'Accept': 'application/json',
}
params = (
    ('apiKey', pure_api_key),
)
response = requests.get(f'{pure_rest_api_url}/persons/{uuid}', headers=headers, params=params)

open(f'{dirpath}/data/temporary_files/resp_pure_persons.json', 'wb').write(response.content)
resp_json = json.loads(response.content)

print(response)

print(resp_json['orcid'])

