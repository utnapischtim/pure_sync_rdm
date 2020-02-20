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
    def do_rdm_push_byUuid(self, inp):
        """\nHelp -> \n"""
        self.get_props()

        from functions.rdm_push_byUuid          import rdm_push_byUuid
        rdm_push_byUuid(self, '')                   # transfer_type -> '' / 'full_comp' / 'update' / 'changes'

    #   ---     ---     ---
    def do_rdm_push_byPage(self, inp):
        """\nHelp -> \n"""
        self.get_props()

        from functions.rdm_push_byPage          import get_pure_by_page
        from functions.rdm_push                 import create_invenio_data
        pag_begin = 1
        pag_end =   3
        pag_size =  10
        get_pure_by_page(self, pag_begin, pag_end, pag_size)
    
    #   ---     ---     ---
    def do_pure_updates_check(self, inp):
        """\nHelp -> \n"""
        self.get_props()

        from functions.pure_get_updates         import pure_get_updates
        pure_get_updates(self)

    #   ---     ---     ---
    def do_pure_get_changes(self, inp):
        """\nHelp -> \n"""
        self.get_props()

        from functions.pure_get_changes         import pure_get_changes
        pure_get_changes(self)
    
    #   ---     ---     ---
    def do_full_comparison(self, inp):
        """\nHelp -> \n"""
        self.get_props()

        from functions.intersection_pure_rdm    import intersection_pure_rdm
        intersection_pure_rdm(self)

    #   ---     ---     ---
    def do_rdm_duplicates(self, inp):
        """\nHelp -> \n"""
        self.get_props()

        from functions.get_from_rdm             import get_from_rdm
        from functions.find_rdm_duplicates      import find_rdm_duplicates
        resp = get_from_rdm(self)
        if resp == True: 
            find_rdm_duplicates(self)

    #   ---     ---     ---
    def do_delete_all_recs(self, inp):
        """\nHelp -> \n"""
        self.get_props()

        from functions.get_from_rdm             import get_from_rdm
        from functions.delete_all_records       import delete_all_records
        get_from_rdm(self)
        delete_all_records(self)

    #   ---     ---     ---
    def do_delete_toDelete(self, inp):
        """\nHelp -> \n"""
        self.get_props()

        from functions.delete_record            import delete_record
        delete_record(self)

    
    # REDUCE LENGTH LOGS
    def do_Shorten_logs(self, inp):
        """\nHelp -> Reduce length of log files\n"""
        self.get_props()

        from functions.shorten_log_files        import shorten_log_files
        shorten_log_files(self)


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