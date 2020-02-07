from pprint import pprint
import requests
import os

dirpath = os.path.dirname(os.path.abspath(__file__))

file_name = '81270319.pdf'
file_url = 'https://pure01.tugraz.at/ws/files/1820831/81270319.pdf'
auth = ('ws_grosso', 'U+0n0#yI')

from requests.auth import HTTPBasicAuth

# DOWNLOAD FILE FROM PURE
response = requests.get(file_url, auth=HTTPBasicAuth('ws_grosso', 'U+0n0#yI'))
print(f'Download response - {file_name}: {response}\n')

if response.status_code < 300:
    open(str(dirpath) + '/tmp_files/' + file_name, 'wb').write(response.content)
else:
    pprint(response.content)