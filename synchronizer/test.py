from setup          import *
import requests

file_name = 'img1.jpg'
recid = '9tse4-5g827'

headers = {
    'Authorization': f'Bearer {token_rdm}',
    'Content-Type': 'application/octet-stream',
}
data = open(f'{dirpath}/{file_name}', 'rb').read()
url = f'{rdm_api_url_records}api/records/{recid}/files/{file_name}'
response = requests.put(url, headers=headers, data=data, verify=False)
print(response)

# curl -k -X PUT https://localhost:5000/api/records/pv1dx-rwa61/files/snow_doge.jpg -H "Content-Type: application/octet-stream" --data-binary @snow_doge.jpg