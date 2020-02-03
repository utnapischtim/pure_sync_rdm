import os
from PTR_7 import pureToInvenio

dirpath = os.path.dirname(os.path.abspath(__file__))
retrans_data = open(dirpath + '/reports/to_re_transfer.log', 'r')

# Create instance
inst_pti = pureToInvenio()

uuid = retrans_data.readline()
cnt = 0
while uuid:
    cnt += 1
    print(uuid.strip())
    
    inst_pti.get_pure_by_id(uuid.strip())

    uuid = retrans_data.readline()

if cnt == 0:    print('\n- Nothing to re-transmit -\n')