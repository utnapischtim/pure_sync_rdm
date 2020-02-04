import requests
import os
from pprint import pprint

dirpath = os.path.dirname(os.path.abspath(__file__))
file_name = dirpath + '/reports/to_delete.log'

retrans_data = open(file_name, 'r')

token = 'tbLJnp63VamCPLvqWDGGYMgJLCIG8Yq7CyElWqPSMQQNBlWTIEDEO2getinI'
headers = {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json',
}

record_id = retrans_data.readline()
cnt = 0

while record_id:

    r_id = record_id.strip()

    response = requests.delete('https://127.0.0.1:5000/api/records/' + r_id, headers=headers, verify=False)

    record_id = retrans_data.readline()
    print(f'\n{r_id} {response}\n')
    
    if response.status_code >= 300:         print(response.content)
    else:
        cnt += 1
        # remove deleted record_id
        with open(file_name, "r") as f:
            lines = f.readlines()
        with open(file_name, "w") as f:
            for line in lines:
                if line.strip("\n") != r_id:
                    f.write(line)

print(f'\n{cnt} records deleted')