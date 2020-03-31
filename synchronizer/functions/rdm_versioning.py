from setup                          import *
from functions.general_functions    import rdm_get_uuid_metadata, add_spaces

def rdm_versioning(shell_interface: object, uuid: str):
    response = rdm_get_uuid_metadata(shell_interface, uuid)

    if response.status_code == 429:
        shell_interface.time.sleep(wait_429)
        return False

    open(f'{shell_interface.dirpath}/data/temporary_files/rdm_get_uuid_metadata.json', "wb").write(response.content)

    resp_json = shell_interface.json.loads(response.content)
    
    message = '\tMetadata Version   - '

    total_recids = resp_json['hits']['total']

    if total_recids == 0:
        # If there are no records with the same uuid means it is the first one (version 1)
        metadata_version = 1
        message += 'Record NOT found - Metadata version: 1'

    else:
        rdm_metadata = resp_json['hits']['hits'][0]['metadata']
        # open(f'{shell_interface.dirpath}/data/temporary_files/version1.json', "w").write(shell_interface.json.dumps(rdm_metadata))
        # open(f'{shell_interface.dirpath}/data/temporary_files/version2.json', "w").write(shell_interface.json.dumps(shell_interface.item))

        # --------------------------
        # 1 - Getting records from pages (when populating RDM for the first time) there should be no versioning required
        # 2 - When getting records from pure 'changes' endpoint, they will have some changes (no need to compare it)
        #     So, is it necessary 'check_metadata_differences' ?????

        # # Checks if the record metadata from pure is the same as the one already in RDM
        # check_metadata_differences(rdm_metadata, shell_interface.item)
        # --------------------------

        # Gets metadata_version from RDM
        metadata_version = rdm_metadata['metadataVersion']

        # Increase by one for new version
        message += f'Found record     - Current ver.:{add_spaces(metadata_version)}  - New version: {metadata_version + 1}'

        metadata_version += 1
    
    print(message)
    return metadata_version



def check_metadata_differences(data_rdm, data_pure):

    # RDM path + Pure path
    matches = [
        [['title'], ['title']],
        [['recid'], ['recid']]
    ]

    for paths in matches:
        
        # RDM value
        rdm_value = None
        for i in paths[0]:
            rdm_value = data_rdm[i]
        print(rdm_value)
        
        # Pure value
        pure_value = None
        for i in paths[1]:
            pure_value = data_rdm[i]

        print(pure_value)

    return