from setup import *

def rdm_push_byUuid(self, transfer_type):
    try:
        # date time in yyyy-mm-dd_rdm_push_records.log
        current_time = self.datetime.now().strftime("%H:%M:%S")
        report = f"\n{str(self.date.today())} - {current_time}\n"
        filename = self.dirpath + "/reports/" + str(self.date.today()) + "_rdm_push_records.log"
        open(filename, "a").write(report)

        # read to_transfer.log
        retrans_data = open(self.dirpath + '/data/to_transfer.txt', 'r')
        
        uuid = retrans_data.readline()

        self.cnt_resp = {}
        cnt_tot = 0
        cnt_true = 0
        
        while uuid:
            cnt_tot += 1
                        
            if (len(uuid.strip()) < 36):
                print('Invalid uuid. Too short\n')
                uuid = retrans_data.readline()
                continue

            response = get_pure_by_id(self, uuid.strip())

            if response == True:        cnt_true += 1
            
            uuid = retrans_data.readline()

        print('\n---------------------')
        if transfer_type == '':
            if cnt_tot == 0:
                print("Nothing to trasmit\n")
            else:
                print(f"Tot records: {cnt_tot} - Success transfer: {cnt_true}\n")

        else:
            if transfer_type == 'full_comp':
                report = f"\nFull comparison - {self.date.today()} - "

            elif transfer_type == 'update':
                report = f"\nUpdate - {self.date.today()} - "

            elif transfer_type == 'changes':
                report = f"\nChanges - {self.date.today()} - "

            if cnt_tot == 0:
                report += "success\nNothing to trasmit\n"
            else:
                percent_success = cnt_true * 100 / cnt_tot

                if percent_success >= upload_percent_accept:
                    report += "success\n"
                else:
                    report += "error\n"

                current_time = self.datetime.now().strftime("%H:%M:%S")
                report += f"{current_time}\nTot records: {cnt_tot} - Success transfer: {cnt_true}\n"
            
            # Adds report to yyyy-mm-dd_updates.log
            date_today = str(self.date.today())
            file_name = f'{self.dirpath}/reports/{date_today}_updates.log'
            open(file_name, "a").write(report)

            print(report)

    except:
        print('\n!!!   !!!   ERROR in rdm_push_byUuid   !!!   !!!\n')



def get_pure_by_id(self, uuid):
    
    try:
        from functions.rdm_push import create_invenio_data
        self.exec_type = 'by_id'
        
        headers = {
            'Accept': 'application/json',
            'api-key': pure_api_key,
        }
        params = (
            ('apiKey', pure_api_key),
        )
        response = self.requests.get(pure_rest_api_url + 'research-outputs/' + uuid, headers=headers, params=params)
        print('Pure response: ', response)
        if response.status_code >= 300:
            print(response.content)
            raise Exception

        open(self.dirpath + "/reports/temporary_files/resp_pure.json", 'wb').write(response.content)
        self.item = self.json.loads(response.content)
        
        # Creates data to push to InvenioRDM
        return create_invenio_data(self)

    except:
        print('\n!!!   !!!   ERROR in get_pure_by_id method   !!!   !!!\n')