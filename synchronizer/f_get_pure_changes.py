from f_full_comparison import *

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
        toDelete_str = ''
        cnt_to_delete = 0

        for item in resp_json['items']:

            if item['changeType'] == 'UPDATE':
                changed_uuid = item['uuid']
                toDel_flag = False

                # check if the uuid is already in rdm_uuids_recids.log
                file_name = dirpath + "/reports/full_comparison/rdm_uuids_recids.log"
                with open(file_name, 'r') as f:
                    lines = f.read().splitlines()
                    for line in lines:
                        split = line.split(' ')
                        uuid  = split[0]
                        recid = split[1]
                        if changed_uuid == uuid:
                            cnt_to_delete += 1
                            toDel_flag = True
                            toDelete_str += f'{recid}\n'
                            print(f"{item['changeType']} - {item['uuid']} - To delete old version ({recid})")
                if toDel_flag == False:
                    print(f"{item['changeType']} - {item['uuid']}")
                            

                uuids += changed_uuid + '\n'

        print('\nRecords to update: ', len(resp_json['items']))
        print(f'To delete: {cnt_to_delete} (Out of date)\n')

        open(dirpath + "/reports/to_transfer.log", "a").write(uuids)

        toDel_fileName = dirpath + '/reports/to_delete.log'
        open(toDel_fileName, "a").write(toDelete_str)

    except:
        print('Error in get_pure_changes function')


inst_fc = FullComparison()
inst_fc.get_from_rdm()
inst_fc.delete_record()

get_pure_changes()

from f_uuid_transfer import uuid_transfer
uuid_transfer('changes')