from setup import *

# -- GET FROM PURE --
def get_from_pure(self):
    try:
        pag = 2
        pag_size = 15
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
            response = self.requests.get(pure_rest_api_url + 'research-outputs', headers=headers, params=params)
            open(self.dirpath + "/reports/resp_pure.json", 'wb').write(response.content)
            resp_json = self.json.loads(response.content)

            # resp_json = open(dirpath + '/reports/resp_pure.json', 'r')             # -- TEMPORARY -- 
            # resp_json = json.load(resp_json)                                            # -- TEMPORARY -- 

            if len(resp_json['items']) == 0:    go_on = False

            #       ---         ---         ---
            for item in resp_json['items']:
                cnt += 1
                uuid_str += item['uuid'] + '\n'

            print(f'Pag {str(pag)} - Records {cnt}')

            go_on = False   # TEMP!!

            self.time.sleep(3)
            pag += 1

        print(f'\n- Tot items: {cnt} -')
        open(self.dirpath + "/reports/full_comparison/pure_uuids.log", 'w+').write(uuid_str)

    except:
        print('\n---   !!!   Error in get_from_pure   !!!   ---\n')