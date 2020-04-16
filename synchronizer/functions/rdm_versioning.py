from setup                          import *
from functions.general_functions    import rdm_get_metadata_by_query, add_spaces, add_to_full_report

def rdm_versioning (shell_interface: object, uuid: str):
    response = rdm_get_metadata_by_query(shell_interface, uuid)

    if response.status_code == 429:
        shell_interface.time.sleep(wait_429)
        return False

    resp_json = shell_interface.json.loads(response.content)
    
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
                print(f" VERSIONING - Different uuid {rdm_metadata['uuid']}")
                continue
            
            # Add recid to listed versions
            metadata_versions.append(item['id'])

            # Get the latest version
            if 'metadataVersion' in rdm_metadata and not metadata_version:
                metadata_version = rdm_metadata['metadataVersion']
                continue

        message += f'Current ver.:{add_spaces(metadata_version)}  - New version: {metadata_version + 1}'        

    add_to_full_report(shell_interface, message)

    return [metadata_version, metadata_versions]