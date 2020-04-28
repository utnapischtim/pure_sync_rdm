from source.general_functions   import add_to_full_report, dirpath
from source.rdm.delete_record   import delete_record

def rdm_duplicate_records():

    file_name = data_files_name['all_rdm_records']
    all_records = open(file_name, 'r').readlines()                       

    temp_arr = []
    count_deleted = 0

    for record in reversed(all_records):

        record_split = record.split(' ')
        uuid = record_split[0]
        recid = record_split[1].strip('\n')

        if uuid in temp_arr:
            count_deleted += 1
            delete_record(recid)
            continue

        temp_arr.append(uuid)

    if count_deleted == 0:
        report = '\nThere are no duplicate records to delete\n'
        add_to_full_report(report)

    report = f'Total items: {len(all_records)}\nDeleted: {count_deleted}\n'
    add_to_full_report(report)

        
        

