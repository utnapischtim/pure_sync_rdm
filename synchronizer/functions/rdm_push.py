from setup import *
from functions.rdm_put_file import rdm_put_file, get_record_recid
from requests.auth import HTTPBasicAuth

#   ---         ---         ---
def create_invenio_data(my_prompt):

    # try:
    my_prompt.record_files = []
    item = my_prompt.item
    my_prompt.uuid = item['uuid']

    my_prompt.data = '{'
    my_prompt.data += '"owners": [1], '
    my_prompt.data += '"_access": {"metadata_restricted": false, "files_restricted": false}, '
    
                        # invenio field name                  # PURE json path
    add_field(my_prompt, item, 'title',                             ['title'])
    add_field(my_prompt, item, 'publicationDatePure',               ['publicationStatuses', 0, 'publicationDate', 'year'])
    add_field(my_prompt, item, 'createdDatePure',                   ['info', 'createdDate'])
    add_field(my_prompt, item, 'modifiedDatePure',                  ['info', 'modifiedDate'])
    add_field(my_prompt, item, 'pureId',                            ['pureId'])
    add_field(my_prompt, item, 'uuid',                              ['uuid'])                                                                   
    add_field(my_prompt, item, 'type_p',                            ['types', 0, 'value'])                                                     
    add_field(my_prompt, item, 'category',                          ['categories', 0, 'value'])                                              
    add_field(my_prompt, item, 'peerReview',                        ['peerReview'])                                                         
    add_field(my_prompt, item, 'publicationStatus',                 ['publicationStatuses', 0, 'publicationStatuses', 0, 'value'])
    add_field(my_prompt, item, 'language',                          ['languages', 0, 'value'])
    add_field(my_prompt, item, 'totalNumberOfAuthors',              ['totalNumberOfAuthors'])
    add_field(my_prompt, item, 'managingOrganisationalUnit',        ['managingOrganisationalUnit', 'names', 0, 'value'])
    add_field(my_prompt, item, 'workflow',                          ['workflows', 0, 'value'])
    add_field(my_prompt, item, 'confidential',                      ['confidential'])
    add_field(my_prompt, item, 'publisherName',                     ['publisher', 'names', 0, 'value'])
    add_field(my_prompt, item, 'access_right',                      ['openAccessPermissions', 0, 'value'])
    add_field(my_prompt, item, 'pages',                             ['info','pages'])                                                     
    add_field(my_prompt, item, 'volume',                            ['info','volume'])                                                         
    add_field(my_prompt, item, 'versionType',                       ['electronicVersions', 0, 'versionType', 'value'])    # review                
    add_field(my_prompt, item, 'licenseType',                       ['electronicVersions', 0, 'licenseType', 'value'])    # review
    add_field(my_prompt, item, 'journalTitle',                      ['info', 'journalAssociation', 'title', 'value'])
    add_field(my_prompt, item, 'journalNumber',                     ['info', 'journalNumber'])

    if 'electronicVersions' in item:
        cnt = 0
        for EV in item['electronicVersions']:
            if 'file' in EV:
                if 'fileURL' in EV['file'] and 'fileName' in EV['file']:
                    
                    if cnt == 0:
                        my_prompt.data += '"versionFiles": ['
                    cnt += 1

                    my_prompt.data += '{'
                    add_field(my_prompt, EV, 'fileName',                          ['file', 'fileName'])
                    add_field(my_prompt, EV, 'fileModifBy',                       ['creator'])
                    add_field(my_prompt, EV, 'fileModifDate',                     ['created'])
                    add_field(my_prompt, EV, 'fileType',                          ['file', 'mimeType'])
                    add_field(my_prompt, EV, 'fileAccessType',                    ['accessTypes', 0, 'value'])
                    add_field(my_prompt, EV, 'fileSize',                          ['file', 'size'])
                    add_field(my_prompt, EV, 'fileDigest',                        ['file', 'digest'])
                    add_field(my_prompt, EV, 'fileDigestAlgorithm',               ['file', 'digestAlgorithm'])

                    my_prompt.data = my_prompt.data[:-2]
                    my_prompt.data += '}, '                                  # end review

                    # DOWNLOAD FILE FROM PURE
                    file_name = EV['file']['fileName']
                    file_url  = EV['file']['fileURL']
                    response = my_prompt.requests.get(file_url, auth=HTTPBasicAuth(pure_username, pure_password))
                    print(f'Pure download file\t->\t{response}\t({file_name})')

                    # SAVE FILE
                    if response.status_code < 300:
                        open(str(my_prompt.dirpath) + '/data/temporary_files/' + file_name, 'wb').write(response.content)
                        my_prompt.record_files.append(file_name)
        if cnt > 0:
            my_prompt.data = my_prompt.data[:-2]       
            my_prompt.data += '], '


    # --- personAssociations ---
    if 'personAssociations' in item:
        my_prompt.data += '"contributors": ['
        for i in item['personAssociations']:
            my_prompt.data += '{'
            
            if 'name' in i:
                if 'firstName' in i['name'] and 'lastName' in i['name']:
                    full_name = i['name']['lastName'] + ', '
                    full_name += i['name']['firstName']
                    my_prompt.data += f'"name": "{full_name}", '
                else:   
                    my_prompt.data += '"name": "Name not specified", '
            elif 'authorCollaboratorName' in i:
                my_prompt.data += '"name": "See authorCollaboratorName", '
            else:   
                my_prompt.data += '"name": "Name not specified", '

            add_field(my_prompt, i, 'authorCollaboratorName',         ['authorCollaboration', 'names', 0, 'value'])    
            add_field(my_prompt, i, 'personRole',                     ['personRoles', 0, 'value'])    
            add_field(my_prompt, i, 'organisationalUnit',             ['organisationalUnits', 0, 'names', 0, 'value'])
            add_field(my_prompt, i, 'link',                           ['person', 'link', 'href'])
            add_field(my_prompt, i, 'link',                           ['externalPerson', 'link', 'href'])
            add_field(my_prompt, i, 'type_p',                         ['externalPerson', 'types', 0, 'value'])
            my_prompt.data = my_prompt.data[:-2]                          # removes last 2 characters
            my_prompt.data += '}, '

        my_prompt.data = my_prompt.data[:-2]       
        my_prompt.data += '], '

    # --- organisationalUnits ---
    if 'organisationalUnits' in item:
        my_prompt.data += '"organisationalUnits": ['
        for i in item['organisationalUnits']:
            my_prompt.data += '{'
            add_field(my_prompt, i, 'name',                           ['names', 0, 'value'])
            add_field(my_prompt, i, 'link',                           ['link', 'href'])
            my_prompt.data = my_prompt.data[:-2]
            my_prompt.data += '}, '
            
        my_prompt.data = my_prompt.data[:-2]
        my_prompt.data += '], '

    my_prompt.data = my_prompt.data[:-2]
    my_prompt.data += '}'          # End data

    return post_to_rdm(my_prompt)

    # except:
    #     print('\n- Error in create_invenio_data method -\n')


