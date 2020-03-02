from setup                          import *
from functions.rdm_push_record      import create_invenio_data
from functions.rdm_push_by_uuid     import rdm_push_by_uuid
from functions.general_functions    import give_spaces

def get_pure_by_page(my_prompt, pag_begin, pag_end, pag_size):

    for pag in range(pag_begin, pag_end):

        date_today = my_prompt.date.today()

        my_prompt.count_total                       = 0
        my_prompt.count_errors_push_metadata        = 0
        my_prompt.count_errors_put_file             = 0
        my_prompt.count_errors_record_delete        = 0
        my_prompt.count_successful_push_metadata    = 0
        my_prompt.count_successful_push_file        = 0
        my_prompt.count_successful_record_delete    = 0
        my_prompt.count_uuid_not_found_in_pure      = 0

        report  = '\n\n--   --   --\n'
        report += f'\nPag {str(pag)} - pag_size {str(pag_size)}'

        # add page to report file  
        file_records = f'{my_prompt.dirpath}/reports/{date_today}_records.log'
        open(file_records, "a").write(report)
        print(report)

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

        #       ---         ---         ---
        # Creates data to push to InvenioRDM
        for my_prompt.item in resp_json['items']:
            print('')                       # adds new line in the console
            create_invenio_data(my_prompt)          
        #       ---         ---         ---

        # Add RDM HTTP reponse codes to yyyy-mm-dd_pages.log
        file_pages = f'{my_prompt.dirpath}/reports/{date_today}_pages.log'

        metadata_success  = give_spaces(my_prompt.count_successful_push_metadata)
        metadata_error    = give_spaces(my_prompt.count_errors_push_metadata)
        file_success      = give_spaces(my_prompt.count_successful_push_file)
        file_error        = give_spaces(my_prompt.count_errors_put_file)

        report = f'\nPage {give_spaces(pag)} - Page size {give_spaces(pag_size)} - '
        report += f'Metadata: success {metadata_success}, error {metadata_error} -\t'
        report += f'Files: success {file_success}, error {file_error}'

        open(file_pages, "a").write(report)

        file_summary = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_summary.log'
        open(file_summary, "a").write(f'\n\n\nPage: {pag} - Page size: {pag_size}')

        # summary.log and records.log
        from functions.general_functions import report_records_summary
        report_records_summary(my_prompt, 'Pages')
