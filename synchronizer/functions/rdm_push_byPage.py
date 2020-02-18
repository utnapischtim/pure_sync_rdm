from setup                      import *
from functions.rdm_push         import create_invenio_data
from functions.rdm_push_byUuid  import rdm_push_byUuid

def get_pure_by_page(self, pag_begin, pag_end, pag_size):

    try:
        self.exec_type = 'by_page'
        self.cnt_resp = {}
        self.cnt_errors = 0

        for pag in range(pag_begin, pag_end):

            report_text = f'\nPag {str(pag)} - pag_size {str(pag_size)}\n'
            print(report_text)
            # add page to report file
            report_file = self.dirpath + "/reports/full_reports/" + str(self.date.today()) + "_report.log"     
            open(report_file, "a").write(report_text)                       # 'a' -> append

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
            response = self.requests.get(pure_rest_api_url + 'research-outputs', headers=headers, params=params)
            open(self.dirpath + "/reports/resp_pure.json", 'wb').write(response.content)
            resp_json = self.json.loads(response.content)

            # resp_json = open(self.dirpath + '/reports/resp_pure.json', 'r')             # -- TEMPORARY -- 
            # resp_json = json.load(resp_json)                                            # -- TEMPORARY -- 

            #       ---         ---         ---
            for self.item in resp_json['items']:
                create_invenio_data(self)          # Creates data to push to InvenioRDM
            #       ---         ---         ---
                
            # view total number of http respone codes in report.log
            report_text = 'HTTP response codes:\n'
            for key in self.cnt_resp:
                report_text += str(key) + ": " + str(self.cnt_resp[key]) + "\n"
            open(report_file, "a").write(report_text)
            print(report_text)

            # add http reponse codes to d_rdm_push_report.log
            report_file = self.dirpath + "/reports/d_rdm_push_report.log"
            now = self.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            report_text = f'\n{str(self.date.today())} {current_time},\tpag {pag},\tsize {pag_size},\tcodes:\t'
            for key in self.cnt_resp:
                report_text += f'{str(key)}: {str(self.cnt_resp[key])},\t'
            open(report_file, "a").write(report_text)

            self.cnt_resp = {}

        if self.cnt_errors > 0:
            rdm_push_byUuid(self, 'update')

        print('\n-- -- Finito -- --\n')
    except:
        print('\n- Error in get_pure_by_page method -\n')