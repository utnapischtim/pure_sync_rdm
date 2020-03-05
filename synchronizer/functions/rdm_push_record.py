from setup                          import *
from functions.get_put_file         import rdm_put_file, get_file_from_pure
from functions.general_functions    import rdm_get_recid

#   ---         ---         ---
def rdm_push_record(shell_interface, uuid: str):
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

    print(f'\n\tGet metadata\t->\t{response}')

    if response.status_code >= 300:
        shell_interface.count_uuid_not_found_in_pure += 1
        print(response.content)

        file_name = f'{shell_interface.dirpath}/reports/{shell_interface.date.today()}_records.log'
        report = f'Get metadata from Pure - {response.content}\n'
        open(file_name, "a").write(report)

        shell_interface.time.sleep(1)
        return 

    file_name = f'{shell_interface.dirpath}/data/temporary_files/resp_pure.json'
    open(file_name, 'wb').write(response.content)
    shell_interface.item = shell_interface.json.loads(response.content)

    # resp_json = open(shell_interface.dirpath + '/data/temporary_files/resp_pure.json', 'r')             # -- TEMPORARY -- 
    # shell_interface.item = shell_interface.json.load(resp_json)                                         # -- TEMPORARY -- 
    
    # Creates data to push to InvenioRDM
    return create_invenio_data(shell_interface)


#   ---         ---         ---
def create_invenio_data(shell_interface):
    """ Gets the necessary information from Pure response in order to
        create the json that will be pushed to RDM """

    shell_interface.count_total += 1      # counts all records

    shell_interface.record_files = []
    item = shell_interface.item
    shell_interface.uuid = item['uuid']

    shell_interface.data = {}
    shell_interface.data['owners']       = [1]
    shell_interface.data['_access']      = {'metadata_restricted': False, 'files_restricted': False}

                        # RDM field name                # PURE json path
    add_field(shell_interface, item, 'title',                       ['title'])
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
    add_field(shell_interface, item, 'access_right',                ['openAccessPermissions', 0, 'value'])

    
    # --- electronicVersions ---
    if 'electronicVersions' in item:
        shell_interface.data['versionFiles'] = []
        sub_data = {}
        for i in item['electronicVersions']:
            if 'file' not in i:
                continue
            elif 'fileURL' not in i['file'] or 'fileName' not in i['file']:
                continue

            sub_data = add_to_var(sub_data, i, 'fileName',            ['file', 'fileName'])
            sub_data = add_to_var(sub_data, i, 'fileSize',            ['file', 'size'])
            sub_data = add_to_var(sub_data, i, 'fileType',            ['file', 'mimeType'])
            sub_data = add_to_var(sub_data, i, 'fileDigest',          ['file', 'digest'])
            sub_data = add_to_var(sub_data, i, 'fileDigestAlgorithm', ['file', 'digestAlgorithm'])
            sub_data = add_to_var(sub_data, i, 'fileModifBy',         ['creator'])
            sub_data = add_to_var(sub_data, i, 'fileModifDate',       ['created'])
            sub_data = add_to_var(sub_data, i, 'fileAccessType',      ['accessTypes', 0, 'value'])
            sub_data = add_to_var(sub_data, i, 'fileVersionType',     ['versionType', 0, 'value'])
            sub_data = add_to_var(sub_data, i, 'fileLicenseType',     ['licenseType', 0, 'value'])

            shell_interface.data['versionFiles'].append(sub_data)

            # Download file from Pure
            get_file_from_pure(shell_interface, i)


    # --- personAssociations ---
    if 'personAssociations' in item:
        shell_interface.data['contributors'] = []
        sub_data = {}
        for i in item['personAssociations']:

            first_name = get_value(i, ['name', 'firstName'])
            last_name  = get_value(i, ['name', 'lastName'])

            if first_name and last_name:
                sub_data['name'] = f'{last_name}, {first_name}'
            elif last_name and not first_name:
                sub_data['name'] = f'{last_name}, (first name not specified)'
            elif first_name and not last_name:
                sub_data['name'] = f'(last name not specified), {first_name}'

            sub_data = add_to_var(sub_data, i, 'authorCollaboratorName',   ['authorCollaboration', 'names', 0, 'value'])   
            sub_data = add_to_var(sub_data, i, 'personRole',               ['personRoles', 0, 'value'])    
            sub_data = add_to_var(sub_data, i, 'organisationalUnit',       ['organisationalUnits', 0, 'names', 0, 'value'])
            sub_data = add_to_var(sub_data, i, 'link',                     ['person', 'link', 'href'])
            sub_data = add_to_var(sub_data, i, 'link',                     ['externalPerson', 'link', 'href'])
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


    shell_interface.data = shell_interface.json.dumps(shell_interface.data)
    open(f'{shell_interface.dirpath}/data/temporary_files/lash_push.json', "w").write(shell_interface.data)

    # Calling post_to_rdm
    return post_to_rdm(shell_interface)


