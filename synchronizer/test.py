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


a = [{'externalId': '2372346', 'name': 'Institu', 'uuid': 'b9fadcac9bca87'}, {'externalId': '2376', 'name': 'Institu', 'uuid': 'b9fadcac9b4444444444ca87'}]

for i in a:
    if i['externalId'] == '2376':
        a.remove(i)

print(a)