import os
from PTR_1 import PureToRdm

try:
    dirpath = os.path.dirname(os.path.abspath(__file__))
    retrans_data = open(dirpath + '/reports/to_transfer.log', 'r')

    # Create instance
    inst_pti = PureToRdm()

    uuid = retrans_data.readline()
    cnt = 0
    while uuid:
        cnt += 1
        print('\nuuid: ' + uuid.strip())
        
        inst_pti.get_pure_by_id(uuid.strip())

        uuid = retrans_data.readline()

    if cnt == 0:    print('\n- Nothing to transmit -\n')
    else:           print(f'\n{cnt} records transmitted\n')
except:
    print('\n- Error in 2_uuid_transmit.py -\n')