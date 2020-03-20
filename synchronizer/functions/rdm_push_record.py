from setup                          import *
from functions.get_put_file         import rdm_put_file, get_file_from_pure
from functions.general_functions    import rdm_get_recid, pure_get_metadata

#   ---         ---         ---
def rdm_push_record(shell_interface: object, uuid: str):
    
    # Gets from Pure the metadata of the given uuid
    pure_get_metadata(shell_interface, uuid)

    return create_invenio_data(shell_interface)


#   ---         ---         ---
def create_invenio_data(shell_interface: object):
    """ Reads pure metadata and creates the json that will be pushed to RDM """

    # counts all records
    shell_interface.count_total += 1      

    shell_interface.record_files = []
    shell_interface.rdm_file_review = []
    item = shell_interface.item
    shell_interface.uuid = item['uuid']

    shell_interface.data = {}
    # Id 1 (master@tugraz.at) -> owner of all records
    # Other ids specific for actual users
    # GET FROM DB id of certain user (by email) - select id from accounts_user where email = 'admin@invenio.org';

    # RDM user id of the record owner
    shell_interface.data['owners'] = [1]                                                    # Master user id = 1 (?????????????)

    # If some RDM owner is specified then it will be added to owners(see rdm_person_association.py)
    if shell_interface.rdm_record_owner:
        shell_interface.data['owners'].append(shell_interface.rdm_record_owner)

    # shell_interface.data['_access'] = {'metadata_restricted': True, 'files_restricted': True}        # Default value for _access field
    shell_interface.data['_access'] = {'metadata_restricted': False, 'files_restricted': False}        # Default value for _access field

                                    # RDM field name                # PURE json path
    add_field(shell_interface, item, 'title',                       ['title'])
    add_field(shell_interface, item, 'access_right',                ['openAccessPermissions', 0, 'value'])
    
    shell_interface.data['title']           = 'ccc'                                                      # TEST TEST
    shell_interface.data['groupRestrictions']  = ['CC']                                             # TEST TEST
    shell_interface.data['ipRestrictions']     = ['127.0.0.9']                                                 # TEST TEST

    add_field(shell_interface, item, 'uuid',                        ['uuid'])
    add_field(shell_interface, item, 'pureId',                      ['pureId'])
    add_field(shell_interface, item, 'publicationDatePure',         ['publicationStatuses', 0, 'publicationDate', 'year'])
    add_field(shell_interface, item, 'createdDatePure',             ['info', 'createdDate'])
    add_field(shell_interface, item, 'modifiedDatePure',            ['info', 'modifiedDate'])
    add_field(shell_interface, item, 'pages',                       ['info','pages'])   
    add_field(shell_interface, item, 'volume',                      ['info','volume'])
    add_field(shell_interface, item, 'journalTitle',                ['info', 'journalAssociation', 'title', 'value'])
    add_field(shell_interface, item, 'journalNumber',               ['info', 'journalNumber'])
    add_field(shell_interface, item, 'pureId',                      ['pureId'])
    add_field(shell_interface, item, 'type_p',                      ['types', 0, 'value'])    
    add_field(shell_interface, item, 'category',                    ['categories', 0, 'value'])  
    add_field(shell_interface, item, 'peerReview',                  ['peerReview'])    
    add_field(shell_interface, item, 'publicationStatus',           ['publicationStatuses', 0, 'publicationStatuses', 0, 'value'])
    add_field(shell_interface, item, 'language',                    ['languages', 0, 'value'])
    add_field(shell_interface, item, 'totalNumberOfAuthors',        ['totalNumberOfAuthors'])
    add_field(shell_interface, item, 'managingOrganisationalUnit',  ['managingOrganisationalUnit', 'names', 0, 'value'])
    add_field(shell_interface, item, 'workflow',                    ['workflows', 0, 'value'])
    add_field(shell_interface, item, 'confidential',                ['confidential'])
    add_field(shell_interface, item, 'publisherName',               ['publisher', 'names', 0, 'value'])
    add_field(shell_interface, item, 'abstract',                    ['abstracts', 0, 'value'])

    # --- Electronic Versions ---
    shell_interface.data['versionFiles'] = []

    if 'electronicVersions' in item or 'additionalFiles' in item:
        # Checks if the file has been already uploaded to RDM and if it has been internally reviewed
        get_rdm_file_review(shell_interface)

    if 'electronicVersions' in item:
        for i in item['electronicVersions']:
            get_files_data(shell_interface, i)

    # --- Additional Files ---
    if 'additionalFiles' in item:
        for i in item['additionalFiles']:
            get_files_data(shell_interface, i)

    # --- personAssociations ---
    if 'personAssociations' in item:
        shell_interface.data['contributors'] = []
        
        file_owner_name = f'{shell_interface.dirpath}/data/pure_rdm_user_id.txt'
        file_owner_data = open(file_owner_name).readlines()

        for i in item['personAssociations']:
            sub_data = {}

            person_uuid = get_value(i, ['person', 'uuid'])

            # Name
            first_name = get_value(i, ['name', 'firstName'])
            last_name  = get_value(i, ['name', 'lastName'])

            if first_name and last_name:
                sub_data['name'] = f'{last_name}, {first_name}'
            elif last_name and not first_name:
                sub_data['name'] = f'{last_name}, (first name not specified)'
            elif first_name and not last_name:
                sub_data['name'] = f'(last name not specified), {first_name}'

            # RDM OWNER
            # Searchs among all users uuid if there is a match
            for line in file_owner_data:
                if person_uuid == line.split(' ')[0]:

                    rdm_record_owner = line.split(' ')[1]
                    
                    if rdm_record_owner not in shell_interface.data['owners']:
                        # Adds RDM user id (record owner) to 'owners'
                        shell_interface.data['owners'].append(rdm_record_owner)


            # ORCID
            person_uuid = get_value(i, ['person', 'uuid'])
            if person_uuid:
                # Only 'person' uuids (internal persons) are in Pure. 
                # 'externalPerson' uuids will not be found (404), therefore it is not possible to get their orcid's
                sub_data['uuid'] = person_uuid
                orcid = get_orcid(shell_interface, person_uuid, sub_data['name'])
                if orcid:
                    sub_data['orcid'] = orcid
            else:
                sub_data = add_to_var(sub_data, i, 'uuid',   ['externalPerson', 'uuid'])

            # Standard fields
            sub_data = add_to_var(sub_data, i, 'externalId',               ['person', 'externalId'])     # 'externalPerson' never have 'externalId'
            sub_data = add_to_var(sub_data, i, 'authorCollaboratorName',   ['authorCollaboration', 'names', 0, 'value'])   
            sub_data = add_to_var(sub_data, i, 'personRole',               ['personRoles', 0, 'value'])    
            sub_data = add_to_var(sub_data, i, 'organisationalUnit',       ['organisationalUnits', 0, 'names', 0, 'value'])
            sub_data = add_to_var(sub_data, i, 'type_p',                   ['externalPerson', 'types', 0, 'value'])

            shell_interface.data['contributors'].append(sub_data)


    # --- organisationalUnits ---
    if 'organisationalUnits' in item:
        shell_interface.data['organisationalUnits'] = []
        sub_data = {}
        for i in item['organisationalUnits']:

            sub_data = add_to_var(sub_data, i, 'name', ['names', 0, 'value'])
            sub_data = add_to_var(sub_data, i, 'link', ['link', 'href'])

        shell_interface.data['organisationalUnits'].append(sub_data)

    # --- Abstract ---  
    if 'abstracts' in item:
        shell_interface.count_abstracts += 1

    shell_interface.data = shell_interface.json.dumps(shell_interface.data)
    open(f'{shell_interface.dirpath}/data/temporary_files/lash_push.json', "w").write(shell_interface.data)

    # Calling post_to_rdm
    return post_to_rdm(shell_interface)



