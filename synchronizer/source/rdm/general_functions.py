import requests
import json
from setup                          import versioning_running, rdm_host_url
from source.general_functions       import add_spaces
from source.rdm.requests            import Requests
from source.reports                 import Reports
from source.rdm.delete_record       import Delete

rdm_requests = Requests()
reports = Reports()
delete  = Delete()
    

def get_recid(uuid: str):
    """
    1 - to check if there are duplicates
    2 - to delete duplicates
    3 - to add the record uuid and recid to all_rdm_records.txt
    4 - gets the last metadata_version
    """

    # # The following function needs to be imported localy to avoid 'circular imports'
    # from source.rdm.delete_record            import delete_record

    """ KNOWN ISSUE: if the applied restriction in invenio_records_permissions (for admin users)
                     do not allow to read the record then it will not be listed """

    response = rdm_requests.get_rdm_metadata_by_query(uuid)

    resp_json = json.loads(response.content)

    total_recids = resp_json['hits']['total']
    if total_recids == 0:
        # If there are no records with the same uuid means it is the first one (version 1)
        return False

    # Iterate over all records with the same uuid
    # The first record is the most recent (they are sorted)
    count = 0
    for item in resp_json['hits']['hits']:
        count += 1

        recid = item['metadata']['recid']
        
        if count == 1:
            # URLs to be transmitted to Pure if the record is successfuly added in RDM      # TODO TODO TODO TODO TODO 
            api_url             = f'{rdm_host_url}api/records/{recid}'
            landing_page_url    = f'{rdm_host_url}records/{recid}'
            newest_recid = recid

            report = f'\tRDM get recid         - {response} - Total:       {add_spaces(total_recids)}  - {api_url}'
            reports.add(['console'], report)

        else:
            # If versioning is running then it is not necessary to delete older versions of the record
            if not versioning_running:
                # Duplicate records are deleted
                response = delete.record(recid)

                # if response:
                #     global_counters['delete']['success'] += 1
                # else:
                #     global_counters['delete']['error'] += 1

    return newest_recid


#   ---         ---         ---
def get_userid_from_list_by_externalid(external_id: str, file_data: list):

    for line in file_data:
        line = line.split('\n')[0]
        line = line.split(' ')

        # Checks if at least one of the ids match
        if external_id == line[2]:
            user_id         = line[0]
            user_id_spaces  = add_spaces(user_id)

            report = f'\tRDM owner list        -                  - User id:     {user_id_spaces}  - externalId: {external_id}'
            reports.add(['console'], report)

            return user_id


#   ---         ---         ---
def update_rdm_record(data: str, recid: str):

    response = rdm_requests.rdm_put_metadata(recid, data)

    url = f'{rdm_host_url}api/records/{recid}'
    reports.add(['console'], f'\tRecord update         - {response} - {url}')

    return response

