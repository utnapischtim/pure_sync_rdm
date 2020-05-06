import json
import requests
from datetime                       import date, datetime
from requests.auth                  import HTTPBasicAuth
from setup                          import pure_username, pure_password, temporary_files_name, \
                                           pure_rest_api_url, pure_api_key, log_files_name
from source.reports                 import Reports

reports = Reports()


def get_next_page(resp_json, page):
    
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



def get_pure_file(shell_interface, electronic_version: str):

    file_name = electronic_version['file']['fileName']
    file_url  = electronic_version['file']['fileURL']

    # Get request to Pure
    response = requests.get(file_url, auth=HTTPBasicAuth(pure_username, pure_password))

    # If the file is not in RDM
    if len(shell_interface.pure_rdm_file_match) == 0:
        match_review = 'File not in RDM    '

    # If the file in pure is different from the one in RDM
    elif shell_interface.pure_rdm_file_match[0] == False:
        match_review = 'Match: F, Review: -'

    # If the file is the same, checks if the one in RDM has been reviewed by internal stuff
    else:
        match_review = 'Match: T, Review: F'
        if shell_interface.pure_rdm_file_match[1]:
            match_review = 'Match: T, Review: T'
    
    report = f'\tPure get file         - {response} - {match_review} - {file_name[0:55]}...'
    reports.add(['console'], report)
    
    if response.status_code < 300:
        # Save file
        base_path = temporary_files_name['base_path']
        open(f'{base_path}/{file_name}', 'wb').write(response.content)

        shell_interface.record_files.append(file_name)

        # ISSUE encountered when putting txt files
        file_extension = file_name.split('.')[file_name.count('.')]
        if file_extension == 'txt':
            report = '\n\tATTENTION, the file extension is txt - \tKnown issue -> jinja2.exceptions.UndefinedError: No first item, sequence was empty.\n'
            reports.add(['console'], report)

    else:
        reports.add(['console'], f'Error downloading file from pure ({file_url})')

    return