def get_files_data(shell_interface: object, i: dict):
    """ Gets metadata information from electronicVersions and additionalFiles files.
        It also downloads the relative files. The Metadata without file will be ignored """

    if 'file' not in i:
        return False
    elif 'fileURL' not in i['file'] or 'fileName' not in i['file']:
        return False

    internal_review = False     # Default value

    pure_size   = get_value(i, ['file', 'size'])
    pure_name   = get_value(i, ['file', 'fileName'])

    shell_interface.pure_rdm_file_match = []        # [file_match, internalReview]

    # Checks if pure_size and pure_name are the same as any of the files in RDM with the same uuid
    for rdm_file in shell_interface.rdm_file_review:

        rdm_size   = str(rdm_file['size'])
        rdm_review = rdm_file['review']

        if pure_size == rdm_size and pure_name == rdm_file['name']:
            shell_interface.pure_rdm_file_match.append(True)
            shell_interface.pure_rdm_file_match.append(rdm_review)
            internal_review = rdm_review       # The new uploaded file will have the same review value as in RDM
            break

    sub_data = {}

    sub_data['internalReview'] = internal_review

    sub_data = add_to_var(sub_data, i, 'name',            ['file', 'fileName'])
    sub_data = add_to_var(sub_data, i, 'size',            ['file', 'size'])
    sub_data = add_to_var(sub_data, i, 'mimeType',        ['file', 'mimeType'])
    sub_data = add_to_var(sub_data, i, 'digest',          ['file', 'digest'])
    sub_data = add_to_var(sub_data, i, 'digestAlgorithm', ['file', 'digestAlgorithm'])
    sub_data = add_to_var(sub_data, i, 'createdBy',       ['creator'])
    sub_data = add_to_var(sub_data, i, 'createdDate',     ['created'])
    sub_data = add_to_var(sub_data, i, 'versionType',     ['versionTypes', 0, 'value'])
    sub_data = add_to_var(sub_data, i, 'licenseType',     ['licenseTypes', 0, 'value'])
    sub_data = add_to_var(sub_data, i, 'accessType',      ['accessTypes', 0, 'value'])

    # Append to sub_data to .data
    shell_interface.data['versionFiles'].append(sub_data)

    # Download file from Pure
    get_file_from_pure(shell_interface, i)
    return



