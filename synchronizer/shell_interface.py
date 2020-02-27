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
    def do_changes_check(self, inp):
        """\nHelp ->\tGets from Pure API endpoint 'changes' all the records that have been created, modified or deleted.\n"""
        self.get_props()

        from functions.pure_get_changes         import pure_get_changes
        pure_get_changes(self)


    #   ---     ---     ---
    def do_push_page_to_rdm(self, inp):
        """\nHelp ->\tPush to RDM records from Pure by page \n"""
        self.get_props()
        from functions.rdm_push_by_page          import get_pure_by_page
        from functions.rdm_push                 import create_invenio_data

        pag_begin = 15
        pag_end =   20
        pag_size =  50
        get_pure_by_page(self, pag_begin, pag_end, pag_size)

    
    #   ---     ---     ---
    def do_shorten_logs(self, inp):
        """\nHelp ->\tReduce log files length or delete them\n"""
        self.get_props()
        from functions.shorten_log_files        import shorten_log_files

        shorten_log_files(self)



    

    #   ---     ---     ---
    def do_push_uuid_to_rmd(self, inp):
        """\nHelp -> \tPush to RDM all uuids that are in to_transfer.log\n"""
        self.get_props()
        from functions.rdm_push_by_uuid          import rdm_push_by_uuid

        rdm_push_by_uuid(self, '')                   # transfer_type -> '' / 'full_comp' / 'update' / 'changes'
    

    #   ---     ---     ---
    def do_duplicates_in_rdm(self, inp):
        """\nHelp ->\tFind and delete RDM duplicate records\n"""
        self.get_props()
        from functions.rdm_duplicates      import rdm_duplicates

        rdm_duplicates(self)


    #   ---     ---     ---
    def do_delete_reading_txt(self, inp):
        """\nHelp ->\tDelete RDM records by recid (to_delete.log)\n"""
        self.get_props()
        from functions.delete_record import delete_reading_txt

        delete_reading_txt(self)
    

    #   ---     ---     ---
    def do_update(self, inp):
        """\nHelp -> \t\n"""
        self.get_props()
        from functions.pure_get_updates          import pure_get_updates

        pure_get_updates(self)
    

    #   ---     ---     ---
    def do_delete_all(self, inp):
        """\nHelp -> \t\n"""
        self.get_props()
        from functions.delete_all_records    import delete_all_records

        delete_all_records(self)

    
    #   ---     ---     ---
    def do_test(self, inp):
        self.get_props()

        from functions.delete_record        import delete_record
        response = delete_record(self, inp)

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