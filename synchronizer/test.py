file_name = f'./synchronizer/data/pure_rdm_user_id.txt'
file_data = open(file_name).readlines()

for i in file_data:
    print(i.split(' ')[0])