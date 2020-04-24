from setup                      import dirpath
from source.general_functions   import itinialize_counters, add_to_full_report
from source.rdm.add_record      import RdmAddRecord

class AddFromUuidList:

    def add_from_uuid_list(self):

        self.global_counters = itinialize_counters()

        # read to_transfer.log
        file_name = f'{dirpath}/data/to_transfer.txt'
        uuids = open(file_name, 'r').readlines()

        if len(uuids) == 0:
            add_to_full_report('\nThere is nothing to transfer.\n')
            return

        rdm_add_record = RdmAddRecord()

        for uuid in uuids:
            uuid = uuid.split('\n')[0]
            if (len(uuid) != 36):
                add_to_full_report('Invalid uuid lenght.')
                continue
            
            rdm_add_record.push_record_by_uuid(self.global_counters, uuid)
        return
