from setup                          import *
from functions.general_functions    import rdm_get_metadata_by_query, add_spaces, add_to_full_report

def rdm_versioning(shell_interface: object, uuid: str):
    response = rdm_get_metadata_by_query(shell_interface, uuid)

    if response.status_code == 429:
        shell_interface.time.sleep(wait_429)
        return False

    resp_json = shell_interface.json.loads(response.content)
    
    message = f'\tRDM metadata version  - {response} - '

    total_recids = resp_json['hits']['total']

    if total_recids == 0:
        # If there are no records with the same uuid means it is the first one (version 1)
        metadata_version = 1
        message += f'Record NOT found    - Metadata version: 1'

    else:
        rdm_metadata = resp_json['hits']['hits'][0]['metadata']
        # open(f'{shell_interface.dirpath}/data/temporary_files/version1.json', "w").write(shell_interface.json.dumps(rdm_metadata))
        # open(f'{shell_interface.dirpath}/data/temporary_files/version2.json', "w").write(shell_interface.json.dumps(shell_interface.item))

        # 1 - Getting records from pages (when populating RDM for the first time) there should be no versioning required
        # 2 - When getting records from pure 'changes' endpoint, they will have some changes (no need to compare it)
        #     So, it is probably not necessary to 'check_metadata_differences'

        if 'metadataVersion' not in rdm_metadata:
            return False

        # Gets metadata_version from RDM
        metadata_version = rdm_metadata['metadataVersion']

        # Increase by one for new version
        message += f'Current ver.:{add_spaces(metadata_version)}  - New version: {metadata_version + 1}'

        metadata_version += 1
    
    add_to_full_report(shell_interface, message)
    return metadata_version