from functions.delete_record            import delete_record
from functions.general_functions        import add_to_full_report

def rdm_duplicates(shell_interface):

    file_name = f'{shell_interface.dirpath}/data/all_rdm_records.txt'
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

    if count_deleted == 0:
        report = '\nThere are no duplicate records to delete\n'
        add_to_full_report(shell_interface, report)

    report = f'Total items: {len(all_records)}\nDeleted: {count_deleted}\n'
    add_to_full_report(shell_interface, report)

        
        

