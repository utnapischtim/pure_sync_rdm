from setup import *
from functions.get_from_rdm import get_from_rdm

def pure_get_changes(my_prompt):
    try:
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
        file_name = f'{my_prompt.dirpath}/reports/temporary_files/resp_pure_changes.json'
        open(file_name, 'wb').write(response.content)

        # Load json
        resp_json = my_prompt.json.loads(response.content)

        # Get all RDM uuids and recids
        get_from_rdm(my_prompt)                                  # MAYBE TAKES TOO LONG !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        file_name = my_prompt.dirpath + '/reports/full_comparison/rdm_uuids_recids.log'
        uuidRecid_rdm = open(file_name, 'r').readlines()

        to_delete = ''
        cnt_toDel = 0

        to_transfer = ''
        cnt_toTrans = 0

        for item in resp_json['items']:

            if 'changeType' not in item:    continue
            pure_uuid = item['uuid']
            print(f"{item['changeType']} - {item['uuid']}")

            #   ---     UPDATE      ---
            if item['changeType'] == 'UPDATE':
                cnt_toTrans += 1
                to_transfer += pure_uuid + '\n'

                # Check if older version of the same uuid is in RDM
                toDel_flag = False

                for rdm_record in uuidRecid_rdm:

                    rdm_uuid = rdm_record.split(' ')[0]
                    

                    if pure_uuid == rdm_uuid:
                        rdm_recid = rdm_record.split(' ')[1]
                        
                        to_delete += rdm_recid
                        cnt_toDel += 1
                        toDel_flag = True

                if toDel_flag:
                    print(f"Delete old version - recid: {rdm_recid}")


            #   ---     ADD / CREATE      ---
            if item['changeType'] == 'ADD' or item['changeType'] == 'CREATE':       # REVIEW !!!!!!!!!!! difference between add and create?
                cnt_toTrans += 1
                to_transfer += pure_uuid + '\n'


            #   ---     DELETE      ---
            if item['changeType'] == 'DELETE':                                      # REVIEW !!!!!!!!!!!!!!!!!!!!!!!

                for rdm_record in uuidRecid_rdm:

                    rdm_uuid = rdm_record.split(' ')[0]
                    rdm_recid = rdm_record.split(' ')[1]

                    if pure_uuid == rdm_uuid:
                        
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


