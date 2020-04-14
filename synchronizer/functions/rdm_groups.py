from setup                          import *
from functions.general_functions    import db_query, add_spaces, update_rdm_record, rdm_get_metadata_by_query, add_to_full_report

#   ---         ---         ---
def rdm_create_group(shell_interface: object, group_externalId: str, group_name: str):

    response = db_query(shell_interface, f"SELECT * FROM accounts_role WHERE name = '{group_externalId}'")
    message   = f'\tRDM search group      -  ExtId:   {add_spaces(group_externalId)}  -'
    message_2 = f'          - {group_name[0:40]}'

    # If the group has already been created
    if response:
        print(f'{message} Found     {message_2}')
        return 'Already exists'

    report = f'{message} Not found {message_2}'
    add_to_full_report(shell_interface, report)

    group_name = group_name.replace('(', '\(')
    group_name = group_name.replace(')', '\)')
    group_name = group_name.replace(' ', '_')
    command = f'pipenv run invenio roles create {group_externalId} -d {group_name}'
    response = shell_interface.os.system(command)

    if response != 0:
        print(f'\tWarning - Creating group response: {response}')
        return f'Error: {response}'

    return 'Success'

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
    # Report
    current_time = shell_interface.datetime.now().strftime("%H:%M:%S")
    report_name = f'{shell_interface.dirpath}/reports/{shell_interface.date.today()}_groups.log'
    shell_interface.report_name = report_name
    report = f"""

--   --   --

{current_time} - RDM GROUP SPLIT -

Old group             - externalId: {old_group_externalId}
"""
    open(report_name, "a").write(report)
    print(f'\nOld group: {old_group_externalId} - New groups: {new_groups_externalIds}\n')

    # Get name and uuid of new groups
    new_groups_data = []

    for externalId in new_groups_externalIds:
        # Get group information
        response = pure_get_organisationalUnit_data(shell_interface, externalId)
        new_groups_data.append(response)

        report = f"\nNew group             - externalId: {externalId}   - {response['uuid']} - {response['name']}\n"
        open(report_name, "a").write(report)

        # Create new group
        response = rdm_create_group(shell_interface, externalId, response['name'])
        open(report_name, "a").write(f'New group creation    - {response}\n')

    # Get group id
    query = f"SELECT id FROM accounts_role WHERE name = '{old_group_externalId}';"
    old_group_id = db_query(shell_interface, query)[0][0]
    print(f'\tOld group             - Id: {old_group_id}')

    # Get all users in old group
    query = f"SELECT user_id FROM accounts_userrole WHERE role_id = {old_group_id};"
    response = db_query(shell_interface, query)

    report = 'Old group             - Number of users: '
    if not response:
        report += '0'
        print(f'\t{report}')
        open(report_name, "a").write(f'\n{report}\n')
    else:
        report += f'{len(response)}'
        print(f'\t{report}')
        open(report_name, "a").write(f'\n{report}\n')

        for i in response:

            user_id = i[0]

            # Get user email
            user_email = get_user_email(shell_interface, user_id)

            # Remove user from old group
            response = group_remove_user(shell_interface, user_email, old_group_externalId)

            for new_group_externalId in new_groups_externalIds:

                # Add user to new groups
                group_add_user(shell_interface, user_email, new_group_externalId, user_id)

    # DOESNT WORK - DOESNT WORK - DOESNT WORK - DOESNT WORK - DOESNT WORK - DOESNT WORK -
    # - - Delete old group - - 
    # Checks if there are still users in accounts_userrole that are related to the old group
    query = f"SELECT user_id FROM accounts_userrole WHERE role_id = '{old_group_id}';"
    response = db_query(shell_interface, query)
    if not response:
        response = db_query(shell_interface, f"DELETE FROM accounts_role WHERE name = '{old_group_externalId}';")
        if response:
            print(response)
            print(f'Group {old_group_externalId} successfuly deleted')
    if len(response) > 0:
        print(f'Warning: there are still users related to the old group -> {response}')
    # DOESNT WORK - DOESNT WORK - DOESNT WORK - DOESNT WORK - DOESNT WORK - DOESNT WORK -

    # - -               - -
    # - - Modify record - -

    # Get from RDM all old group's records
    response = rdm_get_metadata_by_query(shell_interface, old_group_externalId)

    resp_json = shell_interface.json.loads(response.content)
    total_items = resp_json['hits']['total']

    report = f"\nModify records - Group: {old_group_externalId} - Number records: {total_items}\n"
    open(report_name, "a").write(report)
    print(f'\t{report}')

    if total_items == 0:
        return True

    # Iterates over all old group records
    for item in resp_json['hits']['hits']:
        item = item['metadata']

        recid = item['recid']
        url = f'{rdm_api_url_records}api/records/{recid}'
        print(f"\tRecid:               {url}")

        # Removes old organisationalUnit from organisationalUnits
        for i in item['organisationalUnits']:
            if i['externalId'] == old_group_externalId:
                item['organisationalUnits'].remove(i)

        # Adds new organisationalUnits
        for i in new_groups_data:
            item['organisationalUnits'].append(i)

        # Change group restrictions
        if old_group_externalId in item['groupRestrictions']:
            item['groupRestrictions'].remove(old_group_externalId)
        for i in new_groups_externalIds:
            item['groupRestrictions'].append(i)

        # Change managingOrganisationalUnit
        if item['managingOrganisationalUnit_externalId'] == old_group_externalId:
            item['managingOrganisationalUnit_name']       = new_groups_data[0]['name']
            item['managingOrganisationalUnit_uuid']       = new_groups_data[0]['uuid']
            item['managingOrganisationalUnit_externalId'] = new_groups_data[0]['externalId']

        record_json = shell_interface.json.dumps(item)

        # Update record
        response = update_rdm_record(shell_interface, record_json, recid)

        current_time = shell_interface.datetime.now().strftime("%H:%M:%S")
        open(report_name, "a").write(f'{current_time} - {response} - {url}\n')

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
    # Report
    current_time = shell_interface.datetime.now().strftime("%H:%M:%S")
    shell_interface.report_name = report_name = f'{shell_interface.dirpath}/reports/{shell_interface.date.today()}_groups.log'

    report = f"\n\n--   --   --\n\n{current_time} - RDM GROUP MERGE -\n\n"
    open(report_name, "a").write(report)

    print(f'{report}Old groups: {old_groups_externalId}')

    # Get name and uuid of new organisationalUnit
    new_group_data = pure_get_organisationalUnit_data(shell_interface, new_group_externalId)

    report = f"New group             - externalId: {add_spaces(new_group_externalId)}   - {new_group_data['name']}\n"
    open(report_name, "a").write(report)

    # - - Create new group - -
    response = rdm_create_group(shell_interface, new_group_externalId, new_group_data['name'])
    open(report_name, "a").write(f'New group creation    - {response}\n')

    # Iterate over old groups
    for old_group_externalId in old_groups_externalId:

        print(f'\n\tGroup externalId: {old_group_externalId}')

        # Get group id
        query          = f"SELECT id, description FROM accounts_role WHERE name = '{old_group_externalId}';"
        response       = db_query(shell_interface, query)[0]
        old_group_id   = response[0]
        old_group_name = response[1]

        # Get all users id that are in this group
        query = f"SELECT user_id FROM accounts_userrole WHERE role_id = {old_group_id};"
        old_group_users = db_query(shell_interface, query)

        if not old_group_users:
            old_group_users = []
        
        report = f"\nOld group (id {add_spaces(old_group_id)})  - Number users: {add_spaces(len(old_group_users))}\
 - externalId:  {add_spaces(old_group_externalId)} - {old_group_name}\n"
        open(report_name, "a").write(report)
        print(report)
        
        for i in old_group_users:
            user_id = i[0]

            # Get user email
            user_email = get_user_email(shell_interface, user_id)

            # - - Remove user from old group - -
            response = group_remove_user(shell_interface, user_email, old_group_externalId)

            # - - Add user to new group - -
            group_add_user(shell_interface, user_email, new_group_externalId, user_id)


        # - - Delete old group - - 
        # ????????????????????????

    # - -                - -
    # - - Modify records - -

    print('\n- Modify records -')
    
    # Get from RDM all records with old groups
    for old_group_externalId in old_groups_externalId:
        
        # Get record metadata
        response = rdm_get_metadata_by_query(shell_interface, old_group_externalId)


        # fffff = f'{shell_interface.dirpath}/data/temporary_files/rdm_get_metadata_by_query.json'
        # with open(fffff) as json_file:
        #     resp_json = shell_interface.json.load(json_file)


        resp_json = shell_interface.json.loads(response.content)
        total_items = resp_json['hits']['total']

        report = f"\nModify records - Group: {old_group_externalId} - Number records: {total_items}\n"
        open(report_name, "a").write(report)
        print(f'\t{report}')

        if total_items == 0:
            continue
        
        # Iterates over all old group records
        for item in resp_json['hits']['hits']:

            item = item['metadata']
            recid = item['recid']

            url = f'{rdm_api_url_records}api/records/{recid}'
            print(f"\n\tRecid:               {url}")

            # + Organisational units +
            new_organisationalUnits_data = [new_group_data]

            for i in item['organisationalUnits']:
                if (i['externalId'] in old_groups_externalId or 
                    i['externalId'] == new_group_data['externalId']):
                    continue
                
                new_organisationalUnits_data.append(i)

            item['organisationalUnits'] = new_organisationalUnits_data

            # + Group restrictions +
            # Remove old group
            if old_group_externalId in item['groupRestrictions']:
                item['groupRestrictions'].remove(old_group_externalId)
            # Add new group
            if new_group_externalId not in item['groupRestrictions']:
                item['groupRestrictions'].append(new_group_externalId)

            # + Managing Organisational Unit +
            if item['managingOrganisationalUnit_externalId'] == old_group_externalId:
                item['managingOrganisationalUnit_name']       = new_group_data['name']
                item['managingOrganisationalUnit_uuid']       = new_group_data['uuid']
                item['managingOrganisationalUnit_externalId'] = new_group_data['externalId']

            record_json = shell_interface.json.dumps(item)

            # Update record
            response = update_rdm_record(shell_interface, record_json, recid)

            current_time = shell_interface.datetime.now().strftime("%H:%M:%S")
            report = f'{current_time} - {response} - {url}\n'
            open(report_name, "a").write(report)



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



