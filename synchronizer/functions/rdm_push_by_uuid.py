from setup                          import *
from functions.rdm_push_record      import rdm_push_record
from functions.general_functions    import initialize_count_variables

def rdm_push_by_uuid(shell_interface):

    initialize_count_variables(shell_interface)

    # read to_transfer.log
    file_name = f'{shell_interface.dirpath}/data/to_transfer.txt'
    uuids = open(file_name, 'r').readlines()

    if len(uuids) == 0:
        print('\nThere is nothing to push.\n')
        return

    for uuid in uuids:
        if (len(uuid) != 36):
            print('Invalid uuid lenght.\n')
            continue
        
        rdm_push_record(shell_interface, uuid)

    return
