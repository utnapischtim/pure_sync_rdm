from functions.delete_record import delete_record

def rdm_duplicates(shell_interface):

    print('---   ---   ---\nFIND RDM DUPLICATES\n\nDuplicates:\n')

    # Read Pure
    file_name = shell_interface.dirpath + '/data/all_rdm_records.txt'
    all_records = open(file_name, 'r').readlines()                       

    temp_arr = []
    count_deleted = 0

    for record in reversed(all_records):

        record_split = record.split(' ')
        uuid = record_split[0]
        recid = record_split[1].strip('\n')

        if uuid in temp_arr:
            count_deleted += 1
            delete_record(shell_interface, recid)
            continue

        temp_arr.append(uuid)

    print(f'\nTotal items: {len(all_records)}\nDeleted: {count_deleted}\n')

        
        

