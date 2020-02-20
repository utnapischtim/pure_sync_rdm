from setup import *
from functions.rdm_put_file import rdm_put_file, get_record_recid
from requests.auth import HTTPBasicAuth

#   ---         ---         ---
def create_invenio_data(self):

    try:
        self.record_files = []
        item = self.item
        self.uuid = item['uuid']

        self.data = '{'
        self.data += '"owners": [1], '
        self.data += '"_access": {"metadata_restricted": false, "files_restricted": false}, '
        
                            # invenio field name                  # PURE json path
        add_field(self, item, 'title',                             ['title'])
        add_field(self, item, 'publicationDatePure',               ['publicationStatuses', 0, 'publicationDate', 'year'])
        add_field(self, item, 'createdDatePure',                   ['info', 'createdDate'])
        add_field(self, item, 'modifiedDatePure',                  ['info', 'modifiedDate'])
        add_field(self, item, 'pureId',                            ['pureId'])
        add_field(self, item, 'uuid',                              ['uuid'])                                                                   
        add_field(self, item, 'type_p',                            ['types', 0, 'value'])                                                     
        add_field(self, item, 'category',                          ['categories', 0, 'value'])                                              
        add_field(self, item, 'peerReview',                        ['peerReview'])                                                         
        add_field(self, item, 'publicationStatus',                 ['publicationStatuses', 0, 'publicationStatuses', 0, 'value'])
        add_field(self, item, 'language',                          ['languages', 0, 'value'])
        add_field(self, item, 'totalNumberOfAuthors',              ['totalNumberOfAuthors'])
        add_field(self, item, 'managingOrganisationalUnit',        ['managingOrganisationalUnit', 'names', 0, 'value'])
        add_field(self, item, 'workflow',                          ['workflows', 0, 'value'])
        add_field(self, item, 'confidential',                      ['confidential'])
        add_field(self, item, 'publisherName',                     ['publisher', 'names', 0, 'value'])
        add_field(self, item, 'access_right',                      ['openAccessPermissions', 0, 'value'])
        add_field(self, item, 'pages',                             ['info','pages'])                                                     
        add_field(self, item, 'volume',                            ['info','volume'])                                                         
        add_field(self, item, 'versionType',                       ['electronicVersions', 0, 'versionType', 'value'])    # review                
        add_field(self, item, 'licenseType',                       ['electronicVersions', 0, 'licenseType', 'value'])    # review
        add_field(self, item, 'journalTitle',                      ['info', 'journalAssociation', 'title', 'value'])
        add_field(self, item, 'journalNumber',                     ['info', 'journalNumber'])

        if 'electronicVersions' in item:
            cnt = 0
            for EV in item['electronicVersions']:
                if 'file' in EV:
                    if 'fileURL' in EV['file'] and 'fileName' in EV['file']:
                        
                        if cnt == 0:
                            self.data += '"versionFiles": ['
                        cnt += 1

                        self.data += '{'
                        add_field(self, EV, 'fileName',                          ['file', 'fileName'])
                        add_field(self, EV, 'fileModifBy',                       ['creator'])
                        add_field(self, EV, 'fileModifDate',                     ['created'])
                        add_field(self, EV, 'fileType',                          ['file', 'mimeType'])
                        add_field(self, EV, 'fileAccessType',                    ['accessTypes', 0, 'value'])
                        add_field(self, EV, 'fileSize',                          ['file', 'size'])
                        add_field(self, EV, 'fileDigest',                        ['file', 'digest'])
                        add_field(self, EV, 'fileDigestAlgorithm',               ['file', 'digestAlgorithm'])

                        self.data = self.data[:-2]
                        self.data += '}, '                                  # end review

                        # DOWNLOAD FILE FROM PURE
                        file_name = EV['file']['fileName']
                        file_url  = EV['file']['fileURL']
                        response = self.requests.get(file_url, auth=HTTPBasicAuth(pure_username, pure_password))
                        print(f'\n--- Download file from Pure. {response}\nFile name:\t{file_name}')

                        # SAVE FILE
                        if response.status_code < 300:
                            open(str(self.dirpath) + '/reports/temporary_files/' + file_name, 'wb').write(response.content)
                            self.record_files.append(file_name)
            if cnt > 0:
                self.data = self.data[:-2]       
                self.data += '], '


        # --- personAssociations ---
        if 'personAssociations' in item:
            self.data += '"contributors": ['
            for i in item['personAssociations']:
                self.data += '{'
                
                if 'name' in i:
                    if 'firstName' in i['name'] and 'lastName' in i['name']:
                        full_name = i['name']['lastName'] + ', '
                        full_name += i['name']['firstName']
                        self.data += f'"name": "{full_name}", '
                    else:   
                        self.data += '"name": "Name not specified", '
                elif 'authorCollaboratorName' in i:
                    self.data += '"name": "See authorCollaboratorName", '
                else:   
                    self.data += '"name": "Name not specified", '

                add_field(self, i, 'authorCollaboratorName',         ['authorCollaboration', 'names', 0, 'value'])    
                add_field(self, i, 'personRole',                     ['personRoles', 0, 'value'])    
                add_field(self, i, 'organisationalUnit',             ['organisationalUnits', 0, 'names', 0, 'value'])
                add_field(self, i, 'link',                           ['person', 'link', 'href'])
                add_field(self, i, 'link',                           ['externalPerson', 'link', 'href'])
                add_field(self, i, 'type_p',                         ['externalPerson', 'types', 0, 'value'])
                self.data = self.data[:-2]                          # removes last 2 characters
                self.data += '}, '

            self.data = self.data[:-2]       
            self.data += '], '

        # --- organisationalUnits ---
        if 'organisationalUnits' in item:
            self.data += '"organisationalUnits": ['
            for i in item['organisationalUnits']:
                self.data += '{'
                add_field(self, i, 'name',                           ['names', 0, 'value'])
                add_field(self, i, 'link',                           ['link', 'href'])
                self.data = self.data[:-2]
                self.data += '}, '
                
            self.data = self.data[:-2]
            self.data += '], '

        self.data = self.data[:-2]
        self.data += '}'          # End data

        return post_to_rdm(self)

    except:
        print('\n- Error in create_invenio_data method -\n')


