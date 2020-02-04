import requests
from pprint import pprint
import os

inv_rec_id = 'y0jhs-yx610'
token = 'tbLJnp63VamCPLvqWDGGYMgJLCIG8Yq7CyElWqPSMQQNBlWTIEDEO2getinI'



headers = {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json',
}

response = requests.delete('https://127.0.0.1:5000/api/records/' + inv_rec_id, headers=headers, verify=False)

print(response)
print(response.content)

if response.status_code == 410:         print('PID has been already deleted.')