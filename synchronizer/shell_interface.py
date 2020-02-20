from cmd import Cmd
import requests
import json
import os
import time
from datetime import date, datetime, timedelta
    
class MyPrompt(Cmd):

    prompt = 'pure_rdm_sync > '
    intro = "\nWelcome! Type ? to list commands\n"
    
    def do_exit(self, inp):
        print("\nBye\n")
        return True

    def help_exit(self):
        print('Type "exit"')
    

    #   ---     ---     ---
    def do_push_uuid_to_rmd(self, inp):
        """\nHelp -> \tPush to RDM all uuids that are in to_transfer.log\n"""
        self.get_props()
        from functions.rdm_push_byUuid          import rdm_push_byUuid

        rdm_push_byUuid(self, '')                   # transfer_type -> '' / 'full_comp' / 'update' / 'changes'


    #   ---     ---     ---
    def do_push_page_to_rdm(self, inp):
        """\nHelp ->\tPush to RDM records from Pure by page \n"""
        self.get_props()
        from functions.rdm_push_byPage          import get_pure_by_page
        from functions.rdm_push                 import create_invenio_data

        pag_begin = 3
        pag_end =   4
        pag_size =  5
        get_pure_by_page(self, pag_begin, pag_end, pag_size)

    
    #   ---     ---     ---
    def do_update_check(self, inp):
        """\nHelp ->\tGets from Pure API all records that have been modified after the last Update_check and push them to RDM. \n"""
        self.get_props()
        from functions.pure_get_updates         import pure_get_updates

        pure_get_updates(self)

    #   ---     ---     ---
    def do_changes_check(self, inp):
        """\nHelp ->\tGets from Pure API endpoint 'changes' all the records that have been updated.\n"""
        self.get_props()

        from functions.pure_get_changes         import pure_get_changes
        pure_get_changes(self)
    

    #   ---     ---     ---
    def do_full_comparison(self, inp):
        """\nHelp ->\tHaving all records from Pure and RDM finds out which records need to be added/deleted from RDM\n"""
        self.get_props()
        from functions.intersection_pure_rdm    import intersection_pure_rdm

        intersection_pure_rdm(self)


    #   ---     ---     ---
    def do_duplicates_in_rdm(self, inp):
        """\nHelp ->\tFind and delete RDM duplicate records\n"""
        self.get_props()
        from functions.get_from_rdm             import get_from_rdm
        from functions.find_rdm_duplicates      import find_rdm_duplicates

        resp = get_from_rdm(self)
        if resp == True: 
            find_rdm_duplicates(self)


    #   ---     ---     ---
    def do_delete_all_records(self, inp):
        """\nHelp ->\tThis is a temporary method..\n"""
        self.get_props()
        from functions.get_from_rdm             import get_from_rdm
        from functions.delete_all_records       import delete_all_records

        get_from_rdm(self)
        delete_all_records(self)


    #   ---     ---     ---
    def do_delete_by_recid(self, inp):
        """\nHelp ->\tDelete RDM records by recid (to_delete.log)\n"""
        self.get_props()
        from functions.delete_record            import delete_record

        delete_record(self)

    
    #   ---     ---     ---
    def do_shorten_logs(self, inp):
        """\nHelp ->\tReduce log files length or delete them\n"""
        self.get_props()
        from functions.shorten_log_files        import shorten_log_files

        shorten_log_files(self)


    #   ---     ---     ---
    def get_props(self):
        self.dirpath = os.path.dirname(os.path.abspath(__file__))
        self.json = json
        self.requests = requests
        self.os = os
        self.time = time
        self.date = date
        self.datetime = datetime
        self.timedelta = timedelta

    # to exit
    do_EOF = do_exit            # ctrl + d 

if __name__ == '__main__':
    MyPrompt().cmdloop()