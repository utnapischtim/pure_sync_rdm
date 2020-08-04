import json
import requests
from datetime                       import date, datetime
from requests.auth                  import HTTPBasicAuth
from setup                          import pure_username, pure_password, temporary_files_name, \
                                           pure_rest_api_url, pure_api_key, log_files_name
from source.reports                 import Reports
from source.pure.requests           import get_pure_metadata

reports = Reports()

def get_next_page(resp_json):
    
    if 'navigationLinks' in resp_json:
        if 'next' in resp_json['navigationLinks'][0]['ref']:
            return resp_json['navigationLinks'][0]['href']
        else:
            if len(resp_json['navigationLinks']) == 2:
                if 'next' in resp_json['navigationLinks'][1]['ref']:
                    return resp_json['navigationLinks'][1]['href']
    return False


def get_pure_record_metadata_by_uuid(uuid: str):
    """ Method used to get from Pure record's metadata """

    # PURE REQUEST
    response = get_pure_metadata('research-outputs', uuid)

    report = f'\tPure get metadata     - {response}'
    if response.status_code == 404:
        report += f' - Metadata not found in Pure for record {uuid}'
    elif response.status_code >= 300:
        report += f' - Error: {response.content}'
    else:
        report += f'                       - {uuid}'
    reports.add(report)

    # Check response
    if response.status_code >= 300:
        report = f'Get Pure metadata      - {response.content}\n'
        reports.add(report['console', 'records'])
        return False

    return json.loads(response.content)



def get_pure_file(shell_interface, file_url: str, file_name: str):

    # Get request to Pure
    response = requests.get(file_url, auth=HTTPBasicAuth(pure_username, pure_password))

    if response.status_code >= 300:
        reports.add(f'Error getting the file {file_url} from Pure')
        return False

    # Save file
    base_path = temporary_files_name['base_path']
    open(f'{base_path}/{file_name}', 'wb').write(response.content)

    return response