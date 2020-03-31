from setup                          import *
from functions.general_functions    import rdm_get_uuid_metadata

def rdm_versioning(shell_interface: object, uuid: str):
    response = rdm_get_uuid_metadata(shell_interface, uuid)

    if response.status_code == 429:
        shell_interface.time.sleep(wait_429)
        return False

    open(f'{shell_interface.dirpath}/data/temporary_files/rdm_get_uuid_metadata.json', "wb").write(response.content)

    resp_json = shell_interface.json.loads(response.content)

    total_recids = resp_json['hits']['total']
    if total_recids == 0:
        # If there are no records with the same uuid means it is the first one (version 1)
        return 1

    metadata_version = resp_json['hits']['hits'][0]['metadata']['metadataVersion']
    return metadata_version + 1

    