def group_remove_user(shell_interface, user_email, group_name):
    
    # Get user id
    query = f"SELECT id FROM accounts_user WHERE email = '{user_email}';"
    user_id = db_query(shell_interface, query)[0][0]
    
    # Get group id
    query = f"SELECT id FROM accounts_role WHERE name = '{group_name}';"
    group_id = db_query(shell_interface, query)[0][0]
    
    # Check if the user is already in the group
    query = f"SELECT * FROM accounts_userrole WHERE user_id = {user_id} AND role_id = {group_id};"
    response = db_query(shell_interface, query)

    report =  f'Remove from group     - User id:      {add_spaces(user_id)} - Group:       {add_spaces(group_name)}'

    if not response:
        open(shell_interface.report_name, "a").write(f'{report} - Already removed from group\n')
        return True

    # Remove user from old group
    print('\tRemove user from old group')

    command = f'pipenv run invenio roles remove {user_email} {group_name}'
    response = shell_interface.os.system(command)

    if response != 0:
        print(f'Warning - Creating group response: {response}')
        open(shell_interface.report_name, "a").write(f'{report} - Error: {response}\n')
        return False

    open(shell_interface.report_name, "a").write(f'{report} - Success\n')
    return True


def group_add_user(shell_interface, user_email, new_group_externalId, user_id):
    
    # Get group id
    query = f"SELECT id FROM accounts_role WHERE name = '{new_group_externalId}';"
    group_id = db_query(shell_interface, query)[0][0]
    
    # Check if the user is already in the group
    query = f"SELECT * FROM accounts_userrole WHERE user_id = {user_id} AND role_id = {group_id};"
    response = db_query(shell_interface, query)

    report =  f'Add to group          - User id:      {add_spaces(user_id)} - Group:       {add_spaces(new_group_externalId)}'

    if response:
        return True

    # Add user to new groups
    print(f'\tAdding user to group {new_group_externalId}')

    command = f'pipenv run invenio roles add {user_email} {new_group_externalId}'
    response = shell_interface.os.system(command)

    if response != 0:
        print(f'Warning - Creating group response: {response}')
        open(shell_interface.report_name, "a").write(f'{report} - Error: {response}\n')
        return False

    open(shell_interface.report_name, "a").write(f'{report} - Success\n')
    return True

    

def get_user_email(shell_interface, user_id):
    # Get user email
    query = f"SELECT email FROM accounts_user WHERE id = {user_id};"
    user_email = db_query(shell_interface, query)[0][0]
    print(f'\n\tUser  id: {add_spaces(user_id)}    - Email:             {user_email}')
    return user_email