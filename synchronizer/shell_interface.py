from cmd import Cmd
import os
dirpath = os.path.dirname(os.path.abspath(__file__))
    
class MyPrompt(Cmd):

    prompt = 'pure_rdm_sync > '
    intro = "\nWelcome! Type ? to list commands\n"
    
    # EXIT
    def do_exit(self, inp):
        print("\nBye\n")
        return True

    def help_exit(self):
        print('Type "exit"')
    

    def do_Test(self, inp):
        print(type(inp))


    # GET UPDATES FROM PURE
    def do_Updates_check(self, inp):
        """\nHelp -> 
                Gets from Pure API all records that have been modified
                after the last update
        """
        from a3_get_pure_updates import get_pure_updates
        get_pure_updates()

    
    # GET CHANGES FROM PURE
    def do_Changes_check(self, inp):
        """Help -> Gets from Pure API endpoint 'changes' all the records that have been modified.\n"""
        from a4_get_pure_changes import get_pure_changes
        get_pure_changes()


    # DELETE RDM RECORD
    def do_Duplicates_delete_RDM(self, inp):
        """Help -> Deletes all duplicate records from RDM.\n"""
        print("do_RDM_delete_duplicates")
        from a8_full_comparison import FullComparison

        inst_fc = FullComparison()
        inst_fc.get_from_rdm()
        inst_fc.find_rdm_duplicates()


    # COMPARE ALL PURE AND RDM RECORDS && DELETE DUPLICATES
    def do_PureRdmComparison_duplicates(self, inp):
        """\nHelp ->  
                Get all records from Pure and from RDM,
                afterwards checks with Pure records are missing in RDM.
                Finally it checks for duplicate records in RDM and removes them.
        """
        print("do_RDM_delete_duplicates")
        from a2_uuid_transfer   import uuid_transfer
        from a8_full_comparison import FullComparison

        inst_fc = FullComparison()
        inst_fc.get_from_rdm()
        inst_fc.get_from_pure()
        inst_fc.find_missing()
        uuid_transfer('full_comp')

        inst_fc.find_rdm_duplicates()
    

    
    # REDUCE LENGTH LOGS
    def shorten_logs(self, inp):
        """Reduce length of daily log files"""

    

    # to exit
    do_EOF = do_exit            # ctrl + d 


if __name__ == '__main__':
    MyPrompt().cmdloop()