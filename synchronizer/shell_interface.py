""" Pure synchronizer

Usage:
    shell_interface.py changes
    shell_interface.py pages            (PAGE_START) (PAGE_END) (PAGE_SIZE)
    shell_interface.py logs
    shell_interface.py delete
    shell_interface.py uuid
    shell_interface.py duplicates
    shell_interface.py delete_all
    shell_interface.py owners
    shell_interface.py owners_orcid
    shell_interface.py owners_list
    shell_interface.py group_split      (OLD_GROUP) (NEW_GROUPS)
    shell_interface.py group_merge      (OLD_GROUPS) (NEW_GROUP)

Arguments:
    PAGE_START      Starting page (int)
    PAGE_END        Ending page (int)
    PAGE_SIZE       Page size (int)
    OLD_GROUP       Old group externalId (str)
    NEW_GROUPS      List of new groups externalIds separated by a space(str)
    OLD_GROUPS      List of old groups externalIds separated by a space (str)
    NEW_GROUP       New group externalId (str)

Options:
    -h --help     Show this screen.
    --version     Show version.

"""
import requests
import json
import os
import time
from docopt                             import docopt
from datetime                           import date, datetime, timedelta
from functions.pure_get_changes         import pure_get_changes
from functions.rdm_push_by_page         import get_pure_by_page
from functions.rdm_push_record          import create_invenio_data
from functions.log_files                import delete_old_log_files
from functions.rdm_duplicates           import rdm_duplicates
from functions.delete_all_records       import delete_all_records
from functions.rdm_push_by_uuid         import rdm_push_by_uuid
from functions.delete_record            import delete_record, delete_from_list
from functions.general_functions        import db_connect
from functions.rdm_owners               import rdm_owners, get_rdm_record_owners, rdm_owners_by_orcid
from functions.rdm_groups               import rdm_group_split, rdm_group_merge


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
        self.rdm_record_owner = None
        db_connect(self)


    def changes(self):
        """ Gets from Pure API endpoint 'changes' all the records that have been created, modified and deleted.
        Next updates accordingly RDM records """
        pure_get_changes(self)

    def pages(self, page_start, page_end, page_size):
        """ Push to RDM records from Pure by page """
        get_pure_by_page(self, page_start, page_end, page_size)

    def logs(self):
        """ Delete old log files """
        delete_old_log_files(self)

    def delete(self):
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

    def owners(self):
        """ Gets from pure all the records related to a certain user,
            afterwards it modifies/create RDM records accordingly."""
        rdm_owners(self)

    def owners_orcid(self):
        rdm_owners_by_orcid(self)

    def owners_list(self):
        """ Gets from RDM all record uuids, recids and owners """
        get_rdm_record_owners(self)

    def rdm_group_split(self, old_id, new_ids):
        """ Split a single group into moltiple ones """
        rdm_group_split(self, old_id, new_ids)

    def rdm_group_merge(self):
        """ Merges multiple groups into a single one """
        rdm_group_merge(self, old_ids, new_id)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Pure synchronizer 1.0')
    print(arguments)
    docopt_instance = shell_interface()

if arguments['changes']:
    docopt_instance.changes()

elif arguments['pages']:
    page_start = int(arguments['PAGE_START'])
    page_end   = int(arguments['PAGE_END'])
    page_size  = int(arguments['PAGE_SIZE'])
    docopt_instance.pages(page_start, page_end, page_size)

elif arguments['logs']:
    docopt_instance.logs()

elif arguments['delete']:
    docopt_instance.delete()

elif arguments['uuid']:
    docopt_instance.uuid()

elif arguments['duplicates']:
    docopt_instance.duplicates()

elif arguments['delete_all']:
    docopt_instance.delete_all()

elif arguments['owners']:
    docopt_instance.owners()

elif arguments['owners_orcid']:
    docopt_instance.owners_orcid()

elif arguments['owners_list']:
    docopt_instance.owners_list()

elif arguments['group_split']:
    old_id  = arguments['OLD_GROUP']
    new_ids = arguments['NEW_GROUPS'].split(' ')
    docopt_instance.rdm_group_split(old_id, new_ids)

elif arguments['group_merge']:
    old_ids = arguments['OLD_GROUPS'].split(' ')
    new_id  = arguments['NEW_GROUP']
    docopt_instance.rdm_group_merge(old_ids, new_id)

