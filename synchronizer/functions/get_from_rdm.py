from setup import *

# -- GET FROM RDM --
def get_from_rdm(self):
    try:
        params = (('prettyprint', '1'),)

        pag = 1
        pag_size = 250
        print(f'\n---   ---   ---\nGET FROM RDM\n\nPag size: {pag_size}\n')

        cnt = 0
        go_on = True
        data_ur = ''
        data_u = ''

        while go_on == True:

            response = self.requests.get(
                f'https://localhost:5000/api/records/?sort=mostrecent&size={pag_size}&page={pag}', 
                params=params, 
                verify=False
                )
            print(response)
            open(self.dirpath + "/reports/resp_rdm.json", 'wb').write(response.content)

            if response.status_code >= 300:
                print(response.content)
                exit()

            resp_json = self.json.loads(response.content)

            for i in resp_json['hits']['hits']:
                data_ur += i['metadata']['uuid'] + ' ' + i['metadata']['recid'] + '\n'
                data_u  += i['metadata']['uuid'] + '\n'
                cnt += 1

            print(f'Pag {str(pag)} - Records {cnt}')

            if 'next' not in resp_json['links']:
                go_on = False

            # go_on = False   # TEMP!!
            self.time.sleep(3)
            pag += 1
            
        print(f'\n- Tot items: {cnt} -')
        open(self.dirpath + "/reports/full_comparison/rdm_uuids_recids.log", 'w+').write(data_ur)
        open(self.dirpath + "/reports/full_comparison/rdm_uuids.log", 'w+').write(data_u)

    except:
        print('\n---   !!!   Error in get_from_rdm   !!!   ---\n')