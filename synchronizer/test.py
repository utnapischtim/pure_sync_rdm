import json
import os
from pprint import pprint

dirpath = os.path.dirname(os.path.abspath(__file__))

resp_json = open(dirpath + '/reports/resp_pure.json', 'r')             # -- TEMPORARY -- 
resp_json = json.load(resp_json)                                            # -- TEMPORARY -- 
cnt=0
cnta=0
for item in resp_json['items']:

    if 'electronicVersions' in item:
        cnt+=1
        child = item['electronicVersions']
        # print(cnt, '----------------')
        # pprint(child)
        # exit()
        # if 'file' in child['accessTypes']:
        if 'file' in child[0]:
            # cnta+=1
            # print('a - ', cnta)
            # pprint(item['electronicVersions'])
            # pprint(item['electronicVersions']['title'])
            # pprint(child[0]['title'])
            pprint(child[0]['file']['size'])