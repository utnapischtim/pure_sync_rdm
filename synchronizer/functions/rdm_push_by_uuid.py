from setup                          import *
from functions.rdm_push_record      import rdm_push_record
from functions.general_functions    import initialize_count_variables

def rdm_push_by_uuid(shell_interface):

    initialize_count_variables(shell_interface)
    shell_interface.count_http_responses = {}

    # # read to_transfer.log
    # file_name = f'{shell_interface.dirpath}/data/to_transfer.txt'
    # uuids = open(file_name, 'r').readlines()

    # if len(uuids) == 0:
    #     print('\nThere is nothing to push.\n')
    #     return

    # for uuid in uuids:
    #     uuid = uuid.split('\n')[0]
    #     if (len(uuid) != 36):
    #         print('Invalid uuid lenght.')
    #         continue
        
    #     rdm_push_record(shell_interface, uuid)
    # return


    rdm_push_record(shell_interface, '0ed3060c-49de-4b0e-83a9-90ca1a078c37')    # TEMP!!!!!!!!!!!!!!!!!