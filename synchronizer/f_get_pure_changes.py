   
def get_pure_changes():
    try:
        import requests
        import json
        import os
        from setup import dirpath
        from datetime import date
        from pprint import pprint  

        date = str(date.today())

        headers = {
            'Accept': 'application/json',
        }
        params = (
            ('page', '1'),
            ('pageSize', '100'),
            ('apiKey', 'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
        )
        # # PURE get request
        response = requests.get('https://pure01.tugraz.at/ws/api/514/changes/' + date, headers=headers, params=params)
        open(dirpath + "/reports/resp_pure_changes.json", 'wb').write(response.content)
        resp_json = json.loads(response.content)

        # resp_json = open(dirpath + '/reports/resp_pure.json', 'r')                  # -- TEMPORARY -- 
        # resp_json = json.load(resp_json)                                            # -- TEMPORARY -- 

        uuids = ''

        for item in resp_json['items']:
            print(f"{item['changeType']} - {item['uuid']}")
            if item['changeType'] == 'UPDATE':
                uuids += item['uuid'] + '\n'

        print('Records to update: ', len(resp_json['items']))

        open(dirpath + "/reports/to_transfer.log", "a").write(uuids)

        from f_uuid_transfer import uuid_transfer
        uuid_transfer('changes')

    except:
        print('Error in get_pure_changes function')
