import requests
import json
import time
import os
from datetime import datetime, date
from setup import pure_api_key, pure_rest_api_url, pure_username, pure_password, dirpath
from requests.auth import HTTPBasicAuth

class PureToRdm:
    
    def __init__(self):
        # directory path
        self.dirpath = dirpath
        self.cnt_resp = {}


    #   ---         ---         ---
    def get_pure_by_page(self, pag_begin, pag_end, pag_size):

        try:
            self.exec_type = 'by_page'

            for pag in range(pag_begin, pag_end):

                report_text = f'\nPag {str(pag)} - pag_size {str(pag_size)}\n'
                # add page to report file
                report_file = self.dirpath + "/reports/full_reports/" + str(date.today()) + "_report.log"     
                open(report_file, "a").write(report_text)                       # 'a' -> append

                headers = {
                    'Accept': 'application/json',
                    'api-key': pure_api_key,
                }
                params = (
                    ('page', pag),
                    ('pageSize', pag_size),
                    ('apiKey', pure_api_key),
                )
                # PURE get request
                response = requests.get(pure_rest_api_url + 'research-outputs', headers=headers, params=params)
                open(self.dirpath + "/reports/resp_pure.json", 'wb').write(response.content)
                resp_json = json.loads(response.content)

                # resp_json = open(self.dirpath + '/reports/resp_pure.json', 'r')             # -- TEMPORARY -- 
                # resp_json = json.load(resp_json)                                            # -- TEMPORARY -- 

                #       ---         ---         ---
                for self.item in resp_json['items']:
                    self.create_invenio_data()          # Creates data to push to InvenioRDM
                #       ---         ---         ---
                    
                # view total number of http respone codes in report.log
                report_text = 'HTTP response codes:\n'
                for key in self.cnt_resp:
                    report_text += str(key) + ": " + str(self.cnt_resp[key]) + "\n"
                open(report_file, "a").write(report_text)

                # add http reponse codes to d_rdm_push_report.log
                report_file = self.dirpath + "/reports/d_rdm_push_report.log"
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                report_text = f'\n{str(date.today())} {current_time}, pag {pag}, size {pag_size}, codes: \t'
                # report_text = '\n' + str(current_time) + ' - pag ' + str(pag) + ' - pag_size ' + str(pag_size) + ' - http codes::\n'

                for key in self.cnt_resp:
                    report_text += str(key) + ": " + str(self.cnt_resp[key]) + ', \t'
                open(report_file, "a").write(report_text)

                self.cnt_resp = {}

            print('\n-- -- Finito -- --\n')
        except:
            print('\n- Error in get_pure_by_page method -\n')

    #   ---         ---         ---
    def get_pure_by_id(self, uuid):
        
        try:
            self.exec_type = 'by_id'
            
            headers = {
                'Accept': 'application/json',
                'api-key': pure_api_key,
            }
            params = (
                ('apiKey', pure_api_key),
            )
            response = requests.get(pure_rest_api_url + 'research-outputs/' + uuid, headers=headers, params=params)
            print('Pure response: ', response)
            if response.status_code >= 300:
                print(response.content)
                raise Exception

            open(self.dirpath + "/reports/pure_resp.json", 'wb').write(response.content)
            self.item = json.loads(response.content)
            
            # Creates data to push to InvenioRDM
            return self.create_invenio_data()

        except:
            print('\n- Error in get_pure_by_id method -\n')


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
            self.add_field(item, 'title',                             ['title'])
            self.add_field(item, 'publicationDatePure',               ['publicationStatuses', 0, 'publicationDate', 'year'])
            self.add_field(item, 'createdDatePure',                   ['info', 'createdDate'])
            self.add_field(item, 'modifiedDatePure',                  ['info', 'modifiedDate'])
            self.add_field(item, 'pureId',                            ['pureId'])
            self.add_field(item, 'uuid',                              ['uuid'])                                                                   
            self.add_field(item, 'type_p',                            ['types', 0, 'value'])                                                     
            self.add_field(item, 'category',                          ['categories', 0, 'value'])                                              
            self.add_field(item, 'peerReview',                        ['peerReview'])                                                         
            self.add_field(item, 'publicationStatus',                 ['publicationStatuses', 0, 'publicationStatuses', 0, 'value'])
            self.add_field(item, 'language',                          ['languages', 0, 'value'])
            self.add_field(item, 'totalNumberOfAuthors',              ['totalNumberOfAuthors'])
            self.add_field(item, 'managingOrganisationalUnit',        ['managingOrganisationalUnit', 'names', 0, 'value'])
            self.add_field(item, 'workflow',                          ['workflows', 0, 'value'])
            self.add_field(item, 'confidential',                      ['confidential'])
            self.add_field(item, 'publisherName',                     ['publisher', 'names', 0, 'value'])
            self.add_field(item, 'access_right',                      ['openAccessPermissions', 0, 'value'])
            self.add_field(item, 'pages',                             ['info','pages'])                                                     
            self.add_field(item, 'volume',                            ['info','volume'])                                                         
            self.add_field(item, 'versionType',                       ['electronicVersions', 0, 'versionType', 'value'])                     
            self.add_field(item, 'licenseType',                       ['electronicVersions', 0, 'licenseType', 'value'])
            self.add_field(item, 'journalTitle',                      ['info', 'journalAssociation', 'title', 'value'])
            self.add_field(item, 'journalNumber',                     ['info', 'journalNumber'])
            # versionType:          e.g. Final published version, Accepted author manuscript (rare)
            # metadataVersion:      ???
            # versionFiles:         ???

            # # Test invenio RDM fields
            # self.data += '"description": "TEST DESCRIPTION", '
            # self.data += '"additional_descriptions": [{"description": "this is my additional description"}], '
            # self.data += '"additional_titles": [{"title": "this is my additional title"}], '
            
            # TEST TITLE2
            self.data += '"title2": ['
            self.data += '{'
            self.add_field(item, 'value',                               ['title'])
            self.add_field(item, 'version',                             ['title'])
            self.add_field(item, 'createdBy',                           ['title'])
            self.add_field(item, 'createdDate',                         ['title'])
            self.data = self.data[:-2]
            self.data += '}, '
            self.data = self.data[:-2]       
            self.data += '], '

            if 'electronicVersions' in item:
                cnt = 0
                for EV in item['electronicVersions']:
                    if 'file' in EV:
                        if 'fileURL' in EV['file'] and 'fileName' in EV['file']:
                            
                            if cnt == 0:
                                self.data += '"versionFiles": ['
                            cnt += 1

                            file_name = EV['file']['fileName']
                            file_url  = EV['file']['fileURL']

                            self.data += '{'                                    # TO REVIEW !!! 
                            self.data += f'"fileName": "{file_name}", '
                            self.data += f'"fileModifBy": "Markus??", '
                            self.data += f'"fileVersion": "1??", '
                            self.data = self.data[:-2]
                            self.data += '}, '                                  # end review

                            # DOWNLOAD FILE FROM PURE
                            response = requests.get(file_url, auth=HTTPBasicAuth(pure_username, pure_password))
                            print(f'\n--- Download file from Pure. {response}\nFile name:\t{file_name}')

                            # SAVE FILE
                            if response.status_code < 300:
                                open(str(self.dirpath) + '/tmp_files/' + file_name, 'wb').write(response.content)
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

                    self.add_field(i, 'authorCollaboratorName',         ['authorCollaboration', 'names', 0, 'value'])    
                    self.add_field(i, 'personRole',                     ['personRoles', 0, 'value'])    
                    self.add_field(i, 'organisationalUnit',             ['organisationalUnits', 0, 'names', 0, 'value'])
                    self.add_field(i, 'link',                           ['person', 'link', 'href'])
                    self.add_field(i, 'link',                           ['externalPerson', 'link', 'href'])
                    self.add_field(i, 'type_p',                         ['externalPerson', 'types', 0, 'value'])
                    self.data = self.data[:-2]                          # removes last 2 characters
                    self.data += '}, '

                self.data = self.data[:-2]       
                self.data += '], '

            # --- organisationalUnits ---
            if 'organisationalUnits' in item:
                self.data += '"organisationalUnits": ['
                for i in item['organisationalUnits']:
                    self.data += '{'
                    self.add_field(i, 'name',                           ['names', 0, 'value'])
                    self.add_field(i, 'link',                           ['link', 'href'])
                    self.data = self.data[:-2]
                    self.data += '}, '
                    
                self.data = self.data[:-2]
                self.data += '], '

            self.data = self.data[:-2]
            self.data += '}'          # End data

            # Write last_push.log
            filename = self.dirpath + "/reports/last_push.json"
            open(filename, "w+").write(self.data)

            return self.post_to_invenio()

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
                    resp_json = json.load(open(self.dirpath + '/iso6393.json', 'r'))
                    for i in resp_json:
                        if i['name'] == element:
                            element = i['iso6393']

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
    def post_to_invenio(self):

        try:
            self.metadata_success = None
            self.file_success =     None
            time.sleep(1)                                 # ~ 5000 records per hour

            data_utf8 = self.data.encode('utf-8')
            headers = {
                'Content-Type': 'application/json',
            }
            params = (
                ('prettyprint', '1'),
            )
            # POST REQUEST
            response = requests.post('https://localhost:5000/api/records/', headers=headers, params=params, data=data_utf8, verify=False)

            # RESPONSE CHECK
            print('Metadata post: ', response)                

            # adds all response http codes into array
            if response.status_code in self.cnt_resp:       self.cnt_resp[response.status_code] += 1
            else:                                           self.cnt_resp[response.status_code] =  1

            uuid = self.item["uuid"]
            current_time = datetime.now().strftime("%H:%M:%S")

            report = f'{current_time} - {str(response)} - {uuid} - {self.item["title"]}\n'

            if response.status_code >= 300:

                print(response.content)

                # metadata transmission success flag
                self.metadata_success = False

                # post json error_jsons
                filename = self.dirpath + "/reports/error_jsons/" + uuid + ".json"
                open(filename, "w").write(str(self.data))
                
                # error description from invenioRDM
                report += str(response.content) + '\n'

                # append records to re-transfer
                if self.exec_type != 'by_id':
                    open(self.dirpath + "/reports/to_transfer.log", "a").write(uuid + "\n")

            filename = self.dirpath + "/reports/full_reports/" + str(date.today()) + "_report.log"
            open(filename, "a").write(report)

            if response.status_code == 429:
                print('Waiting 15 min')
                time.sleep(900)                     # 429 too many requests, wait 15 min

            # Successful transmition
            if response.status_code < 300:

                # metadata transmission success flag
                self.metadata_success = True

                # - Upload record FILES to RDM -
                if len(self.record_files) > 0:
                    for file_name in self.record_files:
                        self.put_file_to_rdm(file_name)


            # FINALL SUCCESS CHECK
            # print(f'Success check -> metadata: {self.metadata_success} - file: {self.file_success}')

            if(self.metadata_success == False or self.file_success == False):
                
                return False
            else:
                self.delete_errorJson_and_toTransfer(uuid)
                return True

        except:
            print('\n- Error in post_to_invenio method -\n')



    #   ---         ---         ---
    def delete_errorJson_and_toTransfer(self, uuid):

        # if uuid in to_transfer then removes it
        file_name = self.dirpath + "/reports/to_transfer.log"
        with open(file_name, "r") as f:
            lines = f.readlines()
        with open(file_name, "w") as f:
            for line in lines:
                if line.strip("\n") != uuid:
                    f.write(line)

        # Get file names from folder
        isfile = os.path.isfile
        join = os.path.join
        folder = '/reports/error_jsons/'
        onlyfiles = [f for f in os.listdir(self.dirpath + folder) if isfile(join(self.dirpath + folder, f))]

        for file_name in onlyfiles:
            file_uuid = file_name.split('.')[0]
            
            if file_uuid == uuid:
                os.remove(self.dirpath + folder + file_name)
                print(f'\nRecord {uuid} correctly transmitted.\n/reports/error_jsons/{file_name} has been deleted.')
        

    #   ---         ---         ---
    def put_file_to_rdm(self, file_name):
        try:
            file_path = self.dirpath + '/tmp_files/'
            cnt = 0
            
            # GET from RDM recid of last added record
            while True:
                cnt += 1
                time.sleep(cnt * 2)
                response = requests.get(
                    'https://localhost:5000/api/records/?sort=mostrecent&size=1&page=1', 
                    params=(('prettyprint', '1'),), 
                    verify=False
                    )
                resp_json = json.loads(response.content)

                for i in resp_json['hits']['hits']:
                    recid       = i['metadata']['recid']
                    record_uuid = i['metadata']['uuid']
                    print(f'Adding FILE number {cnt} to recid {recid}')
                
                if self.uuid == record_uuid or cnt > 10:
                    break
            if cnt > 10:    print('Having troubles getting the recid of the newly added record\n')

            # - PUT FILE TO RDM -
            headers = {
                'Content-Type': 'application/octet-stream',
            }
            data = open(file_path + file_name, 'rb').read()
            response = requests.put('https://127.0.0.1:5000/api/records/' + recid + '/files/' + file_name, headers=headers, data=data, verify=False)

            # Report
            report = ''
            print(f'Transf to RDM: {response}\n')
            report += 'FileTransf ' + str(response) + ' - ' + str(recid) + '\n'

            if response.status_code >= 300:
                report += str(response.content) + '\n'

                # metadata transmission success flag
                self.file_success = False
            else:
                self.file_success = True

                # # if the upload was successful then delete file from /tmp_files
                os.remove(file_path + file_name) 

            filename = self.dirpath + "/reports/full_reports/" + str(date.today()) + "_report.log"
            open(filename, "a").write(report)


        except:
            print('\n- Error in put_file_to_rdm method -\n')
