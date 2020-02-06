import requests
import json

response = requests.get(
    'https://localhost:5000/api/records/?sort=mostrecent&size=1&page=1', 
    params=(('prettyprint', '1'),), 
    verify=False
    )
resp_json = json.loads(response.content)

for i in resp_json['hits']['hits']:
    print(i['metadata']['recid'])