import os
response = os.system('pipenv run invenio roles create some_group4')
print(f'response: {response}')

# from functions.general_functions import bcolors
# print(bcolors.BLUE + "Warning: No active frommets remain. Continue?" + bcolors.END)
