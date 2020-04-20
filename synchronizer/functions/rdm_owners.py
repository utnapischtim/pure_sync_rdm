from setup                          import pure_rest_api_url, dirpath, rdm_api_url_records, token_rdm
from functions.general_functions    import rdm_get_metadata_verified, rdm_get_metadata, add_to_full_report, initialize_count_variables, rdm_get_recid, rdm_get_recid_metadata, update_rdm_record, add_spaces
from functions.rdm_push_record      import create_invenio_data
from functions.rdm_push_record      import rdm_push_record
from functions.rdm_database         import RdmDatabase


#   ---         ---         ---
def rdm_owners(shell_interface: object):
    """ Gets from pure all the records related to a certain user,
        afterwards it modifies/create RDM records accordingly. """

    external_id = '56038' # TEMP

    add_to_full_report(f'\nUser external_id: {external_id}\n')

    # Gets the ID of the logged in user
    user_id = rdm_get_user_id(shell_interface)

    # If the user was not found in RDM then there is no owner to add to the record.
    if not user_id:
        return

    # Get from pure user_uuid
    user_uuid = pure_get_user_uuid(shell_interface, 'externalId', external_id)
    
    if not user_uuid:
        return False

    # Add user to user_ids_match table
    add_user_ids_match(shell_interface, user_id, user_uuid, external_id)

    get_owner_records(shell_interface, user_id, user_uuid)


#   ---         ---         ---
def rdm_owners_by_orcid(shell_interface: object):

    orcid = '0000-0002-4154-6945'  # TEMP

    add_to_full_report(f'\norcid: {orcid}\n')

    if len(orcid) != 19:
        add_to_full_report('Warning - Orcid length it is not 19\n')

    # Gets the ID and IP of the logged in user
    user_id = rdm_get_user_id(shell_interface)

    # If the user was not found in RDM then there is no owner to add to the record.
    if not user_id:
        return

    # Get from pure user_uuid
    user_uuid = pure_get_user_uuid(shell_interface, 'orcid', orcid)
    
    if not user_uuid:
        return False

    get_owner_records(shell_interface, user_id, user_uuid)
    

#   ---         ---         ---
def get_owner_records(shell_interface, user_id, user_uuid):
    
    initialize_count_variables(shell_interface)
    shell_interface.count_http_responses = {}

    page      = 1
    page_size = 25
    go_on     = True
    count     = 0

    while go_on:

        url = f'{pure_rest_api_url}persons/{user_uuid}/research-outputs?page={page}&pageSize={page_size}'
        response = rdm_get_metadata_verified(url)

        # Write data into pure_get_person_records
        file_name = f'{dirpath}/data/temporary_files/pure_get_person_records.json'
        open(file_name, 'wb').write(response.content)

        if response.status_code >= 300:
            add_to_full_report(response.content)
            return False

        # Load response json
        resp_json = shell_interface.json.loads(response.content)

        total_items = resp_json['count']
        add_to_full_report(f'\nGet person records - {response} - Page {page} (size {page_size})    - Total records: {total_items}')

        if total_items == 0:
            if page == 1:
                add_to_full_report('\nThe user has no records - End task\n')
            return True

        for item in resp_json['items']:
        
            uuid  = item['uuid']
            title = item['title']
            count += 1
            
            add_to_full_report(f'\n\tRecord uuid           - {uuid}   - {title[0:55]}...')

            # Get from RDM the recid
            recid = rdm_get_recid(shell_interface, uuid)

            # If the record is not in RDM, it is added
            if recid == False:
                item['owners'] = [user_id]
                shell_interface.item = item

                add_to_full_report('\t+ Create record    +')
                create_invenio_data(shell_interface)

            else:
                # Checks if the owner is already in RDM record metadata

                shell_interface.time.sleep(0.5)
                
                # Get metadata from RDM
                response = rdm_get_recid_metadata(shell_interface, recid)
                record_json = shell_interface.json.loads(response.content)['metadata']

                add_to_full_report(f"\tRDM get metadata      - {response} - Current owners:     - {record_json['owners']}")

                # If the owner is not among metadata owners
                if user_id and user_id not in record_json['owners']:

                    record_json['owners'].append(user_id)
                    add_to_full_report(f"\t+   Adding owner      -               - New owners:         - {record_json['owners']}")

                    record_json = shell_interface.json.dumps(record_json)

                    file_name = f'{dirpath}/data/temporary_files/rdm_record_update.json'
                    open(file_name, 'a').write(record_json)

                    # Add owner to the record
                    update_rdm_record(shell_interface, record_json, recid)
                else:
                    add_to_full_report('\t+ Owner in record  +')

                # exit()

        page += 1


