
import requests
import json

headers = {
    'Content-Type': 'application/json',
}

data = '{"language": "eng"}'

print(data, '\n')

data = data.encode('utf-8')

response = requests.put('https://localhost/api/records/', headers=headers, data=data, verify=False)

print("\n", response)
if response.status_code >= 300:
    print(response.content)
