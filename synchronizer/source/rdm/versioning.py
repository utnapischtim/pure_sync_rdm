import json
from source.general_functions       import add_spaces
from source.reports                 import Reports
from source.rdm.requests            import Requests

def rdm_versioning ():
    """ Gives the version to use for a new record and old versions of the same uuid """

    report   = Reports()
    rdm_requests = Requests()
    
    # Request
    response = rdm_requests.get_rdm_metadata_by_query(uuid)

    resp_json = json.loads(response.content)
    
    message = f'\tRDM metadata version  - {response} - '

    total_recids = resp_json['hits']['total']
    all_metadata_versions = []

    if total_recids == 0:
        # If there are no records with the same uuid means it is the first one (version 1)
        new_version = 1
        report.add(['console'], f'{message}Record NOT found    - Metadata version: 1')
        return [new_version, all_metadata_versions]


    new_version = None
    
    # Iterates over all records in response
    for item in resp_json['hits']['hits']:
        rdm_metadata = item['metadata']

        # If a record has a differnt uuid than it will be ignored
        if uuid != rdm_metadata['uuid']:
            report.add(['console'], f" VERSIONING - Different uuid {rdm_metadata['uuid']}")
            continue

        # Get the latest version
        if 'metadataVersion' in rdm_metadata and not new_version:
            new_version = rdm_metadata['metadataVersion'] + 1
        
        # Add recid to listed versions (old versions)
        recid           = item['id']
        creation_date   = item['created'].split('T')[0]
        version         = str(rdm_metadata['metadataVersion'])
        all_metadata_versions.append([recid, version, creation_date])

    
    # In case the record has no metadataVersion
    if not new_version:
        message += f'Vers. not specified - New metadata version: 1'
        new_version = 1
    else:
        # message += f'Current ver.:     6 - New version: 6'   
        # message += f'Current ver.: {add_spaces(new_version)} - New version: {new_version}'  
        count_old_versions = add_spaces(len(all_metadata_versions))
        message += f'Older versions{count_old_versions} - New version: {new_version}'        

    report.add(['console'], message)

    return [new_version, all_metadata_versions]