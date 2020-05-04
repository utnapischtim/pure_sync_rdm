import json
from datetime                       import date, datetime
from setup                          import pure_rest_api_url, log_files_name
from source.general_functions       import dirpath, add_spaces, initialize_counters
from source.pure.general_functions  import get_pure_metadata
from source.rdm.add_record          import RdmAddRecord
from source.reports                 import Reports

class RunPages:

    def __init__(self):
        self.report = Reports()
        self.rdm_add_record = RdmAddRecord()
        self.report_files = ['console', 'records']
        
    def get_pure_by_page(self, pag_begin: int, pag_end: int, pag_size: int):

        for pag in range(pag_begin, pag_end):
    
            self.global_counters = initialize_counters()

            # Report intro
            current_time = datetime.now().strftime("%H:%M:%S")
            self.report.add_template(self.report_files, ['general', 'title'], ['PAGES', current_time])
            self.report.add_template(self.report_files, ['pages', 'page_and_size'], [pag, pag_size])

            # Pure get request
            response = get_pure_metadata('research-outputs', '', {'page': pag, 'pageSize': pag_size})

            # Load json response
            resp_json = json.loads(response.content)

            # Creates data to push to RDM
            for item in resp_json['items']:
                self.report.add(['console'], '')          # adds new line in the console
                self.rdm_add_record.create_invenio_data(self.global_counters, item)

            self.report_summary(pag, pag_size)


    def report_summary(self, pag, pag_size):
        # Global counters
        self.report.summary_global_counters(self.report_files, self.global_counters)
        # Summary pages.log
        self.report.pages_single_line(self.global_counters, pag, pag_size)
