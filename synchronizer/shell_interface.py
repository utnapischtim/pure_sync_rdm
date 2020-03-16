""" Pure synchronizer

Usage:
    shell_interface.py changes
    shell_interface.py pages
    shell_interface.py shorten_logs
    shell_interface.py delete_from_list
    shell_interface.py uuid
    shell_interface.py duplicates
    shell_interface.py delete_all
    shell_interface.py test
    shell_interface.py persons

Options:
    -h --help     Show this screen.
    --version     Show version.

"""
from docopt                             import docopt
import requests
import json
import os
import time
from cmd                                import Cmd
from datetime                           import date, datetime, timedelta
from functions.pure_get_changes         import pure_get_changes
from functions.rdm_push_by_page         import get_pure_by_page
from functions.rdm_push_record          import create_invenio_data
from functions.shorten_log_files        import shorten_log_files
from functions.rdm_duplicates           import rdm_duplicates
from functions.delete_all_records       import delete_all_records
from functions.rdm_push_by_uuid         import rdm_push_by_uuid
from functions.delete_record            import delete_record, delete_from_list
from functions.general_functions        import db_connect, db_query
from functions.rdm_person_association   import rdm_person_association



class shell_interface:
    
    def __init__(self):
        self.dirpath = os.path.dirname(os.path.abspath(__file__))
        self.json = json
        self.requests = requests
        self.os = os
        self.time = time
        self.date = date
        self.datetime = datetime
        self.timedelta = timedelta
        db_connect(self)


    def changes(self):
        """ Gets from Pure API endpoint 'changes' all the records that have been created, modified and deleted.
        Next updates accordingly RDM records """
        pure_get_changes(self)


    def pages(self):
        """ Push to RDM records from Pure by page """
        pag_begin = 2
        pag_end =   3
        pag_size =  2
        get_pure_by_page(self, pag_begin, pag_end, pag_size)


    def shorten_logs(self):
        """ Reduce log files length or delete them """
        shorten_log_files(self)


    def delete_from_list(self):
        """ Delete RDM records by recid (to_delete.log) """
        delete_from_list(self)


    def uuid(self):
        """ Push to RDM all uuids that are in to_transfer.log """
        rdm_push_by_uuid(self)


    def duplicates(self):
        """ Find and delete RDM duplicate records """
        rdm_duplicates(self)


    def delete_all(self):
        delete_all_records(self)

    def persons(self):
        rdm_person_association(self)



    
    def get_email_test(self):
        # DB query - Get user IP
        resp = db_query(self, "select * from accounts_user where email = 'admin@invenio.org'")
        if len(resp) == 0:
            print('\naccounts_user: email not found\n')
        elif len(resp) > 1:
            print('\naccounts_user: email found multiple times\n')
        else:
            resp = resp[0]
            print(f"""
                id:         {resp[0]}
                email:      {resp[1]}
                current_ip: {resp[8]}
                """)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Pure synchronizer 1.0')
    # print(arguments)
    docopt_instance = shell_interface()

if arguments['changes']             == True: docopt_instance.changes()
elif arguments['pages']             == True: docopt_instance.pages()
elif arguments['shorten_logs']      == True: docopt_instance.shorten_logs()
elif arguments['delete_from_list']  == True: docopt_instance.delete_from_list()
elif arguments['uuid']              == True: docopt_instance.uuid()
elif arguments['duplicates']        == True: docopt_instance.duplicates()
elif arguments['delete_all']        == True: docopt_instance.delete_all()
elif arguments['persons']           == True: docopt_instance.persons()
