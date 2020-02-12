import requests
import json

headers = {
    'Content-Type': 'application/json',
}
params = (
    ('prettyprint', '1'),
)

title = 'some "title3'
title = title.replace('"', '\\"')       # adds \ before "


data = '{"title": "Some title2", "access_right": "open", "owners": [1], "contributors": [{"name": "Doe, John"}], "_access": {"metadata_restricted": false, "files_restricted": false}}'

print(data, '\n')

data = data.encode('utf-8')

response = requests.post('https://localhost:5000/api/records/', headers=headers, params=params, data=data, verify=False)

print("\n", response)
if response.status_code == 400:
    print(response.content)



