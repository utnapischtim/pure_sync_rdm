import json
import requests
from datetime                       import date, datetime
from setup                          import pure_rest_api_url, pure_api_key, log_files_name, temporary_files_name
from source.general_functions       import dirpath
from source.reports                 import Reports

reports = Reports()

def get_pure_record_metadata_by_uuid(uuid: str):
    """ Method used to get from Pure record's metadata """

    # PURE REQUEST
    # url = f'{pure_rest_api_url}research-outputs/{uuid}'
    response = pure_get_metadata('research-outputs', uuid)

    report = f'\tPure get metadata     - {response}'
    if response.status_code == 404:
        report += f' - Metadata not found in Pure for record {uuid}'
    elif response.status_code >= 300:
        report += f' - Error: {response.content}'
    else:
        report += f'                       - {uuid}'
    reports.add(['console'], report)

    # Check response
    if response.status_code >= 300:
        report = f'Get Pure metadata      - {response.content}\n'
        reports.add(['console', 'records'], report)
        return False

    return json.loads(response.content)



def get_pure_metadata(endpoint, identifier = '', parameters = {}):
    headers = {
        'api-key': pure_api_key,
        'Accept': 'application/json',
    }
    url = f'{pure_rest_api_url}{endpoint}/'

    # Identifies a person, research_output or date
    if len(identifier) > 0:
        url += f'{identifier}/'

    # Add parameters to url
    if len(parameters) > 0:
        url = url[:-1]                  # Remove last character
        url += '?'
        for key in parameters:
            url += f'{key}={parameters[key]}&'

    url = url[:-1]

    # Sending request
    response = requests.get(url, headers=headers)

    # Add response content to pure_get_uuid_metadata.json
    open(temporary_files_name['get_pure_metadata'], 'wb').write(response.content)

    return response