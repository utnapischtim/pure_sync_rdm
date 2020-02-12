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

        params = (('prettyprint', '1'),)

        pag = 1
        pag_size = 250

        cnt = 0
        go_on = True
        uuid_str = ''
        recid_str = ''

        while go_on == True:

            response = requests.get(
                f'https://localhost:5000/api/records/?sort=mostrecent&size={pag_size}&page={pag}', 
                params=params, 
                verify=False
                )
            open(self.dirpath + "/reports/resp_rdm.json", 'wb').write(response.content)
            print(response)

            if response.status_code >= 300:
                print(response.content)
                exit()

            resp_json = json.loads(response.content)

            for i in resp_json['hits']['hits']:
                pprint(i['metadata']['uuid'])
                uuid_str += i['metadata']['uuid'] + '\n'
                recid_str += i['metadata']['recid'] + '\n'
                cnt += 1

            if 'next' not in resp_json['links']:
                print('\n- End\nNo more pages available')
                print(f'- Total records: {cnt}\n')
                go_on = False

            time.sleep(3)
            pag += 1
            
        open(self.dirpath + "/reports/full_comparison/all_rdm_uuids.log", 'w+').write(uuid_str)
        open(self.dirpath + "/reports/full_comparison/all_rdm_recids.log", 'w+').write(recid_str)


    def get_from_pure(self):
        try:
            pag = 1
            pag_size = 50
            print(f'Pag size: {pag_size}\n')

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

                time.sleep(3)
                pag += 1

            print(f'\n- Tot items: {cnt} -')
            open(self.dirpath + "/reports/full_comparison/all_pure_uuids.log", 'w+').write(uuid_str)

        except:
            print('\nError in get_from_pure\n')


    def find_missing(self):

        # Read Pure
        file_name = self.dirpath + '/reports/full_comparison/t_pure.log'
        uuid_pure = open(file_name, 'r').readlines()

        # Read RDM
        file_name = self.dirpath + '/reports/full_comparison/t_rdm.log'
        uuid_rdm = open(file_name, 'r').readlines()
            
        # Find missing records
        cnt = 0
        missing_in_rdm = ''
        for i in uuid_pure:
            if i not in uuid_rdm:
                cnt += 1
                missing_in_rdm += i

        file_name = self.dirpath + '/reports/to_transfer.log'
        open(file_name, "a").write(missing_in_rdm)
        print(f'\n{cnt} records added to to_transfer.log\n')


inst_fc = FullComparison()
inst_fc.find_missing()