#   ---         ---         ---
def add_field(my_prompt, item, inv_field, path):

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
        if inv_field == 'language':
            if element == 'Undefined/Unknown':
                return
            else:
                resp_json = my_prompt.json.load(open(my_prompt.dirpath + '/iso6393.json', 'r'))
                for i in resp_json:
                    if i['name'] == element:
                        element = i['iso6393']
                    else:
                        # in case there is no match (e.g. spelling mistake in Pure) ignore field
                        return

        # - ACCESS_RIGHT -
        #   RDM access right (https://github.com/inveniosoftware/invenio-rdm-records/issues/37):
        #   open        ->  metadata available              files available
        #   embargoed   ->  metadata available              files available after embargo date      (unless user has permission)
        #   restricted  ->  metadata available              files restricted                        (unless user has permission)
        #   closed      ->  metadata restricted             files restricted                        (unless user has permission)

        if inv_field == 'access_right':
            if 'openAccessPermissions' in item:
                pure_value = item['openAccessPermissions'][0]['value']
                accessRight_Pure_to_RDM = {
                    'Open':             'open',
                    'Indeterminate':    'closed',          # REVIEW!!!!
                    'None':             'closed',
                    'Closed':           'closed'
                    }
                if pure_value in accessRight_Pure_to_RDM:

                    element  = accessRight_Pure_to_RDM[pure_value]
                else:
                    print('\n--- new access_right ---> not in accessRight_Pure_to_RDM array\n\n')

        # Adding field
        my_prompt.data += '"' + inv_field + '": "' + element + '", '
        return

    except:
        print('\n- Error in add_field method -\n')

