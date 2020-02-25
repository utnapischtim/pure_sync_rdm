from setup                      import *
from functions.rdm_push         import create_invenio_data
from functions.rdm_push_by_uuid  import rdm_push_by_uuid

def get_pure_by_page(my_prompt, pag_begin, pag_end, pag_size):

    # try:
    my_prompt.exec_type = 'by_page'
    my_prompt.count_http_response_codes = {}
    my_prompt.count_errors = 0

    for pag in range(pag_begin, pag_end):

        report_text = f'\nPag {str(pag)} - pag_size {str(pag_size)}\n'
        print(report_text)

        # add page to report file
        report_file = my_prompt.dirpath + "/reports/" + str(my_prompt.date.today()) + "_rdm-push-records.log"     
        open(report_file, "a").write(report_text)                       # 'a' -> append

        # PURE GET REQUEST
        headers = {
            'Accept': 'application/json',
            'api-key': pure_api_key,
        }
        params = (
            ('page', pag),
            ('pageSize', pag_size),
            ('apiKey', pure_api_key),
        )
        response = my_prompt.requests.get(pure_rest_api_url + 'research-outputs', headers=headers, params=params)

        open(my_prompt.dirpath + "/data/temporary_files/resp_pure.json", 'wb').write(response.content)

        # Load json response
        resp_json = my_prompt.json.loads(response.content)

        # Creates data to push to InvenioRDM
        for my_prompt.item in resp_json['items']:
            create_invenio_data(my_prompt)          
        #       ---         ---         ---
            
        # view total number of http respone codes in _rdm-push-records.log
        report_text = 'HTTP response codes:\n'

        for key in my_prompt.count_http_response_codes:
            report_text += f'{key}: {my_prompt.count_http_response_codes[key]}\n'

        open(report_file, "a").write(report_text)
        print(report_text)

        # add http reponse codes to yyyy-mm-_rdm_push_pages.log
        date_today = str(my_prompt.date.today())
        report_file = f'{my_prompt.dirpath}/reports/{date_today}_rdm_push_pages.log'

        now = my_prompt.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        report_text = f'\n{str(my_prompt.date.today())} {current_time},\tpag {pag},\tsize {pag_size},\tcodes:\t'
        
        for key in my_prompt.count_http_response_codes:
            report_text += f'{str(key)}: {str(my_prompt.count_http_response_codes[key])},\t'
            
        open(report_file, "a").write(report_text)

        my_prompt.count_http_response_codes = {}

    if my_prompt.count_errors > 0:
        rdm_push_by_uuid(my_prompt, 'update')

    print('\n-- -- Finito -- --\n')
    # except:
    #     print('\n!!!      !!!  Error in get_pure_by_page method   !!!     !!!\n')