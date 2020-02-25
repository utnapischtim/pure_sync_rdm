from setup                      import *
from functions.rdm_push         import create_invenio_data
from functions.rdm_push_by_uuid  import rdm_push_by_uuid

def get_pure_by_page(my_prompt, pag_begin, pag_end, pag_size):

    # try:
    my_prompt.exec_type = 'by_page'

    for pag in range(pag_begin, pag_end):

        my_prompt.count_http_response_codes = {}

        my_prompt.count_total = 0
        my_prompt.count_errors_push_metadata = 0
        my_prompt.count_errors_put_file = 0
        my_prompt.count_successful_push_metadata = 0
        my_prompt.count_successful_push_file = 0
        my_prompt.count_uuid_not_found_in_pure = 0

        report = f'\nPag {str(pag)} - pag_size {str(pag_size)}\n'
        print(report)

        # add page to report file
        file_records = my_prompt.dirpath + "/reports/" + str(my_prompt.date.today()) + "_rdm-push-records.log"     
        open(file_records, "a").write(report)                       # 'a' -> append

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

        # Add RDM HTTP reponse codes to yyyy-mm-_rdm_push_pages.log
        file_pages = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_rdm_push_pages.log'

        current_time = my_prompt.datetime.now().strftime("%H:%M:%S")
        report = f'\n{str(my_prompt.date.today())} {current_time},\tpag {pag},\tsize {pag_size},\tcodes:\t'
        
        for key in my_prompt.count_http_response_codes:
            report += f'{str(key)}: {my_prompt.count_http_response_codes[key]},\t'

        open(file_pages, "a").write(report)

        # summary.log and records.log
        from functions.report_records_summary import report_records_summary
        report_records_summary(my_prompt, 'Pages')


    # except:
    #     print('\n!!!      !!!  Error in get_pure_by_page method   !!!     !!!\n')