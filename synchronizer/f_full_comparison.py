import requests
import json
import os
import time
from datetime   import date, datetime
from setup import *

class FullComparison:
    """     
        - Checks for Pure records that are not in RDM;
        - Push missing records;
        - Checks for duplicate records in RDM;
        - Deletes duplicates
    """    
    def __init__(self):
        # directory path
        self.dirpath = dirpath


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

                response = requests.get(
                    f'https://localhost:5000/api/records/?sort=mostrecent&size={pag_size}&page={pag}', 
                    params=params, 
                    verify=False
                    )
                print(response)
                open(self.dirpath + "/reports/resp_rdm.json", 'wb').write(response.content)

                if response.status_code >= 300:
                    print(response.content)
                    exit()

                resp_json = json.loads(response.content)

                for i in resp_json['hits']['hits']:
                    data_ur += i['metadata']['uuid'] + ' ' + i['metadata']['recid'] + '\n'
                    data_u  += i['metadata']['uuid'] + '\n'
                    cnt += 1

                print(f'Pag {str(pag)} - Records {cnt}')

                if 'next' not in resp_json['links']:
                    go_on = False

                # go_on = False   # TEMP!!
                time.sleep(3)
                pag += 1
                
            print(f'\n- Tot items: {cnt} -')
            open(self.dirpath + "/reports/full_comparison/rdm_uuids_recids.log", 'w+').write(data_ur)
            open(self.dirpath + "/reports/full_comparison/rdm_uuids.log", 'w+').write(data_u)

        except:
            print('\n---   !!!   Error in get_from_rdm   !!!   ---\n')


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
                response = requests.get(pure_rest_api_url + 'research-outputs', headers=headers, params=params)
                open(self.dirpath + "/reports/resp_pure.json", 'wb').write(response.content)
                resp_json = json.loads(response.content)

                # resp_json = open(self.dirpath + '/reports/resp_pure.json', 'r')             # -- TEMPORARY -- 
                # resp_json = json.load(resp_json)                                            # -- TEMPORARY -- 

                if len(resp_json['items']) == 0:    go_on = False

                #       ---         ---         ---
                for item in resp_json['items']:
                    cnt += 1
                    uuid_str += item['uuid'] + '\n'

                print(f'Pag {str(pag)} - Records {cnt}')

                go_on = False   # TEMP!!

                time.sleep(3)
                pag += 1

            print(f'\n- Tot items: {cnt} -')
            open(self.dirpath + "/reports/full_comparison/pure_uuids.log", 'w+').write(uuid_str)

        except:
            print('\n---   !!!   Error in get_from_pure   !!!   ---\n')


    # -- FIND MISSIN --
    def find_missing(self):
        try:
            print('\n---   ---   ---\nFIND MISSING\n')
            # Read RDM
            file_name = self.dirpath + '/reports/full_comparison/rdm_uuids.log'
            uuid_rdm = open(file_name, 'r').readlines()

            # Read Pure
            file_name = self.dirpath + '/reports/full_comparison/pure_uuids.log'
            uuid_pure = open(file_name, 'r').readlines()
                
            # Find missing records
            cnt_m = 0
            cnt_t = 0
            missing_in_rdm = ''
            for i in uuid_pure:
                if i not in uuid_rdm:
                    cnt_m += 1
                    missing_in_rdm += i
                else:
                    cnt_t += 1

            file_name = self.dirpath + '/reports/to_transfer.log'
            open(file_name, "a").write(missing_in_rdm)
            print(f'{cnt_t}\trecords intersect')
            print(f'{cnt_m}\trecords added to to_transfer.log\n')

        except:
            print('\n---   !!!   Error in find_missing   !!!   ---\n')


    # -- FIND RDM DUPLICATES --
    def find_rdm_duplicates(self):
        try:
            print('---   ---   ---\nFIND RDM DUPLICATES\n\nDuplicates:\n')

            # Read Pure
            file_name = self.dirpath + '/reports/full_comparison/rdm_uuids.log'
            uuid_rdm = open(file_name, 'r').readlines()
            # Read Pure
            file_name = self.dirpath + '/reports/full_comparison/rdm_uuids_recids.log'
            uuidRecid_rdm = open(file_name, 'r').readlines()
            # empty to_delete.log
            toDel_fileName = self.dirpath + '/reports/to_delete.log'
            open(toDel_fileName, 'w').close()                         

            temp_arr = []
            cnt = 0
            dup_recid = []

            for uuid in uuid_rdm:
                cnt_dup = 0
                if uuid not in temp_arr:        # not duplicated
                    temp_arr.append(uuid)
                else:                           # duplicated
                    # find the corresponding recid to the duplicated uuid
                    for i in uuidRecid_rdm:
                        split = i.split(' ')
                        uuid = uuid.split('\n')[0]
                        recid = split[1]

                        if split[0] == uuid:
                            cnt_dup += 1
                            if recid not in dup_recid and cnt_dup > 1:
                                ri = recid.split('\n')[0]
                                print(f"{uuid}\t{ri}")
                                dup_recid.append(recid)
                                cnt += 1

            if cnt == 0:
                print('- There are no duplicates\n')
                report = f"\nDelete - {date.today()} - success\nThere are no duplicates\n"
                open(self.dirpath + '/reports/d_daily_updates.log', "a").write(report)
                exit

            else:
                print(f'\nTot {cnt} duplicates\n')

                dup_recid_str = ''
                for i in dup_recid:
                    dup_recid_str += i

                open(toDel_fileName, "a").write(dup_recid_str)

                self.delete_record()

        except:
            print('\n---   !!!   Error in find_rdm_duplicates   !!!   ---\n')

    
    # -- DELETE RECOD --
    def delete_record(self):
        # NOTE: the user ACCOUNT related to the used TOKEN must be ADMIN
        # pipenv run invenio roles add admin@invenio.org admin
        try:
            print('\n---   ---   ---\nDELETE RECORDS\n')

            file_name = self.dirpath + '/reports/to_delete.log'

            lines_start = sum(1 for line in open(file_name))    # count lines

            records_to_del = open(file_name, 'r')

            headers = {
                'Authorization': 'Bearer ' + token_rdm,         # token from setup.py
                'Content-Type': 'application/json',
            }
            record_id = records_to_del.readline()
            cnt_success = 0
            cnt_error = 0
            cnt_tot = 0

            while record_id:
                cnt_tot += 1
                time.sleep(1)
                r_id = record_id.strip()

                if len(r_id) != 11:
                    print(f'\n{r_id} -> Wrong recid lenght! You can not use uuids.\n')
                    continue

                response = requests.delete('https://127.0.0.1:5000/api/records/' + r_id, headers=headers, verify=False)

                record_id = records_to_del.readline()
                print(f'{r_id} {response}')
                
                if response.status_code < 300 or response.status_code == 410:
                    cnt_success += 1
                    # remove deleted record_id
                    with open(file_name, "r") as f:
                        lines = f.readlines()
                    with open(file_name, "w") as f:
                        for line in lines:
                            if line.strip("\n") != r_id:
                                f.write(line)
                else:
                    cnt_error += 1
                    print(response.content)

            lines_end = sum(1 for line in open(file_name))    # count lines

            current_time = datetime.now().strftime("%H:%M:%S")
            report = f"\n{current_time}\nDelete - {date.today()} - "

            if cnt_tot == 0:
                report += "success\nNothing to trasmit\n"
            else:
                percent_success = cnt_success * 100 / cnt_tot

                if percent_success >= upload_percent_accept:
                    report += "success\n"
                else:
                    report += "error\n"

                current_time = datetime.now().strftime("%H:%M:%S")

            report += f"Tot records: {cnt_tot} - Success transfer: {cnt_success}\n"
            report += f"Lines start: {lines_start} - Lines end: {lines_end}\n"
                
            open(self.dirpath + '/reports/d_daily_updates.log', "a").write(report)
            print(report)

        except:
            print('\n---   !!!   Error in delete_record   !!!   ---\n')


# inst_fc = FullComparison()

# inst_fc.get_from_rdm()
# inst_fc.get_from_pure()
# inst_fc.find_missing()
# os.system('/usr/bin/python /home/bootcamp/src/pure_sync_rdm/synchronizer/2_uuid_transmit.py')

# inst_fc.find_rdm_duplicates()
# inst_fc.delete_record()