file_name = "./reports/full_comparison/rdm_uuids_recids.log"
with open(file_name, 'r') as f:
    lines = f.read().splitlines()
    for line in lines:
        split = line.split(' ')
        uuid  = split[0]
        recid = split[1]
        print(f'{uuid} -|- {recid}')