import os
from PTR_1 import pureToInvenio

dirpath = os.path.dirname(os.path.abspath(__file__))
retrans_data = open(dirpath + '/reports/to_re_transfer.log', 'r')

# Create instance
inst_pti = pureToInvenio()

uuid = retrans_data.readline()
cnt = 0
while uuid:
    cnt += 1
    print('\nuuid: ' + uuid.strip())
    
    inst_pti.get_pure_by_id(uuid.strip())

    uuid = retrans_data.readline()

if cnt == 0:    print('\n- Nothing to re-transmit -\n')
else:           print(f'\n{cnt} records re-transmitted\n')


# uuid = '3e5bc032-716b-4e4b-8e59-fe202e9e9596'       # TEMP
# # uuid = '06f9e00f-ca16-4db5-bdf8-d13bb3235788'     # TEMP
# inst_pti.get_pure_by_id(uuid)                       # TEMP