import requests
import json
import os
import time
from datetime   import date, datetime

class Master:

    def __init__(self):
        self.dirpath = os.path.dirname(os.path.abspath(__file__))
        self.json = json
        self.requests = requests
        self.os = os
        self.time = time
        self.date = date
        self.datetime = datetime


    #   ---     ---     ---
    def rdm_push_byUuid(self):
        from functions.rdm_push_byUuid import rdm_push_byUuid
        rdm_push_byUuid(self, '')               # transfer_type -> '' / 'full_comp' / 'update' / 'changes'


    #   ---     ---     ---
    def rdm_push_byPage(self):
        from functions.rdm_push_byPage import get_pure_by_page

        pag_begin = 1
        pag_end =   2
        pag_size =  3
        get_pure_by_page(self, pag_begin, pag_end, pag_size)
    

    #   ---     ---     ---
    def pure_updates_check(self):
        print('')
    

    #   ---     ---     ---
    def pure_changes_check(self):
        print('')
    

    #   ---     ---     ---
    def full_comparison(self):

        from functions.get_from_pure            import get_from_pure
        from functions.get_from_rdm             import get_from_rdm
        from functions.pure_rdm_intersection    import pure_rdm_intersection

        get_from_pure(self)
        get_from_rdm(self)
        pure_rdm_intersection(self)
    

    #   ---     ---     ---
    def rdm_delete_duplicates(self):
        print('')
    

    #   ---     ---     ---
    def delete_all_recs(self):
        print('')
    

    #   ---     ---     ---
    def delete_toDelete(self):
        print('')
    

    #   ---     ---     ---
    def shorten_logs(self):
        print('')



master_inst = Master()      # - - Create instance - -

# master_inst.rdm_push_byUuid()
master_inst.rdm_push_byPage()
# master_inst.delete_toDelete()
# master_inst.pure_updates_check()
# master_inst.pure_changes_check()
# master_inst.full_comparison()
# master_inst.rdm_delete_duplicates()
# master_inst.delete_all_recs()
# master_inst.delete_toDelete()
# master_inst.shorten_logs()