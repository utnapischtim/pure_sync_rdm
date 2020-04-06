from setup                          import *
from functions.general_functions    import db_query, add_spaces, update_rdm_record, rdm_get_metadata_by_query

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
def rdm_group_split(shell_interface: object, old_group_externalId: str, new_groups_externalIds: list):

    """ 
    1 - Create new groups
    2 - Remove users from old group
    3 - Add users to new groups
    4 - Delete old group
    5 - Modify RDM record: 
        . groupRestrictions
        . managingOrganisationUnit (if necessary)
        . organisationUnits
    """

    print(f'\nOld group: {old_group_externalId} - New groups: {new_groups_externalIds}\n')

    # - - Create new accounts_roles - -
    for group_externalId in new_groups_externalIds:

        # Is the group name given or should I get it from pure?? ????????????????????????????????????????????????????????????????
        group_name = f'New group {group_externalId} random name'

        rdm_create_group(shell_interface, group_externalId, group_name)


    # - - Remove users from old account_role - -
    # - - Add users to new account_roles - -
    # Get group id
    query = f"SELECT id FROM accounts_role WHERE name = '{old_group_externalId}';"
    old_group_id = db_query(shell_interface, query)[0][0]
    print(f'\tOld group id:        {old_group_id}')

    # Get all users in old group
    query = f"SELECT user_id FROM accounts_userrole WHERE role_id = {old_group_id};"
    response = db_query(shell_interface, query)

    if not response:
        print('\tUsers in group:      None')
    else:
        print(f'\tUsers in group:      {len(response)}')
        for i in response:
            user_id = i[0]

            # Get user email
            user_email = get_user_email(user_id)

            # Remove user from old group
            group_remove_user(shell_interface, user_email, old_group_externalId)

            # Add user to new groups
            for new_group_externalId in new_groups_externalIds:
                group_add_user(shell_interface, user_email, new_group_externalId)


    # # - - Delete old account_role - -
    # #  NOT WORKING  !!!  NOT WORKING  !!!  NOT WORKING  !!!  NOT WORKING  !!!  NOT WORKING  !!!
    # #  MOST LIKELY PERMISSION RELATED ISSUE
    # response = db_query(shell_interface, f"DELETE FROM accounts_role WHERE name = '{old_group_externalId}';")
    # if response:
    #     print(response)
    #     print(f'Group {old_group_externalId} successfuly deleted')
    # #  NOT WORKING  !!!  NOT WORKING  !!!  NOT WORKING  !!!  NOT WORKING  !!!  NOT WORKING  !!!


    # - - Modify record - -
    # Get name and uuid of new organisationalUnits
    new_organisationalUnits_data = []
    for externalId in new_groups_externalIds:
        new_organisationalUnits_data.append(pure_get_organisationalUnit_data(shell_interface, externalId))

    # Get from RDM all records with old group
    response = rdm_get_metadata_by_query(shell_interface, old_group_externalId)

    resp_json = shell_interface.json.loads(response.content)
    total_items = resp_json['hits']['total']

    if total_items == 0:
        print('\tRDM group records:   None\n')
        return True
    
    print(f'\tRDM group records:   {total_items}')
    

    # Iterates over all records which include the old group
    for item in resp_json['hits']['hits']:
        item = item['metadata']

        recid = item['recid']
        print(f"\tRecid:               {rdm_api_url_records}api/records/{recid}")

        open(f'{shell_interface.dirpath}/data/temporary_files/t1.json', 'w').write(shell_interface.json.dumps(item))
        
        # Removes old organisationalUnit from organisationalUnits
        for i in item['organisationalUnits']:
            if i['externalId'] == old_group_externalId:
                item['organisationalUnits'].remove(i)

        # Adds new organisationalUnits
        for i in new_organisationalUnits_data:
            item['organisationalUnits'].append(i)

        # Change groups
        if old_group_externalId in item['groupRestrictions']:
            item['groupRestrictions'].remove(old_group_externalId)
        for i in new_groups_externalIds:
            item['groupRestrictions'].append(i)

        # KNOWN ISSUE: IT CAN HAVE ONLY ONE ORGANIZATION        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Change managingOrganisationalUnit
        item['managingOrganisationalUnit_name']       = new_organisationalUnits_data[0]['name']
        item['managingOrganisationalUnit_uuid']       = new_organisationalUnits_data[0]['uuid']
        item['managingOrganisationalUnit_externalId'] = new_organisationalUnits_data[0]['externalId']
        # KNOWN ISSUE: IT CAN HAVE ONLY ONE ORGANIZATION        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        open(f'{shell_interface.dirpath}/data/temporary_files/t2.json', 'w').write(shell_interface.json.dumps(item))
        record_json = shell_interface.json.dumps(item)

        update_rdm_record(shell_interface, record_json, recid)
        shell_interface.time.sleep(0.2)

    return


