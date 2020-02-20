from functions.get_from_pure            import get_from_pure
from functions.get_from_rdm             import get_from_rdm
from functions.rdm_push_byUuid          import rdm_push_byUuid
from functions.delete_record            import delete_record

def intersection_pure_rdm(self):
    try:
        print('\n---   ---   ---\nFIND MISSING\n')
        # Read RDM         
        get_from_rdm(self)                                                # TAKES TOO LONG ???????????????????????????
        file_name = self.dirpath + '/reports/full_comparison/rdm_uuids.log'
        uuid_rdm = open(file_name, 'r').readlines()

        # Read Pure
        get_from_pure(self)                                                # TAKES TOO LONG ???????????????????????????
        file_name = self.dirpath + '/reports/full_comparison/pure_uuids.log'
        uuid_pure = open(file_name, 'r').readlines()

        # TO ADD --
        # empty to_transfer.log
        toTrans_fileName = self.dirpath + '/data/to_transfer.txt'
        open(toTrans_fileName, 'w').close()
            
        # Find missing records in RDM
        cnt_m = 0
        cnt_t = 0
        missing_in_rdm = ''
        for i in uuid_pure:
            if i not in uuid_rdm:
                cnt_m += 1
                missing_in_rdm += i
            else:
                cnt_t += 1

        open(toTrans_fileName, "a").write(missing_in_rdm)
        print(f'{cnt_t}\trecords intersect')
        print(f'{cnt_m}\trecords to add in RDM\n')
            
        # TO DELETE --
        # empty to_transfer.log
        toTrans_fileName = self.dirpath + '/data/to_delete.txt'
        open(toTrans_fileName, 'w').close()

        # Find records to be deleted from RDM
        cnt_d = 0
        cnt_t = 0
        rdm_delete = ''
        for i in uuid_rdm:
            if i not in uuid_pure:
                cnt_d += 1
                rdm_delete += i
            else:
                cnt_t += 1

        open(toTrans_fileName, "a").write(rdm_delete)
        print(f'{cnt_t}\trecords intersect')
        print(f'{cnt_d}\trecords to be deleted from RDM\n')

        # Push data to RDM
        rdm_push_byUuid(self, 'full_comp')

        # Delete from RDM
        delete_record(self)

    except:
        print('\n---   !!!   Error in find_missing   !!!   ---\n')