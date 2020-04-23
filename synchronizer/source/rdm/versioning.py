import json
from source.general_functions        import add_spaces, add_to_full_report
from source.rdm.general_functions    import rdm_get_metadata_by_query, too_many_rdm_requests_check

def rdm_versioning (uuid: str):
    response = rdm_get_metadata_by_query(uuid)

    # If the status_code is 429 (too many requests) then it will wait for some minutes
    if not too_many_rdm_requests_check(response):
        return False

    resp_json = json.loads(response.content)
    
    message = f'\tRDM metadata version  - {response} - '

    total_recids = resp_json['hits']['total']
    metadata_versions = []

    if total_recids == 0:
        # If there are no records with the same uuid means it is the first one (version 1)
        metadata_version = 1
        message += f'Record NOT found    - Metadata version: 1'

    else:
        metadata_version = None
        
        # Iterates over all records in response
        for item in resp_json['hits']['hits']:
            rdm_metadata = item['metadata']

            # If a record has a differnt uuid than it will be ignored
            if uuid != rdm_metadata['uuid']:
                add_to_full_report(f" VERSIONING - Different uuid {rdm_metadata['uuid']}")
                continue
            
            # Add recid to listed versions
            metadata_versions.append(item['id'])

            # Get the latest version
            if 'metadataVersion' in rdm_metadata and not metadata_version:
                metadata_version = rdm_metadata['metadataVersion']
                continue
        
        # In case the record has no metadataVersion
        if not metadata_version:
            message += f'Vers. not specified - New metadata version: 1'
            metadata_version = 1
        else:
            message += f'Current ver.:{add_spaces(metadata_version)}  - New version: {metadata_version + 1}'        

    add_to_full_report(message)

    return [metadata_version, metadata_versions]