from setup                          import *
from functions.rdm_push_record      import rdm_push_record
from functions.general_functions    import initialize_count_variables

def rdm_push_by_uuid(shell_interface):

    initialize_count_variables(shell_interface)

    # read to_transfer.log
    retrans_data = open(shell_interface.dirpath + '/data/to_transfer.txt', 'r')

    uuid_row = retrans_data.readline()
    
    while uuid_row:
        
        uuid = uuid_row.strip()
        if (len(uuid) != 36):
            print('Invalid uuid lenght.\n')
            uuid_row = retrans_data.readline()
            continue
        
        #   ---     ---
        rdm_push_record(shell_interface, uuid)
        #   ---     ---
        
        uuid_row = retrans_data.readline()

    return
