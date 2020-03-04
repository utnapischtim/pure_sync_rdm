""" Pure synchronizer

Usage:
    shell_interface.py changes
    shell_interface.py pages
    shell_interface.py shorten_logs
    shell_interface.py delete_from_list
    shell_interface.py push_from_list
    shell_interface.py duplicates
    shell_interface.py delete_all

Options:
    -h --help     Show this screen.
    --version     Show version.

"""
from docopt                         import docopt
import requests
import json
import os
import time
from cmd                            import Cmd
from datetime                       import date, datetime, timedelta
from functions.pure_get_changes     import pure_get_changes
from functions.rdm_push_by_page     import get_pure_by_page
from functions.rdm_push_record      import create_invenio_data
from functions.shorten_log_files    import shorten_log_files
from functions.rdm_duplicates       import rdm_duplicates
from functions.delete_all_records   import delete_all_records
from functions.rdm_push_by_uuid     import rdm_push_by_uuid
from functions.delete_record        import delete_record, delete_from_list


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


    def changes(self):
        """ Gets from Pure API endpoint 'changes' all the records that have been created, modified and deleted.
        Next updates accordingly RDM records """
        pure_get_changes(self)


    def pages(self):
        """ Push to RDM records from Pure by page """
        pag_begin = 1
        pag_end =   3
        pag_size =  50
        get_pure_by_page(self, pag_begin, pag_end, pag_size)


    def shorten_logs(self):
        """ Reduce log files length or delete them """
        shorten_log_files(self)


    def delete_from_list(self):
        """ Delete RDM records by recid (to_delete.log) """
        delete_from_list(self)


    def push_from_list(self):
        """ Push to RDM all uuids that are in to_transfer.log """
        rdm_push_by_uuid(self)


    def duplicates(self):
        """ Find and delete RDM duplicate records """
        rdm_duplicates(self)


    def delete_all(self):
        delete_all_records(self)



if __name__ == '__main__':
    arguments = docopt(__doc__, version='Pure synchronizer 1.0')
    # print(arguments)
    docopt_instance = shell_interface()

if arguments['changes'] == True:                docopt_instance.changes()
elif arguments['pages'] == True:                docopt_instance.pages()
elif arguments['shorten_logs'] == True:         docopt_instance.shorten_logs()
elif arguments['delete_from_list'] == True:     docopt_instance.delete_from_list()
elif arguments['push_from_list'] == True:       docopt_instance.push_from_list()
elif arguments['duplicates'] == True:           docopt_instance.duplicates()
elif arguments['delete_all'] == True:           docopt_instance.delete_all()






