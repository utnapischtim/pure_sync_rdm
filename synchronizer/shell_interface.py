from cmd import Cmd
import requests
import json
import os
import time
from datetime                       import date, datetime, timedelta
from functions.pure_get_changes     import pure_get_changes
from functions.rdm_push_by_page     import get_pure_by_page
from functions.rdm_push_record      import create_invenio_data
from functions.shorten_log_files    import shorten_log_files
from functions.rdm_duplicates       import rdm_duplicates
from functions.pure_get_updates     import pure_get_updates
from functions.delete_all_records   import delete_all_records
from functions.rdm_push_by_uuid     import rdm_push_by_uuid
from functions.delete_record        import delete_record, delete_from_list
    
class MyPrompt(Cmd):

    prompt = 'pure_rdm_sync > '
    intro = "\nWelcome! Type ? to list commands\n"
    
    def do_exit(self, inp):
        print("\nBye\n")
        return True

    def help_exit(self):
        print('Type "exit"')

    #   ---     ---     ---
    def do_changes(self, inp):
        """\nHelp ->\tGets from Pure API endpoint 'changes' all the records that have been created, modified and deleted.
        Next updates accordingly RDM records\n"""
        self.get_props()
        pure_get_changes(self)

    #   ---     ---     ---
    def do_pages(self, inp):
        """\nHelp ->\tPush to RDM records from Pure by page \n"""
        self.get_props()
        pag_begin = 18
        pag_end =   20
        pag_size =  2
        get_pure_by_page(self, pag_begin, pag_end, pag_size)
    
    #   ---     ---     ---
    def do_shorten_logs(self, inp):
        """\nHelp ->\tReduce log files length or delete them\n"""
        self.get_props()
        shorten_log_files(self)

    #   ---     ---     ---
    def do_duplicates(self, inp):
        """\nHelp ->\tFind and delete RDM duplicate records\n"""
        self.get_props()
        rdm_duplicates(self)
    
    #   ---     ---     ---
    def do_update(self, inp):
        """\nHelp -> \t\n"""
        self.get_props()
        pure_get_updates(self)

    #   ---     ---     ---
    def do_delete_all(self, inp):
        """\nHelp -> \t\n"""
        self.get_props()
        delete_all_records(self)

    #   TEMPORARY .....................
    def do_delete_from_list(self, inp):
        """\nHelp ->\tDelete RDM records by recid (to_delete.log)\n"""
        self.get_props()
        delete_from_list(self)

    #   TEMPORARY .....................
    def do_uuid_push_from_list(self, inp):
        """\nHelp -> \tPush to RDM all uuids that are in to_transfer.log\n"""
        self.get_props()
        self.count_total                       = 0
        self.count_errors_push_metadata        = 0
        self.count_errors_put_file             = 0
        self.count_errors_record_delete        = 0
        self.count_successful_push_metadata    = 0
        self.count_successful_push_file        = 0
        self.count_successful_record_delete    = 0
        self.count_uuid_not_found_in_pure      = 0

        rdm_push_by_uuid(self)                   # transfer_type -> '' / 'full_comp' / 'update' / 'changes'

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