import requests
import json
import time
import os
from datetime import date, timedelta
from pprint import pprint     

# dirpath = os.path.dirname(os.path.abspath(__file__))

#   PURE GET UPDATES
def pure_get_updates():
    """Help -> Gets from Pure API all records that have the current date as 'modifiedDate'."""

    pag = 1
    pag_size = 25          # is it enough?
    days_span = 4

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
    # PURE get request
    response = requests.get('https://pure01.tugraz.at/ws/api/514/research-outputs', headers=headers, params=params)
    open(dirpath + "/reports/resp_pure.json", 'wb').write(response.content)
    resp_json = json.loads(response.content)

    # resp_json = open(dirpath + '/reports/resp_pure.json', 'r')                  # -- TEMPORARY --
    # resp_json = json.load(resp_json)                                            # -- TEMPORARY --

    date_today = date.today()
    date_limit = str(date_today - timedelta(days=days_span))

    report = f"Today: {date_today}\nDays span: {days_span}\nDate limit: {date_limit}\n"
    to_re_trans = ''

    cnt  = 0
    cntu = 0

    for item in resp_json['items']:
        if 'info' in item:

            cnt += 1

            record_date_time = item['info']['modifiedDate']
            record_date = str(record_date_time.split('T')[0])
            
            if record_date >= date_limit:
                report += item['uuid'] + ' - To update ---\n'
                to_re_trans += item['uuid'] + '\n'
                cntu += 1
            else:
                report += item['uuid'] + ' - ' + record_date + '\n'

    print('\nTot: ' + str(cnt) + ' - To update: ' + str(cntu))
    print("See file '/records/d_check_pure_updates.log'\n")
    report += 'Tot: ' + str(cnt) + ' - To update: ' + str(cntu) + '\n\n'

    open(dirpath + '/../reports/d_check_pure_updates.log', "a").write(report)
    open(dirpath + '/../reports/to_transfer.log', "a").write(to_re_trans)

    # os.system('/usr/bin/python /home/bootcamp/src/pure_sync_rdm/synchronizer/2_reTransmit.py')