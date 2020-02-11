import requests
import json
import time
import os
from datetime import date, datetime, timedelta
from pprint import pprint     

dirpath = os.path.dirname(os.path.abspath(__file__))
days_span = 4

# Get date of last update
file_name = dirpath + "/reports/d_daily_updates.log"


# Finds last date when the update successfully happened
with open(file_name, 'r') as f:
    lines = f.read().splitlines()
    for line in reversed(lines):
        if '@' in line:
            line =              line.split('@ ')[1]
            line =              line.split(' - ')
            date_last_update =  line[0]
            result =            line[1]
            if result !=        'success':  continue
            else:                           break

date_today = date.today()
date_object = datetime.strptime(date_last_update, '%Y-%m-%d').date()

# one day after the last update
date_limit = str(date_object + timedelta(days=1))


report = '\n---\n---   ---\n---   ---   ---'
report += f"\nToday: {date_today}\nLast update: {date_last_update} \nDate limit: {date_limit}\n"
print(report)
print(f"See file '/records/full_reports/{date_today}_pure_updates.log'\n")

pag = 1
while True:
    report += f'- Pag: {pag} -\n'
    print(f'Pag: {pag}')
    headers = {
        'Accept': 'application/json',
    }
    params = (
        ('order',      'modified'),
        ('orderBy',    'descending'),
        ('page',        pag),                  # page
        ('pageSize',    250),                  # records per page
        ('apiKey',     'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
    )
    # PURE get request
    response = requests.get('https://pure01.tugraz.at/ws/api/514/research-outputs', headers=headers, params=params)
    print('Pure resp: ', response)
    open(dirpath + "/reports/resp_pure.json", 'wb').write(response.content)
    resp_json = json.loads(response.content)

    # resp_json = open(dirpath + '/reports/resp_pure.json', 'r')                  # -- TEMPORARY --
    # resp_json = json.load(resp_json)                                            # -- TEMPORARY --

    to_re_trans = ''

    cnt  = 0
    cntu = 0

    for item in resp_json['items']:
        if 'info' in item:

            cnt += 1

            record_date_time = item['info']['modifiedDate']
            record_date = str(record_date_time.split('T')[0])
            
            if record_date >= date_limit:
                report += item['uuid'] + ' - ' + record_date + ' - To update ---\n'
                to_re_trans += item['uuid'] + '\n'
                cntu += 1
            else:
                report += item['uuid'] + ' - ' + record_date + ' - ok\n'

    print('Tot: ' + str(cnt) + ' - To update: ' + str(cntu) + '\n')
    report += 'Tot: ' + str(cnt) + ' - To update: ' + str(cntu) + '\n\n'

    open(dirpath + '/reports/full_reports/' + str(date_today) + '_pure_updates.log', "a").write(report)
    open(dirpath + '/reports/to_transfer.log', "a").write(to_re_trans)

    pag += 1
    time.sleep(3)

    # - while loop condition -
    # if the last record is older then the date_limit then it stops
    if record_date < date_limit:
        break

# os.system('/usr/bin/python /home/bootcamp/src/pure_sync_rdm/synchronizer/2_uuid_transmit.py')

