import json
import requests
from datetime                   import date, datetime
from setup                      import dirpath, pure_rest_api_url, pure_api_key
from source.general_functions   import add_to_full_report

#   ---         ---         ---
def pure_get_uuid_metadata(uuid: str):
    """ Method used to get from Pure record's metadata """

    # PURE REQUEST
    url = f'{pure_rest_api_url}research-outputs/{uuid}'
    response = pure_get_metadata(url)

    report = f'\tPure get metadata     - {response}'
    if response.status_code == 404:
        report += f' - Metadata not found in Pure for record {uuid}'
    elif response.status_code >= 300:
        report += f' - Error: {response.content}'
    else:
        report += f' - {uuid}'
    add_to_full_report(report)

    # Add response content to pure_get_uuid_metadata.json
    file_response = f'{dirpath}/data/temporary_files/pure_get_uuid_metadata.json'
    open(file_response, 'wb').write(response.content)

    # Check response
    if response.status_code >= 300:
        add_to_full_report(f'\n{response.content}\n')

        file_records = f'{dirpath}/reports/{date.today()}_records.log'
        report = f'Get Pure metadata      - {response.content}\n'
        open(file_records, "a").write(report)

        return False

    # Load json
    return json.loads(response.content)



def pure_get_metadata(url: str):
    headers = {
        'api-key': pure_api_key,
        'Accept': 'application/json',
    }
    return requests.get(url, headers=headers)
