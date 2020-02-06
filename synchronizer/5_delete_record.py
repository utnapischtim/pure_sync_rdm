import requests
import os
import time
from pprint import pprint

dirpath = os.path.dirname(os.path.abspath(__file__))

## DELETE RECORDS IN to_delete.log
# file_name = dirpath + '/reports/to_delete.log'

# DELETE ALL RECORDS
os.system('/usr/bin/python /home/bootcamp/src/pure_sync_rdm/synchronizer/3_get_from_rdm.py')
file_name = dirpath + '/reports/all_rdm_recids.log'     

toDel_recordss = open(file_name, 'r')

token = 'NWx9pTlbl9jDOwTabxuRDfmfsDtQNbgohx7f7YKRueRS6CZSOnJZyRPtxUa4'
headers = {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json',
}

record_id = toDel_recordss.readline()
cnt = 0

while record_id:
    time.sleep(1)
    r_id = record_id.strip()

    response = requests.delete('https://127.0.0.1:5000/api/records/' + r_id, headers=headers, verify=False)

    record_id = toDel_recordss.readline()
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

print(f'\n{cnt} records deleted\n')