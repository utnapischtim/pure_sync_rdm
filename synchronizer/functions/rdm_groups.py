from functions.general_functions import db_query, add_spaces, update_rdm_record, rdm_get_metadata_by_query

#   ---         ---         ---
def rdm_create_group(shell_interface: object, group_externalId: str, group_name: str):

    response = db_query(shell_interface, f"SELECT * FROM accounts_role WHERE name = '{group_externalId}'")

    message = f'\tRDM group          - '

    if not response:
        message += 'Not found        - '

    elif len(response) == 1:
        message += 'Found            - '
        
    elif len(response) > 1:                                                                         #  TEMPORARY
        print(f'Group in database {len(response)} times - {group_externalId} !!!!!!!')              #  TEMPORARY

    message += f'externalId:  {add_spaces(group_externalId)}  - {group_name}'
    print(message)

    if not response:
                                                            # Known issue related to the system path at execution time
        group_name = group_name.replace('(', '\(')
        group_name = group_name.replace(')', '\)')
        group_name = group_name.replace(' ', '_')
        command = f'pipenv run invenio roles create {group_externalId} -d {group_name}'
        response = shell_interface.os.system(command)

        if response != 0:
            print(f'Warning - Creating group response: {response}')

#   ---         ---         ---
def rdm_add_user_to_group(shell_interface: object, user_id: int, group_externalId: str):

    # Get user's rdm email
    user_email = db_query(shell_interface, f"SELECT email FROM accounts_user WHERE id = {user_id}")[0][0]

    # Get group id
    query = f"SELECT id FROM accounts_role WHERE name = '{group_externalId}'"
    response = db_query(shell_interface, query)

    if not response:
        # If the group does not exist then creates it
        rdm_create_group(shell_interface, group_externalId)
        # Repeats the query to get the group id
        group_id = db_query(shell_interface, query)

    group_id = response[0][0]

    # Checks if match already exists
    response = db_query(shell_interface, f"SELECT * FROM accounts_userrole WHERE user_id = {user_id} AND role_id = {group_id}")

    if response:
        print(f'\tRDM user in group  - User id: {add_spaces(user_id)}   -                     - Already belongs to group {group_externalId} (id {group_id})')
        return True

    # Adds user to group
    command = f'pipenv run invenio roles add {user_email} {group_externalId}'
    response = shell_interface.os.system(command)
    if response != 0:
        print(f'Warning - Creating group response: {response}')


#   ---         ---         ---
def rdm_group_split(shell_interface: object, old_id: str, new_id_1: str, new_id_2: str):

    """ 
    - remove users from old account_role
    - delete old account_role
    - create new accounts_roles
    - add users to new account_roles
    - modify record: 
        . groupRestrictions
        . managingOrganisationUnit (if necessary)
        . organisationUnits
        . contributors organisationUnit (should that be added??)
    """

    print(f'Old id: {old_id} - New ids: {new_id_1}, {new_id_2}')


    # - Remove users from old account_role -
    # Get all users in group
    user_email = db_query(shell_interface, f"SELECT email FROM accounts_user WHERE id = {user_id}")[0][0]

    # command = f'pipenv run invenio roles add {user_email} {group_externalId}'
    # response = shell_interface.os.system(command)
    # if response != 0:
    #     print(f'Warning - Creating group response: {response}')





    # - Delete old account_role -

    # - Create new accounts_roles -

    # - Add users to new account_roles -





    # # - Modify record -
    # # Get from RDM all records with old group
    # response = rdm_get_metadata_by_query(shell_interface, old_id)

    # resp_json = shell_interface.json.loads(response.content)
    # total_items = resp_json['hits']['total']
    # if total_items == 0:
    #     print(f'No items with group_id {old_id}')
    # print(f'Total items: {total_items}')


    return


#   ---         ---         ---
def rdm_group_merge(shell_interface: object, old_id_1: str, old_id_2: str, new_id: str):
    print('rdm_group_merge')
    return

