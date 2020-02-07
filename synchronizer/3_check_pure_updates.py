import requests
import json
import time
import os
from datetime import date
from pprint import pprint     

dirpath = os.path.dirname(os.path.abspath(__file__))

pag = 1
pag_size = 250          # is it enough?

headers = {
    'Accept': 'application/json',
}
params = (
    ('order', 'modified'),
    ('orderBy', 'descending'),
    ('page', pag),
    ('pageSize', pag_size),
    ('apiKey', 'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
)
# # PURE get request
# response = requests.get('https://pure01.tugraz.at/ws/api/514/research-outputs', headers=headers, params=params)
# open(dirpath + "/reports/resp_pure.json", 'wb').write(response.content)
# resp_json = json.loads(response.content)

resp_json = open(dirpath + '/reports/resp_pure.json', 'r')                  # -- TEMPORARY -- 
resp_json = json.load(resp_json)                                            # -- TEMPORARY -- 

date_today = 'Date today: ' + str(date.today())

report = date_today + '\n'
to_re_trans = ''

cnt  = 0
cntu = 0

for item in resp_json['items']:
    if 'info' in item:

        cnt += 1

        mod_date_time_str = item['info']['modifiedDate']
        mod_date_str = mod_date_time_str.split('T')[0]
        
        if date_today == mod_date_str:
            report += item['uuid'] + ' - To update ---\n'
            to_re_trans += item['uuid'] + '\n'
            cntu += 1
        else:
            report += item['uuid'] + ' - ' + mod_date_str + '\n'

cntstr = '\nTot: ' + str(cnt) + ' - To update: ' + str(cntu)
print(cntstr)
report += cntstr

open(dirpath + '/reports/check_pure_updates.log', "w+").write(report)
open(dirpath + "/reports/to_transfer.log", "a").write(to_re_trans)

# os.system('/usr/bin/python /home/bootcamp/src/pure_sync_rdm/synchronizer/2_reTransmit.py')