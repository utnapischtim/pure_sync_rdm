import os
response = os.system('pipenv run invenio roles add viertel@invenio.org some_group2')
print(f'response: {response}')


