from functions.delete_record import delete_record

def delete_all_records(self):

    file_name = self.dirpath + "/reports/full_comparison/rdm_uuids_recids.log"
    toDelete_str = ''

    with open(file_name, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            toDelete_str += line.split(' ')[1] + '\n'
    
    toDel_fileName = self.dirpath + '/data/to_delete.txt'
    open(toDel_fileName, "a").write(toDelete_str)

    delete_record(self)