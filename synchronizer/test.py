""" Pure synchronizer

Usage:
    shell_interface.py changes
    shell_interface.py pages
    shell_interface.py shorten_logs
    shell_interface.py delete_from_list
    shell_interface.py uuid
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


    def uuid(self):
        """ Push to RDM all uuids that are in to_transfer.log """
        rdm_push_by_uuid(self)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Pure synchronizer 1.0')
    # print(arguments)
    docopt_instance = shell_interface()

# if arguments['changes'] == True:                docopt_instance.changes()
# elif arguments['pages'] == True:                docopt_instance.pages()
# elif arguments['shorten_logs'] == True:         docopt_instance.shorten_logs()
# elif arguments['delete_from_list'] == True:     docopt_instance.delete_from_list()
# elif arguments['uuid'] == True:                 docopt_instance.uuid()
# elif arguments['duplicates'] == True:           docopt_instance.duplicates()
# elif arguments['delete_all'] == True:           docopt_instance.delete_all()



docopt_instance.uuid()


