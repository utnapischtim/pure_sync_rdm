
from source.rdm.push_by_changes     import pure_get_changes
from source.rdm.push_by_page        import RunPages
from source.log_manager             import delete_old_log_files
from source.rdm.duplicate_records   import rdm_duplicate_records
from source.rdm.push_by_uuid        import AddFromUuidList
from source.rdm.delete_record       import delete_from_list
from source.rdm.owners              import RdmOwners, get_rdm_record_owners
from source.rdm.groups              import RdmGroups

class ShellInterface:
    
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
        rdm_duplicate_records()

    def owner(self):
        """ Gets from pure all the records related to a certain user recid,
            afterwards it modifies/create RDM records accordingly."""
        rdm_owners = RdmOwners()
        rdm_owners.rdm_owner_check()

    def owner_orcid(self):
        """ Gets from pure all the records related to a certain user orcid,
            afterwards it modifies/create RDM records accordingly."""
        rdm_owners = RdmOwners()
        rdm_owners.rdm_owner_check_by_orcid()

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

        

def method_call(docopt_instance: object, arguments: dict):

    if arguments['changes']:
        docopt_instance.changes()

    elif arguments['pages']:
        page_start = int(arguments['--pageStart'])
        page_end   = int(arguments['--pageEnd'])
        page_size  = int(arguments['--pageSize'])
        docopt_instance.pages(page_start, page_end, page_size)

    elif arguments['logs']:
        docopt_instance.logs()

    elif arguments['delete']:
        docopt_instance.delete()

    elif arguments['uuid']:
        docopt_instance.uuid()

    elif arguments['duplicates']:
        docopt_instance.duplicates()

    elif arguments['owner']:
        docopt_instance.owner()

    elif arguments['owner_orcid']:
        docopt_instance.owner_orcid()

    elif arguments['owners_list']:
        docopt_instance.owners_list()

    elif arguments['group_split']:
        old_id  = arguments['--oldGroup']
        new_ids = arguments['--newGroups'].split(' ')
        docopt_instance.rdm_group_split(old_id, new_ids)

    elif arguments['group_merge']:
        old_ids = arguments['--oldGroups'].split(' ')
        new_id  = arguments['--newGroup']
        docopt_instance.rdm_group_merge(old_ids, new_id)

