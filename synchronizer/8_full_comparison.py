import requests
import json
import time
import os
from setup import *
from pprint import pprint


class FullComparison:
    
    def __init__(self):
        # directory path
        self.dirpath = os.path.dirname(os.path.abspath(__file__))

    def get_from_rdm(self):
        try:
            params = (('prettyprint', '1'),)

            pag = 1
            pag_size = 500
            print(f'\n---   ---   ---\nGET FROM RDM\n\nPag size: {pag_size}\n')

            cnt = 0
            go_on = True
            uuid_str = ''

            while go_on == True:

                response = requests.get(
                    f'https://localhost:5000/api/records/?sort=mostrecent&size={pag_size}&page={pag}', 
                    params=params, 
                    verify=False
                    )
                print(response)
                open(self.dirpath + "/reports/resp_rdm.json", 'wb').write(response.content)

                if response.status_code >= 300:
                    print(response.content)
                    exit()

                resp_json = json.loads(response.content)

                for i in resp_json['hits']['hits']:
                    uuid_str += i['metadata']['uuid'] + '\n'
                    cnt += 1

                print(f'Pag {str(pag)} - Records {cnt}')

                if 'next' not in resp_json['links']:
                    go_on = False

                # go_on = False   # TEMP!!
                time.sleep(3)
                pag += 1
                
            print(f'\n- Tot items: {cnt} -')
            open(self.dirpath + "/reports/full_comparison/all_rdm_uuids.log", 'w+').write(uuid_str)

        except:
            print('\nError in get_from_rdm\n')


    def get_from_pure(self):
        try:
            pag = 3
            pag_size = 50
            print(f'\n---   ---   ---\nGET FROM PURE\n\nPag size: {pag_size}\n')

            cnt = 0
            go_on = True
            uuid_str = ''

            while go_on == True:

                headers = {
                    'Accept': 'application/json',
                    'api-key': 'ca2f08c5-8b33-454a-adc4-8215cfb3e088',
                }
                params = (
                    ('page', pag),
                    ('pageSize', pag_size),
                    ('apiKey', 'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
                )
                # PURE get request
                response = requests.get(pure_rest_api_url + 'research-outputs', headers=headers, params=params)
                open(self.dirpath + "/reports/resp_pure.json", 'wb').write(response.content)
                resp_json = json.loads(response.content)

                # resp_json = open(self.dirpath + '/reports/resp_pure.json', 'r')             # -- TEMPORARY -- 
                # resp_json = json.load(resp_json)                                            # -- TEMPORARY -- 

                if len(resp_json['items']) == 0:    go_on = False

                #       ---         ---         ---
                for item in resp_json['items']:
                    cnt += 1
                    uuid_str += item['uuid'] + '\n'

                print(f'Pag {str(pag)} - Records {cnt}')

                go_on = False   # TEMP!!

                time.sleep(3)
                pag += 1

            print(f'\n- Tot items: {cnt} -')
            open(self.dirpath + "/reports/full_comparison/all_pure_uuids.log", 'w+').write(uuid_str)

        except:
            print('\nError in get_from_pure\n')


    def find_missing(self):
        print('\n---   ---   ---\nFIND MISSING\n')
        # Read Pure
        file_name = self.dirpath + '/reports/full_comparison/all_rdm_uuids.log'
        uuid_rdm = open(file_name, 'r').readlines()

        # Read RDM
        file_name = self.dirpath + '/reports/full_comparison/all_pure_uuids.log'
        uuid_pure = open(file_name, 'r').readlines()
            
        # Find missing records
        cnt_m = 0
        cnt_t = 0
        missing_in_rdm = ''
        for i in uuid_pure:
            if i not in uuid_rdm:
                cnt_m += 1
                missing_in_rdm += i
            else:
                cnt_t += 1

        file_name = self.dirpath + '/reports/to_transfer.log'
        open(file_name, "a").write(missing_in_rdm)
        print(f'{cnt_t}\trecords intersect')
        print(f'{cnt_m}\trecords added to to_transfer.log\n')


inst_fc = FullComparison()
inst_fc.get_from_rdm()
inst_fc.get_from_pure()
inst_fc.find_missing()
os.system('/usr/bin/python /home/bootcamp/src/pure_sync_rdm/synchronizer/2_uuid_transmit.py')