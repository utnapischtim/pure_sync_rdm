import json
import os
from pprint import pprint

dirpath = os.path.dirname(os.path.abspath(__file__))
resp_json = json.load(open(dirpath + '/iso6393.json', 'r'))

for i in resp_json:
    if i['name'] == 'Portuguese':
        pprint(i['iso6392B'])
