def find_rdm_duplicates(self):
    try:
        from functions.delete_record import delete_record

        print('---   ---   ---\nFIND RDM DUPLICATES\n\nDuplicates:\n')

        # Read Pure
        file_name = self.dirpath + '/reports/full_comparison/rdm_uuids.log'
        uuid_rdm = open(file_name, 'r').readlines()
        # Read Pure
        file_name = self.dirpath + '/reports/full_comparison/rdm_uuids_recids.log'
        uuidRecid_rdm = open(file_name, 'r').readlines()
        # empty to_delete.log
        toDel_fileName = self.dirpath + '/data/to_delete.txt'
        open(toDel_fileName, 'w').close()                         

        temp_arr = []
        cnt = 0
        dup_recid = []

        for uuid in reversed(uuid_rdm):
            cnt_dup = 0
            if uuid not in temp_arr:        # not duplicated
                temp_arr.append(uuid)
            else:                           # duplicated
                # find the corresponding recid to the duplicated uuid
                for i in reversed(uuidRecid_rdm):
                    split = i.split(' ')
                    uuid = uuid.split('\n')[0]
                    recid = split[1]

                    if split[0] == uuid:
                        cnt_dup += 1
                        if recid not in dup_recid and cnt_dup > 1:
                            ri = recid.split('\n')[0]
                            print(f"{uuid}\t{ri}")
                            dup_recid.append(recid)
                            cnt += 1

        if cnt == 0:
            print('- There are no duplicates\n')
            report = f"\nDelete - {self.date.today()} - success\nThere are no duplicates\n"
            
            date_today = str(self.date.today())
            open(f'{self.dirpath}/reports/{date_today}_updates.log', "a").write(report)
            
            return

        else:
            print(f'\nTot {cnt} duplicates\n')

            dup_recid_str = ''
            for i in dup_recid:
                dup_recid_str += i

            open(toDel_fileName, "a").write(dup_recid_str)

            delete_record(self)

    except:
        print('\n---   !!!   Error in find_rdm_duplicates   !!!   ---\n')