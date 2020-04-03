from functions.delete_record    import delete_record
from setup                      import *

def delete_all_records(shell_interface):

    rdm_get_all_recods(shell_interface)

    file_data = open(f'{shell_interface.dirpath}/data/all_rdm_records.txt').readlines()
    for line in file_data:
        recid = line.split(' ')[1].strip('\n')
        delete_record(shell_interface, recid)


# -- GET FROM RDM --
def rdm_get_all_recods(shell_interface):
    try:
        pag = 1
        pag_size = 1000

        print(f'\n---   ---   ---\nGET FROM RDM\n\nPag size: {pag_size}\n')

        count = 0
        go_on = True
        data_ur = ''
        data_u = ''

        file_name = f'{shell_interface.dirpath}/data/all_rdm_records.txt'

        # Empty all_rdm_records
        open(file_name, 'w').close()

        while go_on == True:

            # REQUEST to RDM
            params = (('prettyprint', '1'),)
            url = f'{rdm_api_url_records}api/records/?sort=mostrecent&size={pag_size}&page={pag}'
            response = shell_interface.requests.get(url, params=params, verify=False)

            print(response)
            open(shell_interface.dirpath + "/data/temporary_files/resp_rdm.json", 'wb').write(response.content)

            if response.status_code == 429:
                print('\nToo many requests.. wait 15 min\n')
                shell_interface.time.sleep(wait_429)

            elif response.status_code >= 300:
                print(response.content)
                return False

            else:
                resp_json = shell_interface.json.loads(response.content)

                for i in resp_json['hits']['hits']:
                    data_ur += i['metadata']['uuid'] + ' ' + i['metadata']['recid'] + '\n'
                    data_u  += i['metadata']['uuid'] + '\n'
                    count += 1

                print(f'Pag {str(pag)} - Records {count}')

            if 'next' not in resp_json['links']:
                go_on = False
            
            shell_interface.time.sleep(3)
            pag += 1
            
        print(f'\n- Tot items: {count} -')
        open(file_name, 'w+').write(data_ur)

        return True

    except:
        print('\n---   !!!   Error in get_from_rdm   !!!   ---\n')