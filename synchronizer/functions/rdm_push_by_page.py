from setup                          import *
from functions.rdm_push_record      import create_invenio_data
from functions.rdm_push_by_uuid     import rdm_push_by_uuid
from functions.general_functions    import add_spaces, initialize_count_variables


def get_pure_by_page(shell_interface, pag_begin: int, pag_end: int, pag_size: int):

    for pag in range(pag_begin, pag_end):

        date_today = shell_interface.date.today()
        current_time = shell_interface.datetime.now().strftime("%H:%M:%S")
        shell_interface.count_http_responses = {}

        initialize_count_variables(shell_interface)

        # add page to report file  
        report  = f'\n\n--   --   --\n\nPag {str(pag)} - pag_size {str(pag_size)}\n\n'
        file_records = f'{shell_interface.dirpath}/reports/{date_today}_records.log'
        open(file_records, "a").write(report)

        print(f'--   --   --\n\nPag {str(pag)} - pag_size {str(pag_size)}')

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

        file_name = f'{shell_interface.dirpath}/data/temporary_files/pure_get_uuid_metadata.json'
        open(file_name, 'wb').write(response.content)

        # (500 -> internal server error)
        if response.status_code >= 300:
            print(response.content)
            shell_interface.time.sleep(180)
            continue

        # Load json response
        resp_json = shell_interface.json.loads(response.content)

        #       ---         ---         ---
        # Creates data to push to RDM
        for shell_interface.item in resp_json['items']:
            print('')                                   # adds new line in the console
            create_invenio_data(shell_interface)          
        #       ---         ---         ---

        http_response_str = 'HTTP responses -> '
        for key in shell_interface.count_http_responses:
            http_response_str += f'{key}: {shell_interface.count_http_responses[key]}, '
        http_response_str = http_response_str[:-2]

        metadata_success  = add_spaces(shell_interface.count_successful_push_metadata)
        metadata_error    = add_spaces(shell_interface.count_errors_push_metadata)
        file_success      = add_spaces(shell_interface.count_successful_push_file)
        file_error        = add_spaces(shell_interface.count_errors_put_file)
        count_abstracts   = add_spaces(shell_interface.count_abstracts)
        count_orcids      = add_spaces(shell_interface.count_orcids)
        pag_log           = add_spaces(pag)
        pag_size_log      = add_spaces(pag_size)

        # Summary added to pages.log
        report = f"""
{current_time} - Page{pag_log} - Size{pag_size_log} - \
Metadata (ok{metadata_success},error {metadata_error}) - \
File (ok{file_success}, error{file_error}) - \
Abstracts:{count_abstracts} - Orcids:{count_orcids} - \
{http_response_str}\
"""
        file_pages = f'{shell_interface.dirpath}/reports/{date_today}_pages.log'
        open(file_pages, "a").write(report)

        # Summary added to records.log
        report = f"""
Metadata success: {metadata_success}, metadata errors: {metadata_error}
Files success:    {file_success}, files errors:    {file_error}
Abstracts:        {count_abstracts}, Orcids:          {count_orcids}

{http_response_str}"""
        file_records = f'{shell_interface.dirpath}/reports/{date_today}_records.log'
        open(file_records, "a").write(report)

        print(report + '\n')