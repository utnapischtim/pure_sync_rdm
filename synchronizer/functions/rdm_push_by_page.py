from setup                          import *
from functions.rdm_push_record      import create_invenio_data
from functions.rdm_push_by_uuid     import rdm_push_by_uuid
from functions.general_functions    import add_spaces, report_records_summary, initialize_count_variables


def get_pure_by_page(shell_interface, pag_begin, pag_end, pag_size):

    for pag in range(pag_begin, pag_end):

        date_today = shell_interface.date.today()

        initialize_count_variables(shell_interface)

        report  = '\n\n--   --   --\n'
        report += f'\nPag {str(pag)} - pag_size {str(pag_size)}'

        # add page to report file  
        file_records = f'{shell_interface.dirpath}/reports/{date_today}_records.log'
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
        url = f'{pure_rest_api_url}research-outputs'
        response = shell_interface.requests.get(url, headers=headers, params=params)

        file_name = f'{shell_interface.dirpath}/data/temporary_files/resp_pure.json'
        open(file_name, 'wb').write(response.content)

        # Load json response
        resp_json = shell_interface.json.loads(response.content)

        #       ---         ---         ---
        # Creates data to push to InvenioRDM
        for shell_interface.item in resp_json['items']:
            print('')                       # adds new line in the console
            create_invenio_data(shell_interface)          
        #       ---         ---         ---

        # Add RDM HTTP reponse codes to yyyy-mm-dd_pages.log
        file_pages = f'{shell_interface.dirpath}/reports/{date_today}_pages.log'

        metadata_success  = add_spaces(shell_interface.count_successful_push_metadata)
        metadata_error    = add_spaces(shell_interface.count_errors_push_metadata)
        file_success      = add_spaces(shell_interface.count_successful_push_file)
        file_error        = add_spaces(shell_interface.count_errors_put_file)

        report = f'\nPage {add_spaces(pag)} - Page size {add_spaces(pag_size)} - '
        report += f'Metadata: success {metadata_success}, error {metadata_error} -\t'
        report += f'Files: success {file_success}, error {file_error}'
        
        open(file_pages, "a").write(report)

        file_summary = f'{shell_interface.dirpath}/reports/{shell_interface.date.today()}_summary.log'
        open(file_summary, "a").write(f'\n\n\nPage: {pag} - Page size: {pag_size}')

        # summary.log and records.log
        report_records_summary(shell_interface, 'Pages')
