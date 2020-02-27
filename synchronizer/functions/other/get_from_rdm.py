from setup import *

# -- GET FROM RDM --
def get_from_rdm(my_prompt):
    try:
        pag = 1
        pag_size = 1000

        print(f'\n---   ---   ---\nGET FROM RDM\n\nPag size: {pag_size}\n')

        count = 0
        go_on = True
        data_ur = ''
        data_u = ''

        while go_on == True:

            # REQUEST to RDM
            params = (('prettyprint', '1'),)
            url = f'{rdm_api_url_records}api/records/?sort=mostrecent&size={pag_size}&page={pag}'
            response = my_prompt.requests.get(url, params=params, verify=False)

            print(response)
            open(my_prompt.dirpath + "/data/temporary_files/resp_rdm.json", 'wb').write(response.content)

            if response.status_code == 429:
                print('\nToo many requests.. wait 15 min\n')
                my_prompt.time.sleep(wait_429)

            elif response.status_code >= 300:
                print(response.content)
                return False

            else:
                resp_json = my_prompt.json.loads(response.content)

                for i in resp_json['hits']['hits']:
                    data_ur += i['metadata']['uuid'] + ' ' + i['metadata']['recid'] + '\n'
                    data_u  += i['metadata']['uuid'] + '\n'
                    count += 1

                print(f'Pag {str(pag)} - Records {count}')

            if 'next' not in resp_json['links']:
                go_on = False
            
            my_prompt.time.sleep(3)
            pag += 1
            
        print(f'\n- Tot items: {count} -')
        open(my_prompt.dirpath + "/data/all_rdm_records.txt", 'w+').write(data_ur)
        # open(my_prompt.dirpath + "/reports/full_comparison/rdm_uuids_recids.log", 'w+').write(data_ur)
        # open(my_prompt.dirpath + "/reports/full_comparison/rdm_uuids.log", 'w+').write(data_u)

        return True

    except:
        print('\n---   !!!   Error in get_from_rdm   !!!   ---\n')