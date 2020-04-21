from setup                              import dirpath, pure_rest_api_url
from functions.general_functions        import add_to_full_report
from functions.rdm_general_functions    import rdm_get_metadata_verified

from datetime                           import date, datetime
import json

#   ---         ---         ---
def pure_get_uuid_metadata(shell_interface: object, uuid: str):
    """ Method used to get from Pure record's metadata """

    # PURE REQUEST
    url = f'{pure_rest_api_url}research-outputs/{uuid}'
    response = rdm_get_metadata_verified(url)

    add_to_full_report(f'\n\tPure get metadata     - {response}')

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
    shell_interface.item = json.loads(response.content)
    return True