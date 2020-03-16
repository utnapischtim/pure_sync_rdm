from setup import *
import os

def rdm_person_association(shell_interface: object, persion_uuid: str):
    """ Gets from pure all the records related to a certain user,
        afterwards it modifies RDM record's owner to match the user. """

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

    print(response)

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

        # Get recid

        # Add owner to the record

