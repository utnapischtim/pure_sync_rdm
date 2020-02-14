from cmd import Cmd
import os
dirpath = os.path.dirname(os.path.abspath(__file__))
    
class MyPrompt(Cmd):

    prompt = 'pure_rdm_sync > '
    intro = "\nWelcome! Type ? to list commands\n"
    
    def do_exit(self, inp):
        print("\nBye\n")
        return True

    def help_exit(self):
        print('Type "exit"')


    # GET UPDATES FROM PURE
    def do_Updates_check(self, inp):
        """\nHelp -> 
                Gets from Pure API all records that have been modified
                after the last update       """
        from functions.get_pure_updates import get_pure_updates
        get_pure_updates()

    
    # GET CHANGES FROM PURE
    def do_Changes_check(self, inp):
        """Help -> Gets from Pure API endpoint 'changes' all the records that have been modified.\n"""
        from functions.get_pure_changes import get_pure_changes
        get_pure_changes()


    # DELETE RDM RECORD
    def do_Duplicates_delete_RDM(self, inp):
        """Help -> Deletes all duplicate records from RDM.\n"""
        print("do_RDM_delete_duplicates")
        from functions.full_comparison import FullComparison

        inst_fc = FullComparison()
        inst_fc.get_from_rdm()
        inst_fc.find_rdm_duplicates()


    # COMPARE ALL PURE AND RDM RECORDS && DELETE DUPLICATES
    def do_Full_comparison_and_dup(self, inp):
        """\nHelp ->  
                Get all records from Pure and from RDM,
                afterwards checks with Pure records are missing in RDM.
                Finally it checks for duplicate records in RDM and removes them.
        """
        print("do_RDM_delete_duplicates")
        from functions.uuid_transfer   import uuid_transfer
        from functions.full_comparison import FullComparison

        inst_fc = FullComparison()
        inst_fc.get_from_rdm()
        inst_fc.get_from_pure()
        inst_fc.find_missing()
        uuid_transfer('full_comp')

        inst_fc.find_rdm_duplicates()
    
    
    # UUID TRANSFER
    def do_Transfer_uuid(self, inp):
        """\nHelp -> Only uuid transfer"""
        from functions.uuid_transfer   import uuid_transfer
        uuid_transfer('')

    
    # REDUCE LENGTH LOGS
    def do_Shorten_logs(self, inp):
        """Reduce length of log files"""
        from functions.shorten_log_files   import shorten_log_files
        shorten_log_files()

    # to exit
    do_EOF = do_exit            # ctrl + d 

if __name__ == '__main__':
    MyPrompt().cmdloop()