#   ---         ---         ---
def add_field(self, item, inv_field, path):

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
                resp_json = self.json.load(open(self.dirpath + '/iso6393.json', 'r'))
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
        self.data += '"' + inv_field + '": "' + element + '", '
        return

    except:
        print('\n- Error in add_field method -\n')

#   ---         ---         ---
def post_to_rdm(self):

    try:
        self.metadata_success = None
        self.file_success =     None
        self.time.sleep(push_dist_sec)                        # ~ 5000 records per hour

        data_utf8 = self.data.encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('prettyprint', '1'),
        )
        # POST REQUEST metadata
        response = self.requests.post('https://localhost:5000/api/records/', headers=headers, params=params, data=data_utf8, verify=False)

        # RESPONSE CHECK
        print('Metadata post: ', response)                

        # adds metadata http response codes into array
        if response.status_code in self.cnt_resp:       self.cnt_resp[response.status_code] += 1
        else:                                           self.cnt_resp[response.status_code] =  1

        uuid = self.item["uuid"]
        current_time = self.datetime.now().strftime("%H:%M:%S")

        report = f'{current_time} - {str(response)} - {uuid} - {self.item["title"]}\n'

        if response.status_code >= 300:

            self.cnt_errors += 1
            print(response.content)

            # metadata transmission success flag
            self.metadata_success = False

            # post json error_jsons
            if response.status_code != 429:
                filename = f'{self.dirpath}/reports/temporary_files/error_jsons/{uuid}.json'
                open(filename, "w").write(str(self.data))
            
            # error description from invenioRDM
            report += str(response.content) + '\n'

            # append records to re-transfer
            if self.exec_type != 'by_id':
                open(self.dirpath + "/data/to_transfer.txt", "a").write(uuid + "\n")

        filename = self.dirpath + "/reports/" + str(self.date.today()) + "_rdm_push_records.log"
        open(filename, "a").write(report)

        if response.status_code == 429:
            print('Waiting 15 min')
            self.time.sleep(wait_429)                     # 429 too many requests, wait 15 min

        # -- Successful transmition --
        if response.status_code < 300:

            # metadata transmission success flag
            self.metadata_success = True

            # - Upload record FILES to RDM -
            if len(self.record_files) > 0:
                for file_name in self.record_files:
                    file_resp_code = rdm_put_file(self, file_name)

                # adds file transfer http response codes into array
                if file_resp_code not in self.cnt_resp:
                    self.cnt_resp[file_resp_code] = 0

                self.cnt_resp[file_resp_code] += 1
                
            # in case there no file to transfer, gets recid
            else:
                get_record_recid(self)            

            # add uuid to all_rdm_records
            uuid_recid_line = f'{uuid} {self.recid}\n'
            open(self.dirpath + "/reports/all_rdm_records.log", "a").write(uuid_recid_line)


        # FINALL SUCCESS CHECK
        # print(f'Success check -> metadata: {self.metadata_success} - file: {self.file_success}')
        if(self.metadata_success == False or self.file_success == False):
            return False
        else:
            delete_errorJson_and_toTransfer(self, uuid)
            return True

    except:
        print('\n- Error in post_to_rdm method -\n')



#   ---         ---         ---
def delete_errorJson_and_toTransfer(self, uuid):

    # if uuid in to_transfer then removes it
    file_name = self.dirpath + "/data/to_transfer.txt"
    with open(file_name, "r") as f:
        lines = f.readlines()
    with open(file_name, "w") as f:
        for line in lines:
            if line.strip("\n") != uuid:
                f.write(line)

    # Get file names from folder
    isfile = self.os.path.isfile
    join = self.os.path.join
    folder = '/reports/temporary_files/error_jsons/'
    onlyfiles = [f for f in self.os.listdir(self.dirpath + folder) if isfile(join(self.dirpath + folder, f))]

    for file_name in onlyfiles:
        file_uuid = file_name.split('.')[0]
        
        if file_uuid == uuid:
            self.os.remove(self.dirpath + folder + file_name)
            print(f'Correct transmission -> The file /reports/temporary_files/error_jsons/{file_name} has been deleted.\n')
    
