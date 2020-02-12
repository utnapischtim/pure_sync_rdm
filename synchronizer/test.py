import json
import os

dirpath = os.path.dirname(os.path.abspath(__file__))

# Read Pure
file_name = dirpath + '/reports/full_comparison/t_pure.log'
uuid_pure = open(file_name, 'r').readlines()

# Read RDM
file_name = dirpath + '/reports/full_comparison/t_rdm.log'
uuid_rdm = open(file_name, 'r').readlines()
    
# Find missing records
missing_in_rdm = []
for i in uuid_pure:
    if i not in uuid_rdm:
        missing_in_rdm.append(i.split('\n')[0])

print(missing_in_rdm)