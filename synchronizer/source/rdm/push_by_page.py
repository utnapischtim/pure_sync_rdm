import json
from datetime                       import date, datetime
from setup                          import pure_rest_api_url, log_files_name
from source.general_functions       import dirpath, add_spaces, add_to_full_report, initialize_counters
from source.pure.general_functions  import pure_get_metadata
from source.rdm.add_record          import RdmAddRecord
from source.reports                 import Reports

# reports = Reports()
# reports.get_report_template('intro_title', 'some tittttle')

class RunPages:

    def __init__(self):
        self.reports = Reports()

        
    def get_pure_by_page(self, pag_begin: int, pag_end: int, pag_size: int):

        rdm_add_record = RdmAddRecord()

        for pag in range(pag_begin, pag_end):
    
            self.global_counters = initialize_counters()

            current_time = datetime.now().strftime("%H:%M:%S")

            # Report intro
            self.reports.get_report_template(['records', 'records_full'], 'intro_title', [current_time, 'PAGES'])
            self.reports.get_report_template(['records', 'records_full'], 'page_and_size', [pag, pag_size])

            # Pure get request
            params = {
                'page': pag,
                'pageSize': pag_size
            }
            response = pure_get_metadata('research-outputs', '', params)

            # Load json response
            resp_json = json.loads(response.content)

            #       ---         ---         ---
            # Creates data to push to RDM
            for item in resp_json['items']:

                add_to_full_report('')          # adds new line in the console
                rdm_add_record.create_invenio_data(self.global_counters, item)
            #       ---         ---         ---

            http_response_str = 'HTTP responses -> '
            for key in self.global_counters['http_responses']:
                http_response_str += f"{key}: {self.global_counters['http_responses'][key]}, "
            http_response_str = http_response_str[:-2]

            metadata_success  = add_spaces(self.global_counters['successful_push_metadata'])
            metadata_error    = add_spaces(self.global_counters['errors_push_metadata'])
            file_success      = add_spaces(self.global_counters['successful_push_file'])
            file_error        = add_spaces(self.global_counters['errors_put_file'])
            count_abstracts   = add_spaces(self.global_counters['abstracts'])
            count_orcids      = add_spaces(self.global_counters['orcids'])
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
            file_pages = log_files_name['pages']
            open(file_pages, "a").write(report)

            # Summary added to records.log
            report = f"""
Metadata success: {metadata_success}, metadata errors: {metadata_error}
Files success:    {file_success}, files errors:    {file_error}
Abstracts:        {count_abstracts}, Orcids:          {count_orcids}

{http_response_str}"""
            file_records = log_files_name['records']
            open(file_records, "a").write(report)

            add_to_full_report(f'{report}\n')