#   ---         ---         ---
def get_rdm_file_review(shell_interface: object):
    """ When a record is updated in Pure, there will be a check if the new file from Pure is the same as the old file in RDM.
    To do so it makes a comparison on the file size.
    If the size is not the same, then it will be uploaded to RDM and a new internal review will be required. """

    # --- Get file size and internalReview from RDM ---
    sort  = 'sort=mostrecent'
    size  = 'size=100'
    page  = 'page=1'
    query = f'q="{shell_interface.uuid}"'

    headers = {
        'Authorization': f'Bearer {token_rdm}',
        'Content-Type': 'application/json',
    }
    params = (('prettyprint', '1'),)
    url = f'{rdm_api_url_records}api/records/?{sort}&{query}&{size}&{page}'
    response = shell_interface.requests.get(url, headers=headers, params=params, verify=False)

    if response.status_code >= 300:
        print(f'\ntget_rdm_file_size - {shell_interface.uuid} - {response}')
        print(response.content)
        return False

    open(f'{shell_interface.dirpath}/data/temporary_files/rdm_get_recid.json', "wb").write(response.content)

    # Load response
    resp_json = shell_interface.json.loads(response.content)

    total_recids = resp_json['hits']['total']
    if total_recids == 0:
        return False

    record = resp_json['hits']['hits'][0]['metadata']  # [0] because they are ordered, therefore it is the most recent

    if 'versionFiles' in record:
        for file in record['versionFiles']:
            file_size   = file['size']
            file_name   = file['name']
            file_review = file['internalReview']

            shell_interface.rdm_file_review.append({'size': file_size, 'review': file_review, 'name': file_name})

            # print(f'\tFile/s size   - {response} - Number files:  {total_recids}    - Size: {file_size} - Review: {file_review}')
    return

    

#   ---         ---         ---
def add_to_var(sub_data: dict, item: list, rdm_field: str, path: list):
    """ Adds the field to sub_data """
    value = get_value(item, path)

    if rdm_field == 'accessType':
        value = accessright_conversion(value)

    if value:
        sub_data[rdm_field] = value
    return sub_data


#   ---         ---         ---
def add_field(shell_interface: object, item: list, rdm_field: str, path: list):
    """ Adds the field to the data json """
    value = get_value(item, path)

    if rdm_field == 'language':
        value = language_conversion(shell_interface, value)
    elif rdm_field == 'access_right':
        value = accessright_conversion(value)

    if value:
        shell_interface.data[rdm_field] = value
    return


#   ---         ---         ---
def accessright_conversion(pure_value: str):
    
    accessright_pure_to_rdm = {
        'Open':             'open',
        'Embargoed':        'embargoed',
        'Restricted':       'restricted',
        'Closed':           'closed',
        'Unknown':          'closed',
        'Indeterminate':    'closed',
        'None':             'closed'
        }
    if pure_value in accessright_pure_to_rdm:
        return accessright_pure_to_rdm[pure_value]
    else:
        print('\n--- new access_right ---> not in accessright_pure_to_rdmk array\n\n')
        return False


#   ---         ---         ---
def language_conversion(shell_interface: object, pure_language: str):
    if pure_language == 'Undefined/Unknown':
        return False
    
    file_name = f'{shell_interface.dirpath}/iso6393.json'
    resp_json = shell_interface.json.load(open(file_name, 'r'))
    for i in resp_json:
        if i['name'] == pure_language:
            return i['iso6393']
        else:
            # in case there is no match (e.g. spelling mistake in Pure) ignore field
            return False


#   ---         ---         ---
def get_value(item, path: list):
    """ Goes through the json item to get the information of the specified path """

    child = item
    count = 0
    # Iterates over the given path
    for i in path:
        # If the child (step in path) exists or is equal to zero
        if i in child or i == 0:
            # Counts if the iteration took place over every path element
            count += 1
            child = child[i]
        else:
            return False

    # If the full path is not available (missing field)
    if len(path) != count:
        return False

    element = str(child)

    # REPLACEMENTS
    element = element.replace('\t', ' ')        # replace \t with ' '
    element = element.replace('\\', '\\\\')     # adds \ before \
    element = element.replace('"', '\\"')       # adds \ before "
    element = element.replace('\n', '')         # removes new lines

    return element



