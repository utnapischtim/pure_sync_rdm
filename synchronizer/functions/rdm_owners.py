from setup                          import *
from functions.rdm_push_record      import  rdm_push_record, create_invenio_data
from functions.general_functions    import  rdm_get_recid, \
                                            rdm_get_recid_metadata, \
                                            initialize_count_variables, \
                                            db_connect, \
                                            db_query, \
                                            add_spaces, \
                                            bcolors

#   ---         ---         ---
def rdm_owners(shell_interface: object, external_id: int):
    """ Gets from pure all the records related to a certain user,
        afterwards it modifies/create RDM records accordingly. """

    initialize_count_variables(shell_interface)
    shell_interface.count_http_responses = {}

    print(f'\nExternal_id: {external_id}\n')

    # Gets the ID and IP of the logged in user
    response = rdm_get_user_id(shell_interface)

    # If the user was not found in RDM then there is no owner to add to the record.
    if not response:
        return

    user_id = response[0]
    user_ip = response[1]

    # Get from pure user_uuid
    user_uuid = pure_get_user_uuid(shell_interface, external_id)
    
    if not user_uuid:
        return False

    if len(user_uuid) != 36:
        print('\n- Warning! Incorrect user_uuid length -\n')
        return False

    # Add user to user_ids_match table
    add_user_ids_match(shell_interface, user_id, user_uuid, external_id)

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

    if total_items == 0:
        print('\nThe user has no records - End task\n')
        return True

    for item in resp_json['items']:
    
        uuid  = item['uuid']
        title = item['title']
        
        print(f'\n\tRecord uuid        - {uuid}  - {title}')

        # Get from RDM the recid
        recid = rdm_get_recid(shell_interface, uuid)

        # If the record is not in RDM, it is added
        if recid == False:
            item['owners'] = [user_id]
            shell_interface.item = item

            print('\t+ Create record    +')
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
    page_size = 25
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
        
        if total_items == 0:
            print(f'{bcolors.RED}\nUser uuid not found - Exit task\n{bcolors.END}')
            return False

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
        else:
            keep_searching = False

    return False


#   ---         ---         ---
def rdm_get_user_id(shell_interface: object):
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


#   ---         ---         ---
def get_rdm_record_owners(shell_interface: object):
            
    pag = 1
    pag_size = 25

    count = 0
    count_records_per_owner = {}
    go_on = True


    # Empty file
    file_owner = f"{shell_interface.dirpath}/data/temporary_files/rdm_records_owner.txt"
    open(file_owner, 'w').close()

    while go_on == True:

        # REQUEST to RDM
        headers = {
            'Authorization': f'Bearer {token_rdm}',
            'Content-Type': 'application/json',
        }
        params = (('prettyprint', '1'),)
        url = f'{rdm_api_url_records}api/records/?sort=mostrecent&size={pag_size}&page={pag}'

        response = shell_interface.requests.get(url, headers=headers, params=params, verify=False)
        print(f'\n{response}\n')
        
        file_name = f"{shell_interface.dirpath}/data/temporary_files/rdm_get_records.json"
        open(file_name, 'wb').write(response.content)

        if response.status_code >= 300:
            print(response.content)
            break

        resp_json = shell_interface.json.loads(response.content)
        data = ''

        for item in resp_json['hits']['hits']:
            count += 1

            uuid   = item['metadata']['uuid']
            recid  = item['metadata']['recid']
            owners = item['metadata']['owners']

            line = f'{uuid} - {recid} - {owners}'
            print(line)
            data += f'{line}\n'

            for i in owners:
                if i not in count_records_per_owner:
                    count_records_per_owner[i] = 0
                count_records_per_owner[i] += 1

        print(f'\nPag {str(pag)} - Records {count}\n')
        
        open(file_owner, 'a').write(data)

        if 'next' not in resp_json['links']:
            go_on = False
        
        pag += 1
        shell_interface.time.sleep(1)

    print('Owner  Records')
    for key in count_records_per_owner:
        records = add_spaces(count_records_per_owner[key])
        key     = add_spaces(key)
        print(f'{key}    {records}')



def add_user_ids_match(shell_interface: object, user_id: int, user_uuid: str, external_id: str):

    file_name = f"{shell_interface.dirpath}/data/user_ids_match.txt"

    needs_to_add = check_user_ids_match(shell_interface, user_id, user_uuid, external_id, file_name)

    if needs_to_add:
        open(file_name, 'a').write(f'{user_id} {user_uuid} {external_id}\n')
        print(f'user_ids_match     - Adding: {user_id}, {user_uuid}, {external_id}')


def check_user_ids_match(shell_interface: object, user_id: int, user_uuid: str, external_id: str, file_name: str):

    file_data = open(file_name).readlines()
    for line in file_data:
        line = line.split('\n')[0]
        line = line.split(' ')

        # Checks if at least one of the ids match
        if str(user_id) == line[0] or user_uuid == line[1] or external_id == line[2]:
            
            if line == [str(user_id), user_uuid, external_id]:
                print('user_ids_match     - full match')
                return False

            # print('user_ids_match     - partial match -----------------------------------')
            # print(f'{user_id} == {line[0]} and {user_uuid} == {line[1]} and {external_id} == {line[2]}')
            # return False
    
    print('user_ids_match     - No match')
    return True

def get_rdm_userid_from_list_by_externalid(shell_interface: object, external_id: str):
    file_name = f"{shell_interface.dirpath}/data/user_ids_match.txt"
    file_data = open(file_name).readlines()
    for line in file_data:
        line = line.split('\n')[0]
        line = line.split(' ')

        # Checks if at least one of the ids match
        if external_id == line[2]:
            print(f'RDM useridFromList - externalId: {external_id} -> user id: {line[0]}')
            return line[0]