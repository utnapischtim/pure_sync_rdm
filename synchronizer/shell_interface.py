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
    def do_Pure_get_updates(self, inp):
        """
        Help -> Gets from Pure API all records that have the current date as 'modifiedDate'.\n
                Parameters: days span
        """
        from functions.pure_get_updates import pure_get_updates
        pure_get_updates()

    
    # GET CHANGES FROM PURE
    def do_Pure_get_changes(self, inp):
        """Help -> Gets from Pure API endpoint 'changes' all the records that have been updated.\n"""
        print("Pure_get_changes")


    # PUSH to_transfer.log UUIDs TO RDM
    def do_Push_to_transfer(self, inp):
        """Help -> Transmit all uuids that are in to_transfer.log\n"""
        print("Push_to_transfer")


    # DELETE RDM RECORD (by recid)
    def do_RDM_record_delete(self, inp):
        """Help -> Deletes a record from RDM using the record's recid.\n"""
        print("RDM_record_delete")
    

    # COMPARE ALL PURE AND RDM RECORDS
    def do_Full_records_check(self, inp):
        """Help -> Gets all records metadata from Pure and from RDM, looks for differences between the two and updates RDM.\n"""
        print("Full_records_check")

    
    # REDUCE LENGTH LOGS
    def shorten_logs(self, inp):
        """Reduce length of daily log files"""

    

    # to exit
    do_EOF = do_exit            # ctrl + d 


if __name__ == '__main__':
    MyPrompt().cmdloop()