from setup                          import *
from functions.rdm_push_record      import rdm_push_record
from functions.general_functions    import initialize_count_variables
from functions.general_functions    import add_to_full_report

def rdm_push_by_uuid(shell_interface):

    initialize_count_variables(shell_interface)
    shell_interface.count_http_responses = {}

    # read to_transfer.log
    file_name = f'{dirpath}/data/to_transfer.txt'
    uuids = open(file_name, 'r').readlines()

    if len(uuids) == 0:
        add_to_full_report('\nThere is nothing to transfer.\n')
        return

    for uuid in uuids:
        uuid = uuid.split('\n')[0]
        if (len(uuid) != 36):
            add_to_full_report('Invalid uuid lenght.')
            continue
        
        rdm_push_record(shell_interface, uuid)
    return