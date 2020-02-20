from setup                      import *
from functions.rdm_push         import create_invenio_data
from functions.rdm_push_byUuid  import rdm_push_byUuid

def get_pure_by_page(my_prompt, pag_begin, pag_end, pag_size):

    try:
        my_prompt.exec_type = 'by_page'
        my_prompt.cnt_resp = {}
        my_prompt.cnt_errors = 0

        for pag in range(pag_begin, pag_end):

            report_text = f'\nPag {str(pag)} - pag_size {str(pag_size)}\n'
            print(report_text)
            # add page to report file
            report_file = my_prompt.dirpath + "/reports/" + str(my_prompt.date.today()) + "_rdm_push_records.log"     
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
            response = my_prompt.requests.get(pure_rest_api_url + 'research-outputs', headers=headers, params=params)
            open(my_prompt.dirpath + "/reports/temporary_files/resp_pure.json", 'wb').write(response.content)
            resp_json = my_prompt.json.loads(response.content)

            #       ---         ---         ---
            for my_prompt.item in resp_json['items']:
                create_invenio_data(my_prompt)          # Creates data to push to InvenioRDM
            #       ---         ---         ---
                
            # view total number of http respone codes in _rdm_push_records.log
            report_text = 'HTTP response codes:\n'
            for key in my_prompt.cnt_resp:
                report_text += str(key) + ": " + str(my_prompt.cnt_resp[key]) + "\n"
            open(report_file, "a").write(report_text)
            print(report_text)

            # add http reponse codes to yyyy-mm-_rdm_push_pages.log
            date_today = str(my_prompt.date.today())
            report_file = f'{my_prompt.dirpath}/reports/{date_today}_rdm_push_pages.log'

            now = my_prompt.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            report_text = f'\n{str(my_prompt.date.today())} {current_time},\tpag {pag},\tsize {pag_size},\tcodes:\t'
            
            for key in my_prompt.cnt_resp:
                report_text += f'{str(key)}: {str(my_prompt.cnt_resp[key])},\t'
            open(report_file, "a").write(report_text)

            my_prompt.cnt_resp = {}

        if my_prompt.cnt_errors > 0:
            rdm_push_byUuid(my_prompt, 'update')

        print('\n-- -- Finito -- --\n')
    except:
        print('\n- Error in get_pure_by_page method -\n')