#   ---         ---         ---
def post_to_rdm(my_prompt):

    # try:
    my_prompt.metadata_success = None
    my_prompt.file_success =     None
    my_prompt.time.sleep(push_dist_sec)                        # ~ 5000 records per hour

    data_utf8 = my_prompt.data.encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
    }
    params = (
        ('prettyprint', '1'),
    )
    # POST REQUEST metadata
    url = f'{rdm_api_url_records}api/records/'
    response = my_prompt.requests.post(url, headers=headers, params=params, data=data_utf8, verify=False)

    # RESPONSE CHECK
    print(f'RDM post metadata\t->\t{response}')                

    # adds metadata http response codes into array
    if response.status_code not in my_prompt.count_http_response_codes:
        my_prompt.count_http_response_codes[response.status_code] = 0

    my_prompt.count_http_response_codes[response.status_code] += 1


    uuid = my_prompt.item["uuid"]
    current_time = my_prompt.datetime.now().strftime("%H:%M:%S")

    report = f'{current_time} - metadata_to_rdm - {str(response)} - {uuid} - {my_prompt.item["title"]}\n'

    if response.status_code >= 300:

        my_prompt.cnt_errors += 1
        print(response.content)

        # metadata transmission success flag
        my_prompt.metadata_success = False

        # post json error_jsons
        if response.status_code != 429:
            file_name = f'{my_prompt.dirpath}/data/temporary_files/error_jsons/{uuid}.json'
            open(file_name, "w").write(str(my_prompt.data))
        
        # error description from invenioRDM
        report += str(response.content) + '\n'

        # append records to re-transfer
        if my_prompt.exec_type != 'by_id':
            open(my_prompt.dirpath + "/data/to_transfer.txt", "a").write(uuid + "\n")

    file_name = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_rdm-push-records.log'
    open(file_name, "a").write(report)

    if response.status_code == 429:
        print('Waiting 15 min')
        my_prompt.time.sleep(wait_429)                     # 429 too many requests, wait 15 min

    # -- Successful transmition --
    if response.status_code < 300:

        # metadata transmission success flag
        my_prompt.metadata_success = True

        # - Upload record FILES to RDM -
        if len(my_prompt.record_files) > 0:
            for file_name in my_prompt.record_files:
                rdm_put_file(my_prompt, file_name)
            
        # in case there no file to transfer, gets recid
        else:
            get_record_recid(my_prompt)            

        # add uuid to all_rdm_records
        uuid_recid_line = f'{uuid} {my_prompt.recid}\n'
        open(my_prompt.dirpath + "/data/all_rdm_records.txt", "a").write(uuid_recid_line)


    # FINALL SUCCESS CHECK
    # print(f'Success check -> metadata: {my_prompt.metadata_success} - file: {my_prompt.file_success}')
    if(my_prompt.metadata_success == False or my_prompt.file_success == False):
        return False
    else:
        delete_errorJson_and_toTransfer(my_prompt, uuid)
        return True

    # except:
    #     print('\n- Error in post_to_rdm method -\n')



#   ---         ---         ---
def delete_errorJson_and_toTransfer(my_prompt, uuid):

    # if uuid in to_transfer then removes it
    file_name = my_prompt.dirpath + "/data/to_transfer.txt"
    with open(file_name, "r") as f:
        lines = f.readlines()
    with open(file_name, "w") as f:
        for line in lines:
            if line.strip("\n") != uuid:
                f.write(line)

    # Get file names from folder
    isfile = my_prompt.os.path.isfile
    join = my_prompt.os.path.join
    folder = '/data/temporary_files/error_jsons/'
    onlyfiles = [f for f in my_prompt.os.listdir(my_prompt.dirpath + folder) if isfile(join(my_prompt.dirpath + folder, f))]

    for file_name in onlyfiles:
        file_uuid = file_name.split('.')[0]
        
        if file_uuid == uuid:
            my_prompt.os.remove(my_prompt.dirpath + folder + file_name)
            print(f'Correct transmission -> The file /data/temporary_files/error_jsons/{file_name} has been deleted.\n')
    
