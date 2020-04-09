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

d = {'kk': 'vv', 'k2': 'v2'}

for i in d:
    print(i)