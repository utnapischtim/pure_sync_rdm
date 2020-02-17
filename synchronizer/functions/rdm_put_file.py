from setup import *


def rdm_put_file(self, file_name):
    try:
        file_path = self.dirpath + '/tmp_files/'
        cnt = 0
        
        # GET from RDM recid of last added record
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
                recid       = i['metadata']['recid']
                record_uuid = i['metadata']['uuid']
                print(f'Adding FILE number {cnt} to recid {recid}')
            
            if self.uuid == record_uuid or cnt > 10:
                break
        if cnt > 10:    print('Having troubles getting the recid of the newly added record\n')

        # - PUT FILE TO RDM -
        headers = {
            'Content-Type': 'application/octet-stream',
        }
        data = open(file_path + file_name, 'rb').read()
        response = self.requests.put('https://127.0.0.1:5000/api/records/' + recid + '/files/' + file_name, headers=headers, data=data, verify=False)

        # Report
        report = ''
        print(f'Transf to RDM: {response}\n')
        report += 'FileTransf ' + str(response) + ' - ' + str(recid) + '\n'

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


    except:
        print('\n- Error in rdm_put_file method -\n')
