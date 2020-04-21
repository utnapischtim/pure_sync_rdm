from setup                              import dirpath, token_rdm, rdm_api_url_records, pure_rest_api_url, \
                                               versioning_running, pure_api_key, wait_429
from functions.general_functions        import add_to_full_report, add_spaces
import requests
from datetime                           import date
import time
import requests
import json
import os

def rdm_request_headers(parameters):
    headers = {}
    if 'content_type' in parameters:
        headers['Content-Type'] = 'application/json'
    if 'file' in parameters:
        headers['Content-Type'] = 'application/octet-stream'
    if 'accept' in parameters:
        headers['Accept'] = 'application/json'
    if 'token' in parameters:
        headers['Authorization'] = f'Bearer {token_rdm}'
    if 'api_key' in parameters:
        headers['api-key'] = pure_api_key
    return headers

def rdm_request_params():
    params = (
        ('prettyprint', '1'),
    )
    return params

def rdm_get_metadata(url: str):
    headers = rdm_request_headers(['content_type', 'token'])
    params  = rdm_request_params()
    return requests.get(url, headers=headers, params=params, verify=False)

def rdm_get_metadata_verified(url: str):
    headers = rdm_request_headers(['accept', 'api_key'])
    return requests.get(url, headers=headers)

def rdm_post_metadata(url: str, data: str):
    """ Used to create a new record """
    headers = rdm_request_headers(['content_type'])
    params  = rdm_request_params()
    data_utf8 = data.encode('utf-8')
    return requests.post(url, headers=headers, params=params, data=data_utf8, verify=False)

def rdm_put_metadata(url: str, data: str):
    """ Used to update an existing record """
    headers = rdm_request_headers(['content_type', 'token'])
    params  = rdm_request_params()
    data_utf8 = data.encode('utf-8')
    return requests.put(url, headers=headers, params=params, data=data_utf8, verify=False)

def rdm_put_file(url: str, file_path_name: str):
    headers = rdm_request_headers(['file', 'token'])
    data    = open(file_path_name, 'rb').read()
    return requests.put(url, headers=headers, data=data, verify=False)



#   ---         ---         ---
def rdm_get_recid_metadata(shell_interface: object, recid: str):

    # REVIEW - NOT ALLOWING TO IMPORT OUTSIDE THE FUNCTION - REVIEW
    # from functions.general_functions    import add_to_full_report

    if len(recid) != 11:
        report = f'\nERROR - The recid must have 11 characters. Given: {recid}\n'
        add_to_full_report(report)
        return False

    # # GET request RDM
    url = f'{rdm_api_url_records}api/records/{recid}'
    response = rdm_get_metadata(url)

    if response.status_code >= 300:
        add_to_full_report(f'\n{recid} - {response}')
        return False

    open(f'{dirpath}/data/temporary_files/rdm_get_recid_metadata.json', "wb").write(response.content)
    
    return response


#   ---         ---         ---
def rdm_get_metadata_by_query(shell_interface: object, query_value: str):

    # GET request RDM
    sort  = 'sort=mostrecent'
    size  = 'size=100'
    page  = 'page=1'
    query = f'q="{query_value}"'

    url = f'{rdm_api_url_records}api/records/?{sort}&{query}&{size}&{page}'
    response = rdm_get_metadata(url)

    if response.status_code >= 300:
        add_to_full_report(f'\n{query_value} - {response}')
        return False

    open(f'{dirpath}/data/temporary_files/rdm_get_metadata_by_query.json', "wb").write(response.content)
    
    return response
    

#   ---         ---         ---
def rdm_get_recid(shell_interface: object, uuid: str):

    # The function delete_record needs to be imported localy to avoid 'circular imports'
    from functions.delete_record            import delete_record

    """ KNOWN ISSUE: if the applied restriction in invenio_records_permissions
                     do not allow to read the record then it will not be listed """

    response = rdm_get_metadata_by_query(shell_interface, uuid)

    # If the status_code is 429 (too many requests) then it will wait for some minutes
    if not too_many_rdm_requests_check(response):
        return False

    resp_json = json.loads(response.content)

    total_recids = resp_json['hits']['total']
    if total_recids == 0:
        # If there are no records with the same uuid means it is the first one (version 1)
        return False

    # Iterate over all records with the same uuid
    # The first record is the most recent (they are sorted)
    count = 0
    for item in resp_json['hits']['hits']:
        count += 1

        recid = item['metadata']['recid']
        
        if count == 1:
            # URLs to be transmitted to Pure if the record is successfuly added in RDM      # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
            shell_interface.api_url             = f'{rdm_api_url_records}api/records/{recid}'
            shell_interface.landing_page_url    = f'{rdm_api_url_records}records/{recid}'
            newest_recid = recid

            report = f'\tRDM get recid         - {response} - Total:       {add_spaces(total_recids)}  - {shell_interface.api_url}'
            add_to_full_report(report)

        else:
            # If versioning is running then it is not necessary to delete older versions of the record
            if not versioning_running:
                # Duplicate records are deleted
                delete_record(shell_interface, recid)

    return newest_recid


#   ---         ---         ---
def get_rdm_userid_from_list_by_externalid(shell_interface: object, external_id: str, file_data: list):

    if shell_interface.rdm_record_owner:
        return shell_interface.rdm_record_owner

    for line in file_data:
        line = line.split('\n')[0]
        line = line.split(' ')

        # Checks if at least one of the ids match
        if external_id == line[2]:
            user_id         = line[0]
            user_id_spaces  = add_spaces(user_id)

            report = f'\tRDM owner list        -                  - User id:   {user_id_spaces}  - externalId: {external_id}'
            add_to_full_report(report)

            return user_id


#   ---         ---         ---
def update_rdm_record(shell_interface: object, data: str, recid: str):

    url = f'{rdm_api_url_records}api/records/{recid}'
    response = rdm_put_metadata(url, data)

    add_to_full_report(f'\tRecord update         - {response}')

    if response.status_code >= 300:
        add_to_full_report(response.content)
    return response
    

#   ---         ---         ---
def too_many_rdm_requests_check(response: int):
    """ If too many requests are submitted to RDM (more then 5000 / hour) """

    if response.status_code == 429:
        add_to_full_report(response.content)
        add_to_full_report('\nToo many RDM requests.. wait {wait_429 / 60} minutes\n')
        time.sleep(wait_429)
        return False
    return True