#   ---         ---         ---
def add_to_var(sub_data: dict, item: list, rdm_field: str, path: list):
    """ Adds the field to sub_data """
    value = get_value(item, path)
    if value:
        sub_data[rdm_field] = value
    return sub_data


#   ---         ---         ---
def add_field(shell_interface, item: list, rdm_field: str, path: list):
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
def language_conversion(shell_interface, pure_language: str):
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
    cnt = 0
    # Iterates over the given path
    for i in path:
        # If the child (step in path) exists or is equal to zero
        if i in child or i == 0:
            # Counts if the iteration took place over every path element
            cnt += 1
            child = child[i]
        else:
            return False

    # If the full path is not available (missing field)
    if len(path) != cnt:
        return False

    element = str(child)

    # REPLACEMENTS
    element = element.replace('\t', ' ')        # replace \t with ' '
    element = element.replace('\\', '\\\\')     # adds \ before \
    element = element.replace('"', '\\"')       # adds \ before "
    element = element.replace('\n', '')         # removes new lines

    return element



#   ---         ---         ---
def post_to_rdm(shell_interface):

    shell_interface.metadata_success = None
    shell_interface.file_success     = None
    shell_interface.time.sleep(push_dist_sec)                        # ~ 5000 records per hour

    data_utf8 = shell_interface.data.encode('utf-8')
    
    headers = {
        'Content-Type': 'application/json',
    }
    params = (
        ('prettyprint', '1'),
    )
    # POST REQUEST metadata
    url = f'{rdm_api_url_records}api/records/'
    response = shell_interface.requests.post(url, headers=headers, params=params, data=data_utf8, verify=False)

    uuid = shell_interface.item["uuid"]

    # RESPONSE CHECK
    # print(f'{shell_interface.count_total} - RDM post metadata\t->\t{response} - {uuid}')
    print(f'\tPost metadata\t->\t{response} - {uuid}')
    
    current_time = shell_interface.datetime.now().strftime("%H:%M:%S")

    report = f'{current_time} - metadata_to_rdm - {str(response)} - {uuid} - {shell_interface.item["title"]}\n'

    if response.status_code >= 300:

        shell_interface.count_errors_push_metadata += 1
        print(response.content)

        # metadata transmission success flag
        shell_interface.metadata_success = False
        
        # error description from invenioRDM
        report += f'{response.content}\n'

        # Add record to to_transfer.txt to be re pushed afterwards
        open(f'{shell_interface.dirpath}/data/to_transfer.txt', "a").write(f'{uuid}\n')


    file_name = f'{shell_interface.dirpath}/reports/{shell_interface.date.today()}_records.log'
    open(file_name, "a").write(report)

    if response.status_code == 429:
        print('Waiting 15 min')
        shell_interface.time.sleep(wait_429)                     # 429 too many requests, wait 15 min

    # -- Successful transmition --
    if response.status_code < 300:

        shell_interface.count_successful_push_metadata += 1

        # metadata transmission success flag
        shell_interface.metadata_success = True

        # Gets recid from RDM
            #   - to check if there are duplicates
            #   - to delete duplicates
            #   - to add the record uuid and recid to all_rdm_records.txt
        recid = rdm_get_recid(shell_interface, uuid) 

        # - Upload record FILES to RDM -
        if len(shell_interface.record_files) > 0:
            for file_name in shell_interface.record_files:
                rdm_put_file(shell_interface, file_name, recid)
                       
        if recid:
            # add uuid to all_rdm_records
            uuid_recid_line = f'{uuid} {recid}\n'
            open(f'{shell_interface.dirpath}/data/all_rdm_records.txt', "a").write(uuid_recid_line)


    # FINALL SUCCESS CHECK
    if(shell_interface.metadata_success == False or shell_interface.file_success == False):
        return False
    else:
        # if uuid in to_transfer then removes it
        file_name = f'{shell_interface.dirpath}/data/to_transfer.txt'
        with open(file_name, "r") as f:
            lines = f.readlines()
        with open(file_name, "w") as f:
            for line in lines:
                if line.strip("\n") != uuid:
                    f.write(line)
        return True

