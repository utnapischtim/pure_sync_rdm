from setup import *

def pure_get_changes(my_prompt):
    try:
        from functions.get_from_rdm import get_from_rdm
        from rdm_get_recid import rdm_get_recid
        from functions.delete_record import delete_record

        # empty to_delete.log
        open(my_prompt.dirpath + '/data/to_delete.txt', 'w').close()

        # empty to_transfer.log
        open(my_prompt.dirpath + '/data/to_transfer.txt', 'w').close()
        
        date = str(my_prompt.date.today())

        headers = {
            'Accept': 'application/json',
        }
        params = (
            ('page', '1'),
            ('pageSize', '250'),
            ('apiKey', 'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
        )
        # # PURE get request
        url = f'{pure_rest_api_url}changes/{date}'
        response = my_prompt.requests.get(url, headers=headers, params=params)
        print(f'\nPure response: {response}\n')

        if response.status_code >= 300:
            print(response.content)

        # Write data into resp_pure_changes
        file_name = f'{my_prompt.dirpath}/data/temporary_files/resp_pure_changes.json'
        open(file_name, 'wb').write(response.content)

        # Load response json
        resp_json = my_prompt.json.loads(response.content)

        to_delete = ''
        cnt_toDel = 0

        to_transfer = ''
        cnt_toTrans = 0

        for item in resp_json['items']:

            if 'changeType' not in item:
                continue
            
            uuid = item['uuid']
            print(f"{item['changeType']} - {item['uuid']}")

            #   ---     UPDATE      ---
            if item['changeType'] == 'UPDATE':
                cnt_toTrans += 1
                to_transfer += f'{uuid}\n'

                # Check if older version of the same uuid is in RDM
                recid = rdm_get_recid(my_prompt, uuid)

                open(my_prompt.dirpath + "/data/to_delete.txt", "a").write(f'{recid}\n')
                delete_record(my_prompt)


            #   ---     ADD / CREATE      ---
            if item['changeType'] == 'ADD' or item['changeType'] == 'CREATE':       # REVIEW !!!!!!!!!!! difference between add and create?
                cnt_toTrans += 1
                to_transfer += uuid + '\n'


            #   ---     DELETE      ---
            if item['changeType'] == 'DELETE':                                      # REVIEW !!!!!!!!!!!!!!!!!!!!!!!

                for rdm_record in uuidRecid_rdm:

                    rdm_uuid = rdm_record.split(' ')[0]
                    rdm_recid = rdm_record.split(' ')[1]

                    if uuid == rdm_uuid:
                        
                        to_delete += rdm_recid
                        cnt_toDel += 1
                        print(f'Recid found: {rdm_recid}')


        # to transfer
        print(f"\nRecords to update: {cnt_toTrans}")
        open(my_prompt.dirpath + "/data/to_transfer.txt", "a").write(to_transfer)

        # to delete
        print(f'To delete: {cnt_toDel}\n')
        open(my_prompt.dirpath + '/data/to_delete.txt', "a").write(to_delete)

        # UPDATE
        from functions.rdm_push_byUuid import rdm_push_byUuid
        rdm_push_byUuid(my_prompt, 'update')

        # DELETE
        from functions.delete_record    import delete_record
        delete_record(my_prompt)

    except:
        print('Error in get_pure_changes function')


