
def intersection_pure_rdm(self):
    try:
        print('\n---   ---   ---\nFIND MISSING\n')
        # Read RDM
        file_name = self.dirpath + '/reports/full_comparison/rdm_uuids.log'
        uuid_rdm = open(file_name, 'r').readlines()

        # Read Pure
        file_name = self.dirpath + '/reports/full_comparison/pure_uuids.log'
        uuid_pure = open(file_name, 'r').readlines()
            
        # Find missing records
        cnt_m = 0
        cnt_t = 0
        missing_in_rdm = ''
        for i in uuid_pure:
            if i not in uuid_rdm:
                cnt_m += 1
                missing_in_rdm += i
            else:
                cnt_t += 1

        file_name = self.dirpath + '/reports/to_transfer.log'
        open(file_name, "a").write(missing_in_rdm)
        print(f'{cnt_t}\trecords intersect')
        print(f'{cnt_m}\trecords added to to_transfer.log\n')

    except:
        print('\n---   !!!   Error in find_missing   !!!   ---\n')