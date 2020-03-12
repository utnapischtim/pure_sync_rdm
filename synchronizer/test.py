import json
import os

dirpath = os.path.dirname(os.path.abspath(__file__))

resp_json = open(dirpath + '/data/temporary_files/resp_pure_4.json', 'r')
resp_json = json.load(resp_json)

cnt = 0
cnt_files = 0

for item in resp_json['items']:
    cnt += 1

    if 'electronicVersions' in item:

        for EV in item['electronicVersions']:
            if 'file' in EV:
                cnt_files += 1
                print(item['uuid'])

print('\nTot files: ', cnt_files, '\n')