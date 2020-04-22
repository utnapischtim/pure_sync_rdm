from setup                              import dirpath, token_rdm, rdm_api_url_records, pure_rest_api_url, versioning_running, pure_api_key, wait_429
from functions.general_functions        import add_to_full_report, add_spaces
import requests
from datetime                           import date
import time
import requests
import json
import os


def rdm_get_recid_metadata(recid: str):
    """ Having the record recid gets from RDM its metadata """
    if len(recid) != 11:
        report = f'\nERROR - The recid must have 11 characters. Given: {recid}\n'
        add_to_full_report(report)
        return False

    # RDM request
    url = f'{rdm_api_url_records}api/records/{recid}'
    response = rdm_get_metadata(url)

    if response.status_code >= 300:
        add_to_full_report(f'\n{recid} - {response}')
        return False
    
    return response


#   ---         ---         ---
def rdm_get_metadata_by_query(query_value: str):
    """ Applying a query get RDM record metadata """

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
    
    return response
    

#   ---         ---         ---
def rdm_get_recid(uuid: str):
    """
    1 - to check if there are duplicates
    2 - to delete duplicates
    3 - to add the record uuid and recid to all_rdm_records.txt
    4 - gets the last metadata_version
    """

    # The following function needs to be imported localy to avoid 'circular imports'
    from functions.delete_record            import delete_record

    """ KNOWN ISSUE: if the applied restriction in invenio_records_permissions (for admin users)
                     do not allow to read the record then it will not be listed """

    response = rdm_get_metadata_by_query(uuid)

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
            api_url             = f'{rdm_api_url_records}api/records/{recid}'
            landing_page_url    = f'{rdm_api_url_records}records/{recid}'
            newest_recid = recid

            report = f'\tRDM get recid         - {response} - Total:       {add_spaces(total_recids)}  - {api_url}'
            add_to_full_report(report)

        else:
            # If versioning is running then it is not necessary to delete older versions of the record
            if not versioning_running:
                # Duplicate records are deleted
                delete_record(recid)

    return newest_recid


#   ---         ---         ---
def get_rdm_userid_from_list_by_externalid(external_id: str, file_data: list):

    for line in file_data:
        line = line.split('\n')[0]
        line = line.split(' ')

        # Checks if at least one of the ids match
        if external_id == line[2]:
            user_id         = line[0]
            user_id_spaces  = add_spaces(user_id)

            report = f'\tRDM owner list        -                  - User id:     {user_id_spaces}  - externalId: {external_id}'
            add_to_full_report(report)

            return user_id


#   ---         ---         ---
def update_rdm_record(data: str, recid: str):

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


#   ---         ---         ---
def rdm_request_headers(parameters):
    headers = {}
    if 'content_type' in parameters:
        headers['Content-Type'] = 'application/json'
    if 'file' in parameters:
        headers['Content-Type'] = 'application/octet-stream'
    if 'token' in parameters:
        headers['Authorization'] = f'Bearer {token_rdm}'
    return headers

def rdm_request_params():
    return (('prettyprint', '1'),)

def rdm_get_metadata(url: str):
    headers = rdm_request_headers(['content_type', 'token'])
    params  = rdm_request_params()
    return requests.get(url, headers=headers, params=params, verify=False)

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

def rdm_delete_metadata(url: str, recid: str):
    headers = rdm_request_headers(['content_type', 'token'])
    return requests.delete(url, headers=headers, verify=False)