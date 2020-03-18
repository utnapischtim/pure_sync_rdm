from setup                          import *
from functions.general_functions    import rdm_get_recid, rdm_get_recid_metadata, initialize_count_variables, db_connect, db_query
from functions.rdm_push_record      import rdm_push_record, create_invenio_data


#   ---         ---         ---
def rdm_person_association(shell_interface: object, persion_uuid: str):
    """ Gets from pure all the records related to a certain user,
        afterwards it modifies RDM record's owner to match the user.
        To be executed when a user access for the first time (or at every access ?). """

    person_uuid = 'cdc5cd7e-a6d4-4e2a-b258-d0cad657a1d1'        # TEMPORARY
    email       = 'tset@invenio.org'                            # TEMPORARY

    initialize_count_variables(shell_interface)
    shell_interface.count_http_responses = {}

    # Get RDM user id
    get_rdm_owner(shell_interface, email)

    # If the user was not found in RDM then there is no owner to add to the record.
    if shell_interface.rdm_record_owner == None:
        return

    # Pure user uuid  +  RDM user id  +  RDM email
    line = f'{person_uuid} {shell_interface.rdm_record_owner} {email}'
    file_name = f'{shell_interface.dirpath}/data/pure_rdm_user_id.txt'
    open(file_name, 'wb').write(line)

    # PURE REQUEST
    headers = {
        'Accept': 'application/json',
    }
    params = (
        ('apiKey', pure_api_key),
    )
    url = f'{pure_rest_api_url}persons/{person_uuid}/research-outputs'
    response = shell_interface.requests.get(url, headers=headers, params=params)

    print(f'\tPerson records - {response}\n')

    # Write data into resp_pure_changes
    file_name = f'{shell_interface.dirpath}/data/temporary_files/resp_pure_persons.json'
    open(file_name, 'wb').write(response.content)

    if response.status_code >= 300:
        print(response.content)

    # Load response json
    resp_json = shell_interface.json.loads(response.content)

    for item in resp_json['items']:
    
        uuid  = item['uuid']
        title = item['title']
        
        print(f'\n\tPerson record - {uuid} - {title}')

        # Get from RDM the recid
        recid = rdm_get_recid(shell_interface, uuid)

        # If the record is not in RDM, it is added
        if recid == False:
            shell_interface.item = item
            print('------- Create new record')
            create_invenio_data(shell_interface)

        else:
            # Checks if the owner is already in RDM record metadata
            # Get metadata from RDM
            response = rdm_get_recid_metadata(recid)

            record_json = shell_interface.json.loads(response.content)['metadata']

            print(f"\tRDM getMetad. - {response} - Current owners:     - {record_json['owners']}")

            # If the owner is not among metadata owners
            if shell_interface.rdm_record_owner not in record_json['owners']:
                print('------- Adding owner to record')

                record_json['owners'].append(shell_interface.rdm_record_owner)

                # Add owner to the record
                update_rdm_record(shell_interface, record_json, recid)
            else:
                print('------- Owner already in record ;)')


#   ---         ---         ---
def update_rdm_record(shell_interface: object, record_json: dict, recid: str):

    data = shell_interface.json.dumps(record_json)

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

    print(f'\tRecord update - {response}')

    if response.status_code >= 300:
        print(response.content)


#   ---         ---         ---
def get_rdm_owner(shell_interface: object, email: str):

    # TODO - TODO - TODO - TODO - TODO - TODO - TODO - TODO - TODO - TODO - TODO - TODO - TODO - TODO - TODO - TODO - TODO - TODO - TODO
    # IT CAN NOT BE BASED ONLY ON THE EMAIL !!!!!!!!!!!!
    # HOW TO BE SURE THAT IS THE SAME USER AS IN PURE? SEE SHIBBOLETH

    # DB query - Get user IP
    response = db_query(shell_interface, f"SELECT id FROM accounts_user WHERE email = '{email}'")
    if len(response) == 0:
        print('\naccounts_user: email not found\n')
        return False

    elif len(response) > 1:
        print('\naccounts_user: email found multiple times\n')
        return False

    shell_interface.rdm_record_owner = response[0][0]
    print(f'\tRDM record owner - {shell_interface.rdm_record_owner}')
