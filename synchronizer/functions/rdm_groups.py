from functions.general_functions import db_query

def rdm_create_group(shell_interface: object, group_name: str):

    response = db_query(shell_interface, f"SELECT * FROM accounts_role WHERE name = '{group_name}'")

    if len(response) == 0:
        print(f'\tGroup  NOT in database. Creating it   - {group_name}')

        command = f'pipenv run invenio roles create {group_name}'
        response = shell_interface.os.system(command)
        if response != 0:
            print(f'Warning - Creating group response: {response}')

    elif len(response) == 1:
        print(f'\tGroup in database                     - {group_name}')
        
    elif len(response) > 1:
        print(f'\tGroup in database {len(response)} times             - {group_name}')


def rdm_add_user_to_group(shell_interface: object, user_id: int, group_name: str):

    # NEEDS TESTING - NEEDS TESTING - NEEDS TESTING - NEEDS TESTING - NEEDS TESTING - NEEDS TESTING - NEEDS TESTING - NEEDS TESTING - NEEDS TESTING

    # Get user's rdm email
    user_email = db_query(shell_interface, f"SELECT email FROM accounts_user WHERE id = {user_id}")[0][0]

    # Get group's id
    query = f"SELECT id FROM accounts_role WHERE name = '{group_name}'"
    response = db_query(shell_interface, query)

    if len(response) == 0:
        rdm_create_group(shell_interface, group_name)
        response = db_query(shell_interface, query)

    group_id = response[0][0]

    # Checks if match already exists
    response = db_query(shell_interface, f"SELECT * FROM accounts_userrole WHERE user_id = {user_id} AND role_id = {group_id}")

    if len(response) > 0:
        print(f'\tUser {user_email} (id {user_id}) already belongs to group {group_name} (id {group_id})')
        return True

    # Adds user to group
    command = f'pipenv run invenio roles add {user_email} {group_name}'
    response = shell_interface.os.system(command)
    if response != 0:
        print(f'Warning - Creating group response: {response}')

