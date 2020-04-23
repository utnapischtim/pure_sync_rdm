""" Pure synchronizer

Usage:
    shell_interface.py changes
    shell_interface.py pages            (PAGE_START) (PAGE_END) (PAGE_SIZE)
    shell_interface.py logs
    shell_interface.py delete
    shell_interface.py uuid
    shell_interface.py duplicates
    shell_interface.py delete_all
    shell_interface.py owner
    shell_interface.py owner_orcid
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
from docopt                         import docopt
from main                           import method_call
from source.pure.get_changes        import pure_get_changes
from source.rdm.push_by_page        import RunPages
from source.log_manager             import delete_old_log_files
from source.rdm.duplicates          import rdm_duplicates
from source.rdm.delete_all_records  import delete_all_records
from source.rdm.push_by_uuid        import AddFromUuidList
from source.rdm.delete_record       import delete_from_list
from source.rdm.owners              import RdmOwners, get_rdm_record_owners
from source.rdm.groups              import RdmGroups

class shell_interface:
    
    def __init__(self):
        self.rdm_record_owner = None

    def changes(self):
        """ Gets from Pure API endpoint 'changes' all the records that have been 
        created, modified and deleted. Next updates accordingly RDM records """
        pure_get_changes()

    def pages(self, page_start, page_end, page_size):
        """ Push to RDM records from Pure by page """
        run_pages = RunPages()
        run_pages.get_pure_by_page(page_start, page_end, page_size)

    def logs(self):
        """ Delete old log files """
        delete_old_log_files()

    def delete(self):
        """ Delete RDM records by recid (to_delete.log) """
        delete_from_list()

    def uuid(self):
        """ Push to RDM all uuids that are in to_transfer.log """
        add_uuids = AddFromUuidList()
        add_uuids.add_from_uuid_list()

    def duplicates(self):
        """ Find and delete RDM duplicate records """
        rdm_duplicates()

    def delete_all(self):
        """ Delete all RDM records """
        delete_all_records()

    def owner(self):
        """ Gets from pure all the records related to a certain user recid,
            afterwards it modifies/create RDM records accordingly."""
        rdm_owners = RdmOwners()
        rdm_owners.rdm_owner_check()

    def owner_orcid(self):
        """ Gets from pure all the records related to a certain user orcid,
            afterwards it modifies/create RDM records accordingly."""
        rdm_owners = RdmOwners()
        rdm_owners.rdm_owner_by_orcid()

    def owners_list(self):
        """ Gets from RDM all record uuids, recids and owners """
        get_rdm_record_owners()

    def rdm_group_split(self, old_id, new_ids):
        """ Split a single group into moltiple ones """
        # rdm_group_split(self, old_id, new_ids)
        rdm_groups = RdmGroups()
        rdm_groups.rdm_group_split(old_id, new_ids)

    def rdm_group_merge(self, old_ids, new_id):
        """ Merges multiple groups into a single one """
        # rdm_group_merge(self, old_ids, new_id)
        rdm_groups = RdmGroups()
        rdm_groups.rdm_group_merge(old_ids, new_id)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Pure synchronizer 1.0')
    docopt_instance = shell_interface()

# Calls the method given in the arguments
method_call(docopt_instance, arguments)
