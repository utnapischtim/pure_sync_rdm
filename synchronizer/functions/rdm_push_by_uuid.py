from setup import *

def rdm_push_by_uuid(my_prompt):

    from functions.rdm_push_record import rdm_push_record

    # read to_transfer.log
    retrans_data = open(my_prompt.dirpath + '/data/to_transfer.txt', 'r')

    uuid_row = retrans_data.readline()
    
    while uuid_row:
        
        uuid = uuid_row.strip()
        if (len(uuid) != 36):
            print('Invalid uuid lenght.\n')
            uuid_row = retrans_data.readline()
            continue
        
        #   ---     ---
        rdm_push_record(my_prompt, uuid)
        #   ---     ---
        
        uuid_row = retrans_data.readline()

    return
