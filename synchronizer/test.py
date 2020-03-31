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


j1 = {
    "pureId": "1097026",
    "publicationDatePure": "2008"
}
j2 = {
    "pureId": "1097026",
    "publicationDatePure": "200d8"
}
if j1 == j2:
    print('uguali')