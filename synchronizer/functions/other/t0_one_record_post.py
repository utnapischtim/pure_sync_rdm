import requests
import json

# # PUSH METADATA
# headers = {
#     'Content-Type': 'application/json',
# }
# params = (
#     ('prettyprint', '1'),
# )
# data = '{"title": "Some title4", "language": "eng", "access_right": "open", "owners": [1], "contributors": [{"name": "Doe, John"}], "_access": {"metadata_restricted": false, "files_restricted": false}}'
# data = data.encode('utf-8')

# response = requests.post('https://localhost:5000/api/records/', headers=headers, params=params, data=data, verify=False)

# print("\n", response)
# if response.status_code >= 300:
#     print(response.content)


# PUT FILE
recid = '7de1d-c0p31'
file_name = 'file_test.txt'

file_path_name = f'/home/bootcamp/src/pure_sync_rdm/synchronizer/data/temporary_files/{file_name}'

# - PUT FILE TO RDM -
headers = {
    'Content-Type': 'application/octet-stream',
}
data = open(file_path_name, 'rb').read()
url = f'https://invenio-test.tugraz.at/api/records/{recid}/files/{file_name}'
response = requests.put(url, headers=headers, data=data, verify=False)

print(f'File put {response}')
print(response.content)