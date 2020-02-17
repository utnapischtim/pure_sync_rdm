from setup import *

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
            self.time.sleep(1)
            r_id = record_id.strip()

            if len(r_id) != 11:
                print(f'\n{r_id} -> Wrong recid lenght! You can not use uuids.\n')
                continue

            response = self.requests.delete('https://127.0.0.1:5000/api/records/' + r_id, headers=headers, verify=False)

            record_id = records_to_del.readline()
            print(f'{r_id} {response}')
            
            # 410 -> "PID has been deleted"
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
        report += f"Lines start: {lines_start} - Lines end: {lines_end}\n"
            
        open(self.dirpath + '/reports/d_daily_updates.log', "a").write(report)
        print(report)

    except:
        print('\n---   !!!   Error in delete_record   !!!   ---\n')