#   ---         ---         ---
def rdm_group_merge(shell_interface: object, old_groups_externalId: list, new_group_externalId: str):
    """ 
    1 - Create new group
    2 - Remove users from old groups
    3 - Add users to new group
    4 - Delete old groups
    5 - Modify RDM records: 
        . groupRestrictions
        . managingOrganisationUnit (if necessary)
        . organisationUnits
    """

    print(f'\nOld groups: {old_groups_externalId} - New group: {new_group_externalId}\n')

    # - - Create new accounts_roles - -
    # Is the group name given or should I get it from pure?? ????????????????????????????????????????????????????????????????
    group_name = f'New group {new_group_externalId} random name'
    rdm_create_group(shell_interface, new_group_externalId, group_name)

    # - - Remove users from old account_role - -
    # - - Add users to new account_roles - -
    # Get groups id
    old_group_ids = []
    for i in old_groups_externalId:
        id = db_query(shell_interface, f"SELECT id FROM accounts_role WHERE name = '{i}';")[0][0]
        old_group_ids.append(id)
    
    print(f'\tOld groups id:       {old_group_ids}')

    # Get all users in old groups
    for old_group_id in old_group_ids:
        old_group_users = db_query(shell_interface, f"SELECT user_id FROM accounts_userrole WHERE role_id = {old_group_id};")
        if not old_group_users:
            print('\tUsers in group:      None')
        else:
            print(f'\tUsers in group:      {len(old_group_users)}')
            for i in old_group_users:
                user_id = i[0]

                print(user_id)

    # REVIEW !!!!!!!!!!!!!!!!!!!!!
                # # Get user email
                # user_email = get_user_email(user_id)

                # # Remove user from old group
                # group_remove_user(shell_interface, user_email, old_group_externalId)

                # # Add user to new groups
                # for new_group_externalId in new_groups_externalIds:
                #     group_add_user(shell_interface, user_email, new_group_externalId)





#   ---         ---         ---
def pure_get_organisationalUnit_data(shell_interface: object, externalId: str):
    """ Get organisationalUnit name and uuid """

    # PURE REQUEST
    headers = {
        'Accept': 'application/json',
    }
    params = (
        ('page', '1'),
        ('pageSize', '1'),
        ('apiKey', pure_api_key),
    )
    url = f'{pure_rest_api_url}organisational-units/{externalId}/research-outputs'
    response = shell_interface.requests.get(url, headers=headers, params=params)

    # Add response content to pure_get_uuid_metadata.json
    file_response = f'{shell_interface.dirpath}/data/temporary_files/pure_get_uuid_metadata.json'
    open(file_response, 'wb').write(response.content)

    # Check response
    if response.status_code >= 300:
        print(response.content)

    # Load json
    data = shell_interface.json.loads(response.content)
    data = data['items'][0]['organisationalUnits']

    for organisationalUnit in data:
        if organisationalUnit['externalId'] == externalId:

            organisationalUnit_data = {}
            organisationalUnit_data['externalId'] = externalId
            organisationalUnit_data['uuid']       = organisationalUnit['uuid']
            organisationalUnit_data['name']       = organisationalUnit['names'][0]['value']

            return organisationalUnit_data



def group_remove_user(shell_interface, user_email, old_group_externalId):
    # Remove user from old group
    print('Remove user from old group')
    command = f'pipenv run invenio roles remove {user_email} {old_group_externalId}'
    response = shell_interface.os.system(command)
    if response != 0:
        print(f'Warning - Creating group response: {response}')

def group_add_user(shell_interface, user_email, new_group_externalId):
    # Add user to new groups
    print(f'\tAdding user to group {new_group_externalId}')
    command = f'pipenv run invenio roles add {user_email} {new_group_externalId}'
    response = shell_interface.os.system(command)
    if response != 0:
        print(f'Warning - Creating group response: {response}')

def get_user_email(user_id):
    # Get user email
    query = f"SELECT email FROM accounts_user WHERE id = {user_id};"
    user_email = db_query(shell_interface, query)[0][0]
    print(f'\tUser id: {user_id}    - Email:             {user_email}')
    return user_email