#   ---         ---         ---
def post_to_rdm(shell_interface: object):

    shell_interface.metadata_success = None
    shell_interface.file_success     = None

    # push_dist_sec is normally set to 3 sec. ~ 1000 records per hour
    shell_interface.time.sleep(push_dist_sec)                        

    data_utf8 = shell_interface.data.encode('utf-8')
    
    # POST REQUEST metadata
    headers = {
        'Content-Type': 'application/json',
    }
    params = (
        ('prettyprint', '1'),
    )
    url = f'{rdm_api_url_records}api/records/'
    response = shell_interface.requests.post(url, headers=headers, params=params, data=data_utf8, verify=False)

    # Count http responses
    if response.status_code not in shell_interface.count_http_responses:
        shell_interface.count_http_responses[response.status_code] = 0
    shell_interface.count_http_responses[response.status_code] += 1

    uuid = shell_interface.item["uuid"]
    print(f'\tPost metadata - {response} - Uuid:                 {uuid}')
    
    current_time = shell_interface.datetime.now().strftime("%H:%M:%S")
    report = f'{current_time} - metadata_to_rdm - {str(response)} - {uuid} - {shell_interface.item["title"]}\n'

    # RESPONSE CHECK
    if response.status_code >= 300:

        shell_interface.count_errors_push_metadata += 1

        # metadata transmission success flag
        shell_interface.metadata_success = False
        
        # error description from invenioRDM
        report += f'{response.content}\n'
        print(response.content)

        # Add record to to_transfer.txt to be re pushed afterwards
        open(f'{shell_interface.dirpath}/data/to_transfer.txt', "a").write(f'{uuid}\n')

    file_name = f'{shell_interface.dirpath}/reports/{shell_interface.date.today()}_records.log'
    open(file_name, "a").write(report)

    if response.status_code == 429:
        print('Waiting 15 min')
        shell_interface.time.sleep(wait_429)                     # 429 too many requests, wait 15 min
    
    # In case of SUCCESSFUL TRANSMISsION
    if response.status_code < 300:

        shell_interface.count_successful_push_metadata += 1

        # metadata transmission success flag
        shell_interface.metadata_success = True

        # After pushing the record's metadata to RDM needs about a second to be able to get its recid
        shell_interface.time.sleep(1)

        # Gets recid from RDM
            #   - to check if there are duplicates
            #   - to delete duplicates
            #   - to add the record uuid and recid to all_rdm_records.txt
        
        recid = rdm_get_recid(shell_interface, uuid)
        if not recid:
            return False

        # - Upload record FILES to RDM -
        for file_name in shell_interface.record_files:
            rdm_put_file(shell_interface, file_name, recid, uuid)
                       
        if recid:
            # add record to all_rdm_records
            uuid_recid_line = f'{uuid} {recid}\n'
            open(f'{shell_interface.dirpath}/data/all_rdm_records.txt', "a").write(uuid_recid_line)


    # FINALL SUCCESS CHECK
    if(shell_interface.metadata_success == False or shell_interface.file_success == False):
        return False
    else:
        # # Push RDM record link to Pure                                # TODO
        # shell_interface.api_url
        # shell_interface.landing_page_url

        # if uuid in to_transfer then removes it
        file_name = f'{shell_interface.dirpath}/data/to_transfer.txt'
        with open(file_name, "r") as f:
            lines = f.readlines()
        with open(file_name, "w") as f:
            for line in lines:
                if line.strip("\n") != uuid:
                    f.write(line)
    return True



#   ---         ---         ---
def get_orcid(shell_interface: object, person_uuid: str, name: str):
    headers = {
    'Accept': 'application/json',
    }
    params = (
        ('apiKey', pure_api_key),
    )
    url = f'{pure_rest_api_url}/persons/{person_uuid}'
    response = shell_interface.requests.get(url, headers=headers, params=params)
    open(f'{shell_interface.dirpath}/data/temporary_files/resp_pure_persons.json', 'wb').write(response.content)
    
    shell_interface.time.sleep(0.1)
    
    if response.status_code >= 300:
        print(response.content)
        return False

    resp_json = shell_interface.json.loads(response.content)

    message = f'\tPureGet Orcid - {response}'
    if 'orcid' in resp_json:
        shell_interface.count_orcids += 1
        orcid = resp_json['orcid']
        print(f'{message} - {orcid} - {name}')
        return orcid

    print(f'{message} - Not found           - {name}')
    return False