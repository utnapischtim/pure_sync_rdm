from setup import *
from functions.delete_record import delete_from_list, delete_record
import psycopg2



#   ---         ---         ---
def pure_get_metadata(shell_interface: object, uuid: str):
    """ Method used to get from Pure record's metadata """

    # PURE REQUEST
    headers = {
        'Accept': 'application/json',
        'api-key': pure_api_key,
    }
    params = (
        ('apiKey', pure_api_key),
    )
    url = f'{pure_rest_api_url}research-outputs/{uuid}'
    response = shell_interface.requests.get(url, headers=headers, params=params)

    print(f'\n\tGet  metadata - {response}')

    # Add response content to pure_get_metadata.json
    file_response = f'{shell_interface.dirpath}/data/temporary_files/pure_get_metadata.json'
    open(file_response, 'wb').write(response.content)

    # Check response
    if response.status_code >= 300:
        print(response.content)

        file_records = f'{shell_interface.dirpath}/reports/{shell_interface.date.today()}_records.log'
        report = f'Get metadata from Pure - {response.content}\n'
        open(file_records, "a").write(report)

        shell_interface.time.sleep(1)
        return False

    # Load json
    shell_interface.item = shell_interface.json.loads(response.content)



#   ---         ---         ---
# def rdm_get_recid_metadata(shell_interface: object, recid: str):
def rdm_get_recid_metadata(shell_interface: object, recid: str):
    
    if len(recid) != 11:
        print(f'\nERROR - The recid must have 11 characters. Given: {recid}\n')
        return False

    # GET request RDM
    headers = {
        'Authorization': f'Bearer {token_rdm}',
        'Content-Type': 'application/json',
    }
    params = (('prettyprint', '1'),)
    url = f'{rdm_api_url_records}api/records/{recid}'
    response = shell_interface.requests.get(url, headers=headers, params=params, verify=False)

    if response.status_code >= 300:
        print(f'\n{recid} - {response}')
        print(response.content)
        return False

    open(f'{shell_interface.dirpath}/data/temporary_files/rdm_get_recid_metadata.json', "wb").write(response.content)
    
    return response


#   ---         ---         ---
def rdm_get_uuid_metadata(shell_interface: object, uuid: str):
    
    if len(uuid) != 36:
        print(f'\nERROR - The uuid must have 36 characters. Given: {uuid}\n')
        return False

    # GET request RDM
    sort  = 'sort=mostrecent'
    size  = 'size=100'
    page  = 'page=1'
    query = f'q="{uuid}"'

    headers = {
        'Authorization': f'Bearer {token_rdm}',
        'Content-Type': 'application/json',
    }
    params = (('prettyprint', '1'),)
    url = f'{rdm_api_url_records}api/records/?{sort}&{query}&{size}&{page}'
    response = shell_interface.requests.get(url, headers=headers, params=params, verify=False)

    if response.status_code >= 300:
        print(f'\n{uuid} - {response}')
        print(response.content)
        return False

    open(f'{shell_interface.dirpath}/data/temporary_files/rdm_get_uuid_metadata.json', "wb").write(response.content)
    
    return response
    


#   ---         ---         ---
def rdm_get_recid(shell_interface: object, uuid: str):

    response = rdm_get_uuid_metadata(shell_interface, uuid)

    resp_json = shell_interface.json.loads(response.content)

    total_recids = resp_json['hits']['total']
    if total_recids == 0:
        return False

    log_message = f'\tRDM get recid      - {response} - Total: {total_recids}'

    # Iterate over all records with the same uuid
    # The first record is the most recent (they are sorted)
    count = 0
    for i in resp_json['hits']['hits']:
        count += 1
        recid = i['metadata']['recid']
        
        if count == 1:
            # URLs to be transmitted to Pure if the record is successfuly added in RDM
            # shell_interface.api_url             = f'https://127.0.0.1:5000/api/records/{recid}'
            # shell_interface.landing_page_url    = f'https://127.0.0.1:5000/records/{recid}'
            shell_interface.api_url             = f'{rdm_api_url_records}api/records/{recid}'
            shell_interface.landing_page_url    = f'{rdm_api_url_records}records/{recid}'

            print(f'{log_message}            - Newest: {shell_interface.api_url}')
            newest_recid = recid

        else:
            # Duplicate records are deleted
            delete_record(shell_interface, recid)

    shell_interface.recid = newest_recid
    return newest_recid



#   ---         ---         ---
def add_spaces(value: int):
    max_length = 5                              # 5 is the maximum length of the given value
    spaces = max_length - len(str(value))
    return ''.ljust(spaces) + str(value)        # ljust -> adds spaces after a string


#   ---         ---         ---
def initialize_count_variables(shell_interface):
    """ Initialize variables that will be used in report_records_summary method """

    shell_interface.count_total                       = 0
    shell_interface.count_errors_push_metadata        = 0
    shell_interface.count_errors_put_file             = 0
    shell_interface.count_errors_record_delete        = 0
    shell_interface.count_successful_push_metadata    = 0
    shell_interface.count_successful_push_file        = 0
    shell_interface.count_successful_record_delete    = 0
    shell_interface.count_abstracts                   = 0
    shell_interface.count_orcids                      = 0


#   ---         ---         ---
def db_connect(shell_interface):
    connection = psycopg2.connect(f"""\
        host={db_host} \
        dbname={db_name} \
        user={db_user} \
        password={db_password} \
        """)
    shell_interface.cursor = connection.cursor()


#   ---         ---         ---
def db_query(shell_interface, query):
    shell_interface.cursor.execute(query)
    if shell_interface.cursor.rowcount > 0:
        return shell_interface.cursor.fetchall()
    return False


#   ---         ---         ---
# Allows coloring console text
class bcolors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


#   ---         ---         ---
def get_rdm_userid_from_list_by_externalid(shell_interface: object, external_id: str):

    if shell_interface.rdm_record_owner:
        return shell_interface.owner

    file_data = open(f"{shell_interface.dirpath}/data/user_ids_match.txt").readlines()

    for line in file_data:
        line = line.split('\n')[0]
        line = line.split(' ')

        # Checks if at least one of the ids match
        if external_id == line[2]:
            user_id         = line[0]
            user_id_spaces  = add_spaces(user_id)
            print(f'\tRDM useridFromList - user id: {user_id_spaces}   - externalId: {external_id}')
            return user_id



