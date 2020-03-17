from setup                          import *
from functions.general_functions    import rdm_get_recid, rdm_get_recid_metadata
from functions.rdm_push_record      import rdm_push_record


#   ---         ---         ---
def rdm_person_association(shell_interface: object, persion_uuid: str):
    """ Gets from pure all the records related to a certain user,
        afterwards it modifies RDM record's owner to match the user.
        To be executed when a user access for the first time (or at every access ?). """

    person_uuid = 'cdc5cd7e-a6d4-4e2a-b258-d0cad657a1d1' # TEMPORARY

    # PURE REQUEST
    headers = {
        'Accept': 'application/json',
    }
    params = (
        ('apiKey', 'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
    )
    url = f'{pure_rest_api_url}persons/{person_uuid}/research-outputs'
    response = shell_interface.requests.get(url, headers=headers, params=params)

    print(f'Person records - {response}')

    # Write data into resp_pure_changes
    file_name = f'{shell_interface.dirpath}/data/temporary_files/resp_pure_persons.json'
    open(file_name, 'wb').write(response.content)

    if response.status_code >= 300:
        print(response.content)

    # Load response json
    resp_json = shell_interface.json.loads(response.content)

    for person in resp_json['items']:
        
        uuid  = person['uuid']
        title = person['title']
        print(f'{uuid} - {title}')

        # Get from RDM the recid
        recid = rdm_get_recid(shell_interface, uuid)
        if recid == False:
            print(f'{uuid} - uuid not found in RDM')
            
            # Adds record to RDM
            rdm_push_record(shell_interface, uuid)

        # Add owner to the record
        add_owner_to_record(shell_interface, recid)


#   ---         ---         ---
def add_owner_to_record(shell_interface: object, recid: str):

    # recid = 'hya32-x9874'

    response = rdm_get_recid_metadata(recid)
    print(response)

    record_json = shell_interface.json.loads(response.content)['metadata']

    record_json['owners'].append(88)

    print(record_json)


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

    print(response)

    if response.status_code >= 300:
        print(response.content)

