import requests
import json
import time
from datetime import date, timedelta
from pprint import pprint     

def check_pure_updates(days_span, dirpath):
    
    pag = 1
    while True:

        headers = {
            'Accept': 'application/json',
        }
        params = (
            ('order', 'modified'),
            ('orderBy', 'descending'),
            ('page', pag),                      # page
            ('pageSize', 250),                  # records per page
            ('apiKey', 'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
        )
        # PURE get request
        response = requests.get('https://pure01.tugraz.at/ws/api/514/research-outputs', headers=headers, params=params)
        print('Pure resp: ', response)
        open(dirpath + "/reports/resp_pure.json", 'wb').write(response.content)
        resp_json = json.loads(response.content)

        date_today = date.today()
        date_limit = str(date_today - timedelta(days=days_span))

        report = f"Today: {date_today}\nDays span: {days_span}\nDate limit: {date_limit}\n"
        print(report)
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

        open(dirpath + '/reports/d_check_pure_updates.log', "a").write(report)
        open(dirpath + '/reports/to_transfer.log', "a").write(to_re_trans)

        pag += 1
        time.sleep(3)

        # - while loop condition -
        # if the last record is older then the date_limit then it stops
        if record_date < date_limit:
            break

    # os.system('/usr/bin/python /home/bootcamp/src/pure_sync_rdm/synchronizer/2_reTransmit.py')


days_span = 6
check_pure_updates(days_span)