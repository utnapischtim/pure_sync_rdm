from setup import *

def delete_record(self):
    # NOTE: the user ACCOUNT related to the used TOKEN must be ADMIN
    # pipenv run invenio roles add admin@invenio.org admin
    try:
        print('\n---   ---   ---\nDELETE RECORDS\n')

        file_name = self.dirpath + '/data/to_delete.txt'

        records_to_del = open(file_name, 'r')

        headers = {
            'Authorization': 'Bearer ' + token_rdm,         # token from setup.py
            'Content-Type': 'application/json',
        }
        recid = records_to_del.readline()
        cnt_success = 0
        cnt_error = 0
        cnt_tot = 0
        deleted_records = []

        while recid:
            cnt_tot += 1
            self.time.sleep(push_dist_sec)
            r_id = recid.strip()

            if len(r_id) != 11:
                print(f'\n{r_id} -> Wrong recid lenght! You can not use uuids.\n')
                continue
            
            url = f'{rdm_api_url_records}{r_id}'
            response = self.requests.delete(url, headers=headers, verify=False)

            recid = records_to_del.readline()
            print(f'{r_id} {response}')
            
            # 410 -> "PID has been deleted"
            if response.status_code < 300 or response.status_code == 410:
                cnt_success += 1
                deleted_records.append(r_id)

                # remove deleted recid from to_delete.log
                with open(file_name, "r") as f:
                    lines = f.readlines()
                with open(file_name, "w") as f:
                    for line in lines:
                        if line.strip("\n") != r_id:
                            f.write(line)

                # remove record from all_rdm_records.log
                file_name = self.dirpath + "/reports/all_rdm_records.log"
                with open(file_name, "r") as f:
                    lines = f.readlines()
                with open(file_name, "w") as f:
                    for line in lines:
                        line_recid = line.strip("\n")
                        line_recid = line_recid.split(' ')[1]
                        if line_recid != r_id:
                            f.write(line)


            elif response.status_code == 429:
                self.time.sleep(wait_429)
            else:
                cnt_error += 1
                print(response.content)

        current_time = self.datetime.now().strftime("%H:%M:%S")
        report = f"\n{current_time}\nDelete - {self.date.today()} - "

        if cnt_tot == 0:
            report += "success\nNothing to trasmit\n"
        else:
            percent_success = cnt_success * 100 / cnt_tot

            if percent_success >= upload_percent_accept:
                report += "success\n"
            else:
                report += "error\n"

            current_time = self.datetime.now().strftime("%H:%M:%S")

        report += f"Tot records: {cnt_tot} - Success transfer: {cnt_success}\n"

        # Remove records from rdm_uuids_recids.log
        file_name = self.dirpath + '/reports/full_comparison/rdm_uuids_recids.log'
        cnt_removed = 0
        with open(file_name, "r") as f:
            lines = f.readlines()
        with open(file_name, "w") as f:
            for line in lines:
                file_rid = line.strip("\n")
                file_rid = file_rid.split(' ')[1]
                if file_rid in deleted_records:
                    cnt_removed += 1
                else:
                    f.write(line)

        print(f'\nRemoved lines from rdm_uuids_recids.log: {cnt_removed}')

        date_today = str(self.date.today())
        open(f'{self.dirpath}/reports/{date_today}_updates.log', "a").write(report)
        
        print(report)

    except:
        print('\n---   !!!   Error in delete_record   !!!   ---\n')