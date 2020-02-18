import requests
import json
import os
import time
from datetime   import date, datetime, timedelta

class Master:

    def __init__(self):
        self.dirpath = os.path.dirname(os.path.abspath(__file__))
        self.json = json
        self.requests = requests
        self.os = os
        self.time = time
        self.date = date
        self.datetime = datetime
        self.timedelta = timedelta


    #   ---     ---     ---
    def rdm_push_byUuid(self):

        from functions.rdm_push_byUuid import rdm_push_byUuid
        rdm_push_byUuid(self, '')               # transfer_type -> '' / 'full_comp' / 'update' / 'changes'


    #   ---     ---     ---
    def rdm_push_byPage(self):

        from functions.rdm_push_byPage  import get_pure_by_page
        from functions.rdm_push         import create_invenio_data

        pag_begin = 6
        pag_end =   7
        pag_size =  50
        get_pure_by_page(self, pag_begin, pag_end, pag_size)
    

    #   ---     ---     ---
    def pure_updates_check(self):

        from functions.pure_get_updates import pure_get_updates
        pure_get_updates(self)
    

    #   ---     ---     ---
    def pure_get_changes(self):

        from functions.pure_get_changes import pure_get_changes
        from functions.rdm_push_byUuid  import rdm_push_byUuid

        pure_get_changes(self)
        rdm_push_byUuid(self, 'changes')
    

    #   ---     ---     ---
    def full_comparison(self):

        from functions.get_from_pure            import get_from_pure
        from functions.get_from_rdm             import get_from_rdm
        from functions.intersection_pure_rdm    import intersection_pure_rdm
        from functions.rdm_push_byUuid          import rdm_push_byUuid

        get_from_pure(self)
        get_from_rdm(self)
        intersection_pure_rdm(self)
        rdm_push_byUuid(self, 'full_comp')
    

    #   ---     ---     ---
    def rdm_delete_duplicates(self):

        from functions.get_from_rdm             import get_from_rdm
        from functions.find_rdm_duplicates      import find_rdm_duplicates

        get_from_rdm(self)
        find_rdm_duplicates(self)


    #   ---     ---     ---
    def delete_all_recs(self):

        from functions.get_from_rdm             import get_from_rdm
        from functions.delete_all_records import delete_all_records

        get_from_rdm(self)
        delete_all_records(self)
    

    #   ---     ---     ---
    def delete_toDelete(self):

        from functions.delete_record import delete_record
        delete_record(self)
    

    #   ---     ---     ---
    def shorten_logs(self):

        from functions.shorten_log_files import shorten_log_files
        shorten_log_files(self)



master_inst = Master()      # - - Create instance - -

# master_inst.rdm_push_byUuid()
# master_inst.rdm_push_byPage()
# master_inst.pure_updates_check()
# master_inst.pure_get_changes()
# master_inst.full_comparison()
master_inst.rdm_delete_duplicates()
# master_inst.delete_all_recs()
# master_inst.delete_toDelete()
# master_inst.shorten_logs()

## NOTES ##
#
#  best option is first to do the full_comparison in order to have 
#  pure_uuids.log and rdm_uuids.log up to date