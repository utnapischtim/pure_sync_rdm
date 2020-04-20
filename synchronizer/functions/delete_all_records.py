from functions.delete_record        import delete_record
from functions.general_functions    import add_to_full_report, too_many_rdm_requests_check
from setup                          import dirpath, token_rdm, rdm_api_url_records, wait_429

def delete_all_records(shell_interface):

    rdm_get_all_recods(shell_interface)

    file_data = open(f'{dirpath}/data/all_rdm_records.txt').readlines()
    for line in file_data:
        recid = line.split(' ')[1].strip('\n')
        delete_record(shell_interface, recid)


# -- GET FROM RDM --
def rdm_get_all_recods(shell_interface):
    pag = 1
    pag_size = 1000

    add_to_full_report(f'\n---   ---   ---\nGET FROM RDM\n\nPag size: {pag_size}\n')

    count = 0
    go_on = True
    data_ur = ''
    data_u = ''

    file_name = f'{dirpath}/data/all_rdm_records.txt'

    # Empty all_rdm_records
    open(file_name, 'w').close()

    while go_on == True:

        # REQUEST to RDM
        headers = {
            'Authorization': f'Bearer {token_rdm}',
            'Content-Type': 'application/json',
        }
        params = (
            ('prettyprint', '1'),
            )
        url = f'{rdm_api_url_records}api/records/?sort=mostrecent&size={pag_size}&page={pag}'
        response = shell_interface.requests.get(url, headers=headers, params=params, verify=False)

        add_to_full_report(response)
        open(f"{dirpath}/data/temporary_files/resp_rdm.json", 'wb').write(response.content)

        # If the status_code is 429 (too many requests) then it will wait for some minutes
        too_many_rdm_requests_check(response)

        # if response.status_code == 429:
        #     add_to_full_report('\nToo many RDM requests.. wait {wait_429 / 60} minutes\n')
        #     # If too many requests are submitted to RDM (more then 5000 / hour)
        #     shell_interface.time.sleep(wait_429)

        if response.status_code >= 300:
            add_to_full_report(response.content)
            return False

        else:
            resp_json = shell_interface.json.loads(response.content)

            for i in resp_json['hits']['hits']:
                data_ur += f"{i['metadata']['uuid']} {i['metadata']['recid']}\n"
                data_u  += f"{i['metadata']['uuid']}\n"
                count += 1

            add_to_full_report(f'Pag {str(pag)} - Records {count}')

        if 'next' not in resp_json['links']:
            go_on = False
        
        # shell_interface.time.sleep(3)
        pag += 1
        
    add_to_full_report(f'\n- Tot items: {count} -')
    open(file_name, 'w+').write(data_ur)

    return True
