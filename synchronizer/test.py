import json
import os

dirpath = os.path.dirname(os.path.abspath(__file__))

resp_json = open(dirpath + '/data/temporary_files/resp_pure_1.json', 'r')
resp_json = json.load(resp_json)

cnt = 0
cntf = 0

for item in resp_json['items']:
    cnt += 1
    # print(cnt, ' ', item['uuid'])

    if 'electronicVersions' in item:

        for EV in item['electronicVersions']:
            if 'file' in EV:
                cntf += 1
                print(item['uuid'])
                # print('\tfile: ',EV['file']['fileName'])

print('\nTot files: ', cntf, '\n')