from setup                          import *
from functions.general_functions    import rdm_get_recid, rdm_get_recid_metadata, initialize_count_variables, db_connect, db_query
from functions.rdm_push_record      import rdm_push_record, create_invenio_data


#   ---         ---         ---
def rdm_person_association(shell_interface: object, external_id: int):
    """ Gets from pure all the records related to a certain user,
        afterwards it modifies RDM record's owner to match the user.
        To be executed when a user access for the first time (or at every access ?). """

    initialize_count_variables(shell_interface)
    shell_interface.count_http_responses = {}

    print(f'\nExternal_id: {external_id}\n')

    # Gets the ID and IP of the logged in user
    response = get_rdm_user_id(shell_interface)

    # If the user was not found in RDM then there is no owner to add to the record.
    if not response:
        return

    user_id = response[0]
    user_ip = response[1]

    # Get from RDM user_uuid
    user_uuid = pure_get_user_uuid(shell_interface, external_id)
    
    if len(user_uuid) != 36:
        print('\n- Warning! Incorrect user_uuid length -\n')
        return False

    # PURE get person records
    headers = {
        'Accept': 'application/json',
    }
    params = (
        ('apiKey', pure_api_key),
        ('pageSize', 200),
    )
    url = f'{pure_rest_api_url}persons/{user_uuid}/research-outputs'
    response = shell_interface.requests.get(url, headers=headers, params=params)

    # Write data into pure_get_person_records
    file_name = f'{shell_interface.dirpath}/data/temporary_files/pure_get_person_records.json'
    open(file_name, 'wb').write(response.content)

    if response.status_code >= 300:
        print(response.content)
        return False

    # Load response json
    resp_json = shell_interface.json.loads(response.content)

    total_items = resp_json['count']
    print(f'Get person records - {response} - total_items: {total_items}')

    for item in resp_json['items']:
    
        uuid  = item['uuid']
        
        print(f'\n\tRecord uuid        - {uuid}')

        # Get from RDM the recid
        recid = rdm_get_recid(shell_interface, uuid)

        # If the record is not in RDM, it is added
        if recid == False:
            item['owners'] = [user_id]
            shell_interface.item = item

            print('\t+ Create new record +')
            create_invenio_data(shell_interface)

        else:
            # Checks if the owner is already in RDM record metadata
            
            # Get metadata from RDM
            response = rdm_get_recid_metadata(shell_interface, recid)
            record_json = shell_interface.json.loads(response.content)['metadata']

            print(f"\tRDM get metadata   - {response} - Current owners:     - {record_json['owners']}")

            # If the owner is not among metadata owners
            if user_id and user_id not in record_json['owners']:

                record_json['owners'].append(user_id)
                print(f"\t+   Adding owner   -                  - New owners:         - {record_json['owners']}")

                record_json = shell_interface.json.dumps(record_json)

                file_name = f'{shell_interface.dirpath}/data/temporary_files/rdm_record_update.json'
                open(file_name, 'a').write(record_json)

                # Add owner to the record
                update_rdm_record(shell_interface, record_json, recid)
            else:
                print('\t+ Owner in record  +')


#   ---         ---         ---
def update_rdm_record(shell_interface: object, data: str, recid: str):

    data_utf8 = data.encode('utf-8')

    headers = {
        'Authorization': f'Bearer {token_rdm}',
        'Content-Type': 'application/json',
    }
    params = (
        ('prettyprint', '1'),
    )

    url = f'{rdm_api_url_records}api/records/{recid}'

    response = shell_interface.requests.put(url, headers=headers, params=params, data=data_utf8, verify=False)
    print(f'\tRecord update      - {response}')

    if response.status_code >= 300:
        print(response.content)


#   ---         ---         ---
def pure_get_user_uuid(shell_interface: object, external_id: str):
    """ PURE get person records """

    keep_searching = True
    page_size = 50
    page = 1

    while keep_searching:

        headers = {
            'Accept': 'application/json',
        }
        params = (
            ('q', f'"{external_id}"'),
            ('apiKey', pure_api_key),
            ('pageSize', page_size),
            ('page', page),
        )
        url = f'{pure_rest_api_url}persons'

        response = shell_interface.requests.get(url, headers=headers, params=params)

        if response.status_code >= 300:
            print(response.content)
            return False

        open(f'{shell_interface.dirpath}/data/temporary_files/pure_get_user_uuid.json', "wb").write(response.content)
        record_json = shell_interface.json.loads(response.content)

        total_items = record_json['count']
        print(f'Pure get user uuid - {response} - Total items: {total_items}')

        for item in record_json['items']:
            if item['externalId'] == external_id:

                first_name  = item['name']['firstName']
                lastName    = item['name']['lastName']
                uuid        = item['uuid']

                print(f'User uuid          - {uuid}  - {first_name} {lastName}')
                return uuid

        if 'navigationLinks' in record_json:
            page += 1

    return False


#   ---         ---         ---
def get_rdm_user_id(shell_interface: object):
    """ Gets the ID and IP of the logged in user """

    # Table -> accounts_user_session_activity:
    # created
    # updated
    # sid_s
    # user_id
    # ip
    # country
    # browser
    # browser_version
    # os
    # device

    response = db_query(shell_interface, f"SELECT user_id, ip FROM accounts_user_session_activity")

    if len(response) == 0:
        print('\n- accounts_user_session_activity: No user is logged in -\n')
        return False

    elif len(response) > 1:
        print('\n- accounts_user_session_activity: Multiple users in \n')
        return False

    print(f'user IP: {response[0][1]} - user_id: {response[0][0]}')

    return response[0]
