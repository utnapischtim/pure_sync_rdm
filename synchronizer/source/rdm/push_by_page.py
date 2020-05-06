import json
from source.general_functions       import initialize_counters
from source.pure.general_functions  import get_pure_metadata
from source.rdm.add_record          import RdmAddRecord
from source.reports                 import Reports

class RunPages:

    def __init__(self):
        self.report = Reports()
        self.rdm_add_record = RdmAddRecord()
        self.report_files = ['console']
        
    def get_pure_by_page(self, pag_begin: int, pag_end: int, pag_size: int):
        """ Gets records from Pure 'research-outputs' endpoint by page and submit them to RDM. """

        for pag in range(pag_begin, pag_end):
    
            self.global_counters = initialize_counters()

            # Report intro
            self.report.add_template(self.report_files, ['general', 'title'], ['PAGES'])
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
