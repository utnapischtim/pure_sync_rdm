from setup                          import *
from functions.rdm_put_file         import rdm_put_file
from functions.general_functions    import rdm_get_recid
from requests.auth                  import HTTPBasicAuth

#   ---         ---         ---
def rdm_push_record(shell_interface, uuid):
    """ Method used to get from Pure record's metadata """
    
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

    shell_interface.data = '{'
    shell_interface.data += '"owners": [1], '
    shell_interface.data += '"_access": {"metadata_restricted": false, "files_restricted": false}, '
    
                              # RDM field name                    # PURE json path
    add_field(shell_interface, item, 'title',                             ['title'])
    add_field(shell_interface, item, 'publicationDatePure',               ['publicationStatuses', 0, 'publicationDate', 'year'])
    add_field(shell_interface, item, 'createdDatePure',                   ['info', 'createdDate'])
    add_field(shell_interface, item, 'modifiedDatePure',                  ['info', 'modifiedDate'])
    add_field(shell_interface, item, 'pureId',                            ['pureId'])
    add_field(shell_interface, item, 'uuid',                              ['uuid'])                                                                   
    add_field(shell_interface, item, 'type_p',                            ['types', 0, 'value'])                                                     
    add_field(shell_interface, item, 'category',                          ['categories', 0, 'value'])                                              
    add_field(shell_interface, item, 'peerReview',                        ['peerReview'])                                                         
    add_field(shell_interface, item, 'publicationStatus',                 ['publicationStatuses', 0, 'publicationStatuses', 0, 'value'])
    add_field(shell_interface, item, 'language',                          ['languages', 0, 'value'])
    add_field(shell_interface, item, 'totalNumberOfAuthors',              ['totalNumberOfAuthors'])
    add_field(shell_interface, item, 'managingOrganisationalUnit',        ['managingOrganisationalUnit', 'names', 0, 'value'])
    add_field(shell_interface, item, 'workflow',                          ['workflows', 0, 'value'])
    add_field(shell_interface, item, 'confidential',                      ['confidential'])
    add_field(shell_interface, item, 'publisherName',                     ['publisher', 'names', 0, 'value'])
    add_field(shell_interface, item, 'access_right',                      ['openAccessPermissions', 0, 'value'])
    add_field(shell_interface, item, 'pages',                             ['info','pages'])                                                     
    add_field(shell_interface, item, 'volume',                            ['info','volume'])
    add_field(shell_interface, item, 'journalTitle',                      ['info', 'journalAssociation', 'title', 'value'])
    add_field(shell_interface, item, 'journalNumber',                     ['info', 'journalNumber'])

    # ELECTRONIC VERSIONS
    if 'electronicVersions' in item:
        count = 0
        for electronic_version in item['electronicVersions']:
            if 'file'     in electronic_version:
                if 'fileURL'  in electronic_version['file'] and 'fileName' in electronic_version['file']:
                    if count == 0:
                        shell_interface.data += '"versionFiles": ['
                    count += 1

                    shell_interface.data += '{'
                    add_field(shell_interface, electronic_version, 'fileName',                ['file', 'fileName'])
                    add_field(shell_interface, electronic_version, 'fileModifBy',             ['creator'])
                    add_field(shell_interface, electronic_version, 'fileModifDate',           ['created'])
                    add_field(shell_interface, electronic_version, 'fileType',                ['file', 'mimeType'])
                    add_field(shell_interface, electronic_version, 'fileSize',                ['file', 'size'])
                    add_field(shell_interface, electronic_version, 'fileDigest',              ['file', 'digest'])
                    add_field(shell_interface, electronic_version, 'fileDigestAlgorithm',     ['file', 'digestAlgorithm'])

                    add_field(shell_interface, electronic_version, 'fileAccessType',          ['accessTypes', 0, 'value'])
                    add_field(shell_interface, electronic_version, 'fileVersionType',         ['versionType', 0, 'value'])
                    add_field(shell_interface, electronic_version, 'fileLicenseType',         ['licenseType', 0, 'value'])

                    shell_interface.data = shell_interface.data[:-2]
                    shell_interface.data += '}, '                                  # end review

                    # DOWNLOAD FILE FROM PURE
                    file_name = electronic_version['file']['fileName']
                    file_url  = electronic_version['file']['fileURL']
                    response = shell_interface.requests.get(file_url, auth=HTTPBasicAuth(pure_username, pure_password))
                    print(f'\tDownload file\t->\t{response} - ({file_name})')

                    if response.status_code < 300:
                        # Save file
                        open(f'{shell_interface.dirpath}/data/temporary_files/{file_name}', 'wb').write(response.content)

                        # ISSUE encountered when putting txt files
                        file_extension = file_name.split('.')[file_name.count('.')]
                        if file_extension == 'txt':
                            print('\nATTENTION, the file extension is txt')
                            print('Known issue -> jinja2.exceptions.UndefinedError: No first item, sequence was empty.\n')                        
                        # Put file to RDM
                        shell_interface.record_files.append(file_name)
                    else:
                        print(f'Error downloading file from pure ({file_url})')


        if count > 0:
            shell_interface.data = shell_interface.data[:-2]       
            shell_interface.data += '], '


    # --- personAssociations ---
    if 'personAssociations' in item:
        shell_interface.data += '"contributors": ['
        for i in item['personAssociations']:
            shell_interface.data += '{'
            
            if 'name' in i:
                if 'firstName' in i['name'] and 'lastName' in i['name']:
                    full_name = i['name']['lastName'] + ', '
                    full_name += i['name']['firstName']
                    shell_interface.data += f'"name": "{full_name}", '
                else:   
                    shell_interface.data += '"name": "Name not specified", '
            elif 'authorCollaboratorName' in i:
                shell_interface.data += '"name": "See authorCollaboratorName", '
            else:   
                shell_interface.data += '"name": "Name not specified", '

            add_field(shell_interface, i, 'authorCollaboratorName',         ['authorCollaboration', 'names', 0, 'value'])    
            add_field(shell_interface, i, 'personRole',                     ['personRoles', 0, 'value'])    
            add_field(shell_interface, i, 'organisationalUnit',             ['organisationalUnits', 0, 'names', 0, 'value'])
            add_field(shell_interface, i, 'link',                           ['person', 'link', 'href'])
            add_field(shell_interface, i, 'link',                           ['externalPerson', 'link', 'href'])
            add_field(shell_interface, i, 'type_p',                         ['externalPerson', 'types', 0, 'value'])
            shell_interface.data = shell_interface.data[:-2]                          # removes last 2 characters
            shell_interface.data += '}, '

        shell_interface.data = shell_interface.data[:-2]       
        shell_interface.data += '], '

    # --- organisationalUnits ---
    if 'organisationalUnits' in item:
        shell_interface.data += '"organisationalUnits": ['
        for i in item['organisationalUnits']:
            shell_interface.data += '{'
            add_field(shell_interface, i, 'name',                           ['names', 0, 'value'])
            add_field(shell_interface, i, 'link',                           ['link', 'href'])
            shell_interface.data = shell_interface.data[:-2]
            shell_interface.data += '}, '
            
        shell_interface.data = shell_interface.data[:-2]
        shell_interface.data += '], '

    shell_interface.data = shell_interface.data[:-2]
    shell_interface.data += '}'

    open(f'{shell_interface.dirpath}/data/temporary_files/lash_push.json', "w").write(shell_interface.data)

    return post_to_rdm(shell_interface)


