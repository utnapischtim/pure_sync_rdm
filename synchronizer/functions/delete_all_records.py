from functions.delete_record    import delete_from_list
from setup                      import *

def delete_all_records(shell_interface):

    # get_from_rdm(shell_interface)

    file_name = shell_interface.dirpath + "/data/all_rdm_records.txt"
    toDelete_str = ''

    with open(file_name, 'r') as f:
        lines = f.read().splitlines()
        
        for line in lines:
            recid = line.split(' ')[1]
            toDelete_str += f'{recid}\n'
    
    toDel_fileName = shell_interface.dirpath + '/data/to_delete.txt'
    open(toDel_fileName, "a").write(toDelete_str)

    delete_from_list(shell_interface)



# -- GET FROM RDM --
def get_from_rdm(shell_interface):
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
        open(shell_interface.dirpath + "/data/all_rdm_records.txt", 'w+').write(data_ur)

        return True

    except:
        print('\n---   !!!   Error in get_from_rdm   !!!   ---\n')