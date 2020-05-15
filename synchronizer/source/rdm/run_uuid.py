from setup                          import data_files_name
from source.general_functions       import initialize_counters
from source.rdm.add_record          import RdmAddRecord
from source.general_functions       import check_uuid_authenticity
from source.reports                 import Reports

class AddFromUuidList:
    """ Reads from a txt file a list of record uuids and submit them to RDM """

    def __init__(self):
        self.report = Reports()
        self.add_record = RdmAddRecord()


    def _introduction_report(func):
        def _wrapper(self):
            self.report.add_template(['console'], ['general', 'title'], ['PUSH RECORDS FROM LIST'])
            self.global_counters = initialize_counters()
            # Decorated method
            func(self)
        return _wrapper

    @_introduction_report
    def add_from_uuid_list(self):
        """ Submits to RDM all uuids in list (data/to_transfer.txt) """

        uuids = self._read_file()
        if not uuids:
            return

        for uuid in uuids:
            uuid = uuid.split('\n')[0]

            # Checks if lenght of the uuid is correct
            if not check_uuid_authenticity(uuid):
                self.report.add('Invalid uuid lenght.')
                continue
            
            self.add_record.push_record_by_uuid(self.global_counters, uuid)
        return


    def _read_file(self):
    
        # read to_transmit.txt
        file_name = data_files_name['transfer_uuid_list']
        uuids = open(file_name, 'r').readlines()

        if len(uuids) == 0:
            self.report.add('\nThere is nothing to transfer.\n')
            return False

        return uuids