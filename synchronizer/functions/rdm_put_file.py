from setup import *

def rdm_put_file(self, file_name):
    try:
        file_path = self.dirpath + '/tmp_files/'

        # GET from RDM recid of last added record
        get_record_recid(self)

        # - PUT FILE TO RDM -
        headers = {
            'Content-Type': 'application/octet-stream',
        }
        data = open(file_path + file_name, 'rb').read()
        url = 'https://127.0.0.1:5000/api/records/' + self.recid + '/files/' + file_name
        response = self.requests.put(url, headers=headers, data=data, verify=False)

        # Report
        report = ''
        print(f'RDM file put: {response}\n')
        report += 'FileTransf ' + str(response) + ' - ' + str(self.recid) + '\n'

        if response.status_code >= 300:
            report += str(response.content) + '\n'

            # metadata transmission success flag
            self.file_success = False
        else:
            self.file_success = True

            # # if the upload was successful then delete file from /tmp_files
            self.os.remove(file_path + file_name) 

        filename = self.dirpath + "/reports/full_reports/" + str(self.date.today()) + "_report.log"
        open(filename, "a").write(report)
        return response.status_code

        # HAVING PURE ADMIN ACCOUNT REMOVE FILE FROM PURE

    except:
        print('\n- Error in rdm_put_file method -\n')


def get_record_recid(self):
    try:
        # GET from RDM recid of last added record
        cnt = 0
        while True:
            cnt += 1
            self.time.sleep(cnt * 2)
            response = self.requests.get(
                'https://localhost:5000/api/records/?sort=mostrecent&size=1&page=1', 
                params=(('prettyprint', '1'),), 
                verify=False
                )
            resp_json = self.json.loads(response.content)

            for i in resp_json['hits']['hits']:
                self.recid  = i['metadata']['recid']
                rdm_uuid    = i['metadata']['uuid']
            
            if self.uuid == rdm_uuid:
                print(f'Found recid: {self.recid}')
                break
            elif cnt > 10:
                print('Having troubles getting the recid of the newly added record\n')
                break
    except:
        print('\n!!!    !!!  Error in get_record_recid method   !!!       !!!\n')
 