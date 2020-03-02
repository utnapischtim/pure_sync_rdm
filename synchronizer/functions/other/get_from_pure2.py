from setup import *

# -- GET FROM PURE --
def get_from_pure(my_prompt):
    try:
        pag = 1
        pag_size = 25
        print(f'\n---   ---   ---\nGET FROM PURE\n\nPag size: {pag_size}\n')

        cnt = 0
        go_on = True
        uuid_str = ''

        while go_on == True:

            headers = {
                'Accept': 'application/json',
                'api-key': pure_api_key,
            }
            params = (
                ('page', pag),
                ('pageSize', pag_size),
                ('apiKey', pure_api_key),
            )
            # PURE get request
            response = my_prompt.requests.get(pure_rest_api_url + 'research-outputs', headers=headers, params=params)
            open(my_prompt.dirpath + "/data/temporary_files/resp_pure.json", 'wb').write(response.content)
            resp_json = my_prompt.json.loads(response.content)

            if len(resp_json['items']) == 0:    go_on = False

            #       ---         ---         ---
            for item in resp_json['items']:
                cnt += 1
                uuid_str += item['uuid'] + '\n'

            print(f'Pag {str(pag)} - Records {cnt}')

            if pag >= 2:               # TEMP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                go_on = False          # TEMP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            my_prompt.time.sleep(3)
            pag += 1

        print(f'\n- Tot items: {cnt} -')
        open(my_prompt.dirpath + "/reports/full_comparison/pure_uuids.log", 'w+').write(uuid_str)

    except:
        print('\n---   !!!   Error in get_from_pure   !!!   ---\n')