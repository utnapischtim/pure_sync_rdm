import requests
import json

headers = {
    'Content-Type': 'application/json',
}
params = (
    ('prettyprint', '1'),
)

data = '{"language": "eng"}'

print(data, '\n')

data = data.encode('utf-8')

response = requests.post('https://localhost:5000/api/records/g7ywb-mg665/', headers=headers, params=params, data=data, verify=False)

print("\n", response)
if response.status_code >= 300:
    print(response.content)




