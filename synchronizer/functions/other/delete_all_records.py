from functions.delete_record import delete_reading_txt

def delete_all_records(my_prompt):

    file_name = my_prompt.dirpath + "/data/all_rdm_records.txt"
    toDelete_str = ''

    with open(file_name, 'r') as f:
        lines = f.read().splitlines()
        
        for line in lines:
            recid = line.split(' ')[1]
            toDelete_str += f'{recid}\n'
    
    toDel_fileName = my_prompt.dirpath + '/data/to_delete.txt'
    open(toDel_fileName, "a").write(toDelete_str)

    delete_reading_txt(my_prompt)