#   ---         ---         ---
def add_field(shell_interface, item, rdm_field, path):
    try:
        child = item
        cnt = 0
        for i in path:
            if i in child or i == 0:
                cnt += 1
                child = child[i]
            else:
                return

        # the full path is not available (missing field)
        if len(path) != cnt:    return
        
        element = str(child)

        # REPLACEMENTS
        element = element.replace('\t', ' ')        # replace \t with ' '
        element = element.replace('\\', '\\\\')     # adds \ before \
        element = element.replace('"', '\\"')       # adds \ before "
        element = element.replace('\n', '')         # removes new lines

        # Language translation to iso 369-3
        if rdm_field == 'language':
            if element == 'Undefined/Unknown':
                return
            else:
                resp_json = shell_interface.json.load(open(shell_interface.dirpath + '/iso6393.json', 'r'))
                for i in resp_json:
                    if i['name'] == element:
                        element = i['iso6393']
                    else:
                        # in case there is no match (e.g. spelling mistake in Pure) ignore field
                        return

        # - RDM ACCESS RIGHT -
        #   RDM access right (https://github.com/inveniosoftware/invenio-rdm-records/issues/37):
        #   open        ->  metadata available              files available
        #   embargoed   ->  metadata available              files available after embargo date      (unless user has permission)
        #   restricted  ->  metadata available              files restricted                        (unless user has permission)
        #   closed      ->  metadata restricted             files restricted                        (unless user has permission)

        # - PURE ACCESS RIGHT -
        #   Open:           Full text accessible openly on Portal/Web service/Backend
        #   Embargoed:      Full text accessible openly on Portal/Web service/Backend after end of embargo
        #   Restricted:     Full text accessible in Backend and IP restricted
        #   Closed:         Full text accessible in Backend only for related persons and related editors
        #   Unknown:        Public access to file not known

        if rdm_field == 'access_right':
            if 'openAccessPermissions' in item:

                # element = 'closed'               # default value

                pure_value = item['openAccessPermissions'][0]['value']
                accessRight_pure_to_rdm = {
                    'Open':             'open',
                    'Embargoed':        'embargoed',
                    'Restricted':       'restricted',
                    'Closed':           'closed',
                    'Unknown':          'closed',
                    'Indeterminate':    'closed',
                    'None':             'closed'
                    }
                if pure_value in accessRight_pure_to_rdm:
                    element  = accessRight_pure_to_rdm[pure_value]
                else:
                    print('\n--- new access_right ---> not in accessRight_pure_to_rdm array\n\n')
                    
        # Adding field
        shell_interface.data += f'"{rdm_field}": "{element}", '
        return

    except:
        print('\n- Error in add_field method -\n')

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
            # Normally it gets the recid just when putting a file into RDM
            # Now it does it always:
            #   - to check if there are duplicates
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