#   ---         ---         ---
def pure_get_user_uuid(shell_interface: object, key_name: str, key_value: str):
    """ PURE get person records """

    keep_searching = True
    page_size = 250
    page = 1

    while keep_searching:

        url = f'{pure_rest_api_url}persons?page={page}&pageSize={page_size}&q=' + f'"{key_value}"'
        response = rdm_get_metadata_verified(url)

        if response.status_code >= 300:
            add_to_full_report(response.content)
            return False

        open(f'{dirpath}/data/temporary_files/pure_get_user_uuid.json', "wb").write(response.content)
        record_json = shell_interface.json.loads(response.content)

        total_items = record_json['count']

        add_to_full_report(f'Pure get user uuid - {response} - Total items: {total_items}')

        for item in record_json['items']:

            if item[key_name] == key_value:

                first_name  = item['name']['firstName']
                lastName    = item['name']['lastName']
                uuid        = item['uuid']

                add_to_full_report(f'User uuid          - {first_name} {lastName}  -  {uuid}')

                if len(uuid) != 36:
                    add_to_full_report('\n- Warning! Incorrect user_uuid length -\n')
                    return False

                return uuid

        if 'navigationLinks' in record_json:
            page += 1
        else:
            keep_searching = False

    add_to_full_report(f'\nUser uuid not found - Exit task\n')
    return False


#   ---         ---         ---
def rdm_get_user_id(shell_interface: object):
    """ Gets the ID and IP of the logged in user """

    # Creates an instane of rdm database
    rdm_db = RdmDatabase()

    response = rdm_db.db_query(f"SELECT user_id, ip FROM accounts_user_session_activity")

    if not response:
        add_to_full_report('\n- accounts_user_session_activity: No user is logged in -\n')
        return False

    elif len(response) > 1:
        add_to_full_report('\n- accounts_user_session_activity: Multiple users in \n')
        return False

    add_to_full_report(f'user IP: {response[0][1]} - user_id: {response[0][0]}')

    shell_interface.rdm_record_owner = response[0][0]

    return shell_interface.rdm_record_owner


#   ---         ---         ---
def get_rdm_record_owners(shell_interface: object):
            
    pag = 1
    pag_size = 250

    count = 0
    count_records_per_owner = {}
    all_records_list = ''
    go_on = True


    # Empty file
    file_owner = f"{dirpath}/data/temporary_files/rdm_records_owner.txt"
    open(file_owner, 'w').close()

    while go_on == True:

        # REQUEST to RDM
        url = f'{rdm_api_url_records}api/records/?sort=mostrecent&size={pag_size}&page={pag}'
        response = rdm_get_metadata(url)

        add_to_full_report(f'\n{response}\n')
        
        file_name = f"{dirpath}/data/temporary_files/rdm_get_records.json"
        open(file_name, 'wb').write(response.content)

        if response.status_code >= 300:
            add_to_full_report(response.content)
            break

        resp_json = shell_interface.json.loads(response.content)
        data = ''

        for item in resp_json['hits']['hits']:
            count += 1

            uuid   = item['metadata']['uuid']
            recid  = item['metadata']['recid']
            owners = item['metadata']['owners']

            line = f'{uuid} - {recid} - {owners}'
            add_to_full_report(line)
            data += f'{line}\n'
            
            all_records_list += f'{uuid} {recid}\n'

            for i in owners:
                if i not in count_records_per_owner:
                    count_records_per_owner[i] = 0
                count_records_per_owner[i] += 1

        add_to_full_report(f'\nPag {str(pag)} - Records {count}\n')
        
        open(file_owner, 'a').write(data)

        if 'next' not in resp_json['links']:
            go_on = False
        
        pag += 1
        shell_interface.time.sleep(0.5)

    add_to_full_report('Owner  Records')

    for key in count_records_per_owner:
        records = add_spaces(count_records_per_owner[key])
        key     = add_spaces(key)
        add_to_full_report(f'{key}    {records}')
    
    # Updates content of all_rdm_records.txt file
    file_all_records_list = f"{dirpath}/data/all_rdm_records.txt"
    # Empty file
    open(file_all_records_list, 'w').close()
    # Add all records to file
    open(file_all_records_list, 'a').write(all_records_list)



def add_user_ids_match(shell_interface: object, user_id: int, user_uuid: str, external_id: str):

    file_name = f"{dirpath}/data/user_ids_match.txt"

    needs_to_add = check_user_ids_match(shell_interface, user_id, user_uuid, external_id, file_name)

    if needs_to_add:
        open(file_name, 'a').write(f'{user_id} {user_uuid} {external_id}\n')
        add_to_full_report(f'user_ids_match     - Adding id toList - {user_id}, {user_uuid}, {external_id}')


def check_user_ids_match(shell_interface: object, user_id: int, user_uuid: str, external_id: str, file_name: str):

    file_data = open(file_name).readlines()
    for line in file_data:
        line = line.split('\n')[0]
        line = line.split(' ')

        # Checks if at least one of the ids match
        if str(user_id) == line[0] or user_uuid == line[1] or external_id == line[2]:
            
            if line == [str(user_id), user_uuid, external_id]:
                add_to_full_report('user_ids_match     - full match')
                return False
    
    return True