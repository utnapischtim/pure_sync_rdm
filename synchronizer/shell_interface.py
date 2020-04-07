""" Pure synchronizer

Usage:
    shell_interface.py changes
    shell_interface.py pages
    shell_interface.py shorten_logs
    shell_interface.py delete
    shell_interface.py uuid
    shell_interface.py duplicates
    shell_interface.py delete_all
    shell_interface.py test
    shell_interface.py owners
    shell_interface.py owners_orcid
    shell_interface.py owners_list
    shell_interface.py group_split
    shell_interface.py group_merge

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
from functions.shorten_log_files        import shorten_log_files
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


    def pages(self):
        """ Push to RDM records from Pure by page """
        pag_begin = 1
        pag_end =   20
        pag_size =  20
        get_pure_by_page(self, pag_begin, pag_end, pag_size)


    def shorten_logs(self):
        """ Reduce log files length or delete them """
        shorten_log_files(self)


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
        rdm_owners(self, '56038')

        # 2 - 948
        # 3 - 54426
        # 4 - 56038

    def owners_orcid(self):
        rdm_owners_by_orcid(self, '0000-0002-4154-6945')

    def owners_list(self):
        """ Gets from RDM all record uuids, recids and owners """
        get_rdm_record_owners(self)

    def rdm_group_split(self):
        """  """
        old_id  = '2376'
        new_ids = ['20353', '33320']
        rdm_group_split(self, old_id, new_ids)

    def rdm_group_merge(self):
        """  """
        old_id  = ['20353', '33320']
        new_ids = '2376'
        rdm_group_merge(self, old_id, new_ids)
# 709803a8-0655-4a08-a05a-fb706f36a332
# a218e4b7-f925-4329-9584-06d9e1c18869
# 8955b899-e9fb-43a1-8512-9b95d52dc123
# 6cafe0a1-41a0-4402-900b-021a07d25c7a
# a144e753-66b8-4f7b-a4fd-4e5a098dc3ec


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Pure synchronizer 1.0')
    # print(arguments)
    docopt_instance = shell_interface()

if arguments['changes']             == True: docopt_instance.changes()
elif arguments['pages']             == True: docopt_instance.pages()
elif arguments['shorten_logs']      == True: docopt_instance.shorten_logs()
elif arguments['delete']            == True: docopt_instance.delete()
elif arguments['uuid']              == True: docopt_instance.uuid()
elif arguments['duplicates']        == True: docopt_instance.duplicates()
elif arguments['delete_all']        == True: docopt_instance.delete_all()
elif arguments['owners']            == True: docopt_instance.owners()
elif arguments['owners_orcid']      == True: docopt_instance.owners_orcid()
elif arguments['owners_list']       == True: docopt_instance.owners_list()
elif arguments['group_split']       == True: docopt_instance.rdm_group_split()
elif arguments['group_merge']       == True: docopt_instance.rdm_group_merge()
