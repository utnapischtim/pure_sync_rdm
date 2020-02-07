from cmd import Cmd
    
class MyPrompt(Cmd):
    prompt = 'pure_rdm_sync > '
    intro = "\nWelcome! Type ? to list commands\n"
    
    # EXIT
    def do_exit(self, inp):
        print("\nBye\n")
        return True

    def help_exit(self):
        print('Type "exit"')
    

    # GET UPDATES FROM PURE
    def do_Pure_get_updates(self, inp):
        """\nHelp:\tGets from Pure API all records that have the current date as 'modifiedDate'.\n"""
        from functions import *
        print("Pure_get_updates")

    
    # GET CHANGES FROM PURE
    def do_Pure_get_changes(self, inp):
        """\nHelp:\tGets from Pure API endpoint 'changes' all the records that have been updated.\n"""
        print("Pure_get_changes")


    # PUSH to_transfer.log UUIDs TO RDM
    def do_Push_to_transfer(self, inp):
        """\nHelp:\tTransmit all uuids that are in to_transfer.log\n"""
        print("Push_to_transfer")


    # DELETE RDM RECORD (by recid)
    def do_RDM_record_delete(self, inp):
        """\nHelp:\tDeletes a record from RDM using the record's recid.\n"""
        print("RDM_record_delete")
    

    # COMPARE ALL PURE AND RDM RECORDS
    def do_Full_records_check(self, inp):
        """\nHelp:\tGets all records metadata from Pure and from RDM, looks for differences between the two and updates RDM.\n"""
        print("Full_records_check")
    

    # to exit
    do_EOF = do_exit            # ctrl + d 


if __name__ == '__main__':
    MyPrompt().cmdloop()