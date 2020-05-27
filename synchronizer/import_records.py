from source.rdm.requests    import Requests

class importRecords:
    def __init__(self):
        self.rdm_requests = Requests()

    def run_import(self):
        response = self.rdm_requests.get_metadata('', '05qm8-ats84')

        








import_records = importRecords()
import_records.run_import()