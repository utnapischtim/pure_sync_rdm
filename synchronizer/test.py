# import os
# response = os.system('pipenv run invenio roles create some_group4') 
# print(f'response: {response}')

# from functions.general_functions import bcolors
# print(bcolors.BLUE + "Warning: No active frommets remain. Continue?" + bcolors.END)

# import yaml
# with open("test.yml", 'r') as stream:
#     try:
#         print(yaml.safe_load(stream)['services']['db']['environment'][0])
#     except yaml.YAMLError as exc:
#         print(exc)


user_ip = '127.0.2.11'

ip_range = [['127.0.0.3', '127.0.0.8'], ['127.0.1.10', '127.0.2.18']]

in_range = False

for range in ip_range:

    ip_start = range[0]
    ip_end   = range[1]

    if user_ip > ip_start and user_ip < ip_end:
        in_range = True


print(f'\nIn range: {in_range}\n')