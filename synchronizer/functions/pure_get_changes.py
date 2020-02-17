from setup import *

def pure_get_changes(self):
    # try:
    date = str(self.date.today())

    headers = {
        'Accept': 'application/json',
    }
    params = (
        ('page', '1'),
        ('pageSize', '100'),
        ('apiKey', 'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
    )
    # # PURE get request
    response = self.requests.get('https://pure01.tugraz.at/ws/api/514/changes/' + date, headers=headers, params=params)
    open(self.dirpath + "/reports/resp_pure_changes.json", 'wb').write(response.content)

    print(f'\nPure response: {response}\n')
    if response.status_code >= 300:
        print(response.content)

    resp_json = self.json.loads(response.content)

    # resp_json = open(self.dirpath + '/reports/resp_pure.json', 'r')                  # -- TEMPORARY -- 
    # resp_json = self.json.load(resp_json)                                            # -- TEMPORARY -- 

    uuids = ''
    toDelete_str = ''
    cnt_toDelete = 0
    cnt_toUpdate = 0

    for item in resp_json['items']:

        if 'changeType' not in item:    continue

        if item['changeType'] == 'UPDATE':
            changed_uuid = item['uuid']
            toDel_flag = False
            cnt_toUpdate += 1

            # check if the uuid is already in rdm_uuids_recids.log
            file_name = self.dirpath + "/reports/full_comparison/rdm_uuids_recids.log"
            with open(file_name, 'r') as f:
                lines = f.read().splitlines()
                for line in lines:
                    split = line.split(' ')
                    uuid  = split[0]
                    recid = split[1]
                    if changed_uuid == uuid:
                        cnt_toDelete += 1
                        toDel_flag = True
                        toDelete_str += f'{recid}\n'
                        print(f"{item['changeType']} - {item['uuid']} - To delete old version ({recid})")
            if toDel_flag == False:
                print(f"{item['changeType']} - {item['uuid']}")
                        

            uuids += changed_uuid + '\n'

    print(f"\nRecords to update: {cnt_toUpdate}")
    print(f'To delete: {cnt_toDelete} (Out of date)\n')

    open(self.dirpath + "/reports/to_transfer.log", "a").write(uuids)

    toDel_fileName = self.dirpath + '/reports/to_delete.log'
    open(toDel_fileName, "a").write(toDelete_str)

    # except:
    #     print('Error in get_pure_changes function')


