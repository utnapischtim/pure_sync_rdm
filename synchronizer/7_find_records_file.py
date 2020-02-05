import json
import os

dirpath = os.path.dirname(os.path.abspath(__file__))

resp_json = open(dirpath + '/reports/resp_pure.json', 'r')
resp_json = json.load(resp_json)

cnt = 0
cntf = 0

for item in resp_json['items']:
    cnt += 1
    print(cnt, ' ', item['uuid'])

    if 'electronicVersions' in item:

        for EV in item['electronicVersions']:
            if 'file' in EV:
                cntf += 1
                print('\tfile: ',EV['file']['fileName'])

print('\nTot files: ', cntf, '\n')