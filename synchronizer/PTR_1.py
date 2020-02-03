import requests
import json
import time
import os
from datetime import datetime, date

class pureToInvenio:
    
    def __init__(self):
        # directory path
        self.dirpath = os.path.dirname(os.path.abspath(__file__))
        self.cnt_resp = {}


    #   ---         ---         ---
    def get_pure_by_page(self, pag_begin, pag_end, pag_size):

        self.exec_type = 'by_page'

        for pag in range(pag_begin, pag_end):

            report_text = f'\nPag {str(pag)} - pag_size {str(pag_size)}\n'
            # add page to report file
            report_file = self.dirpath + "/reports/" + str(date.today()) + "_report.log"     
            open(report_file, "a").write(report_text)                       # 'a' -> append

            headers = {
                'Accept': 'application/json',
                'api-key': 'ca2f08c5-8b33-454a-adc4-8215cfb3e088',
            }
            params = (
                ('page', pag),
                ('pageSize', pag_size),
                ('apiKey', 'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
            )
            # PURE get request
            response = requests.get('https://pure01.tugraz.at/ws/api/514/research-outputs', headers=headers, params=params)
            open(self.dirpath + "/reports/resp_pure.json", 'wb').write(response.content)
            resp_json = json.loads(response.content)

            # resp_json = open(self.dirpath + '/reports/resp_pure.json', 'r')             # -- TEMPORARY -- 
            # resp_json = json.load(resp_json)                                            # -- TEMPORARY -- 

            for self.item in resp_json['items']:
                self.create_invenio_data()          # Creates data to push to InvenioRDM
                
            # view total number of http respone codes in report.log
            report_text = ''
            for key in self.cnt_resp:
                report_text += str(key) + ": " + str(self.cnt_resp[key]) + "\n"
            open(report_file, "a").write(report_text)

            # add http reponse codes to http_resp_code.log
            report_file = self.dirpath + "/reports/http_resp_code.log"
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            report_text = f'\n{str(date.today())}{current_time}, pag {pag}, size {pag_size}, codes: \t'
            # report_text = '\n' + str(current_time) + ' - pag ' + str(pag) + ' - pag_size ' + str(pag_size) + ' - http codes::\n'

            for key in self.cnt_resp:
                report_text += str(key) + ": " + str(self.cnt_resp[key]) + ', \t'
            open(report_file, "a").write(report_text)

            self.cnt_resp = {}

        print('\n\n-- -- Finito! -- --\n\n')

    #   ---         ---         ---
    def get_pure_by_id(self, uuid):
    
        self.exec_type = 'by_id'
        
        headers = {
            'Accept': 'application/json',
            'api-key': 'ca2f08c5-8b33-454a-adc4-8215cfb3e088',
        }
        params = (
            ('apiKey', 'ca2f08c5-8b33-454a-adc4-8215cfb3e088'),
        )
        response = requests.get('https://pure01.tugraz.at/ws/api/514/research-outputs/' + uuid, headers=headers, params=params)
        open(self.dirpath + "/reports/pure_resp.json", 'wb').write(response.content)
        self.item = json.loads(response.content)
        
        # Creates data to push to InvenioRDM
        self.create_invenio_data()      


    #   ---         ---         ---
    def create_invenio_data(self):

            item = self.item
            self.data = '{'

            self.data += '"access_right": "open", '
            self.data += '"owners": [1], '
            self.data += '"_access": {"metadata_restricted": false, "files_restricted": false}, '
            
                                # invenio field name                  # PURE json path
            self.add_field(item, 'title',                             ['title'])
            self.add_field(item, 'pureId',                            ['pureId'])                                                              
            self.add_field(item, 'uuid',                              ['uuid'])                                                                   
            self.add_field(item, 'type_p',                            ['types', 0, 'value'])                                                     
            self.add_field(item, 'category',                          ['categories', 0, 'value'])                                              
            self.add_field(item, 'peerReview',                        ['peerReview'])                                                         
            self.add_field(item, 'publicationStatus',                 ['publicationStatuses', 0, 'publicationStatuses', 0, 'value'])     
            self.add_field(item, 'publicationDate',                   ['publicationStatuses', 0, 'publicationDate', 'year'])            
            self.add_field(item, 'language',                          ['languages', 0, 'value'])                                            
            self.add_field(item, 'totalNumberOfAuthors',              ['totalNumberOfAuthors'])                             
            self.add_field(item, 'managingOrganisationalUnit',        ['managingOrganisationalUnit', 'names', 0, 'value'])   
            self.add_field(item, 'workflow',                          ['workflows', 0, 'value'])                                   
            self.add_field(item, 'confidential',                      ['confidential'])                                                     
            self.add_field(item, 'publisherName',                     ['publisher', 'names', 0, 'value'])                                  
            self.add_field(item, 'accessType',                        ['openAccessPermissions', 0, 'value'])                                
            self.add_field(item, 'pages',                             ['info','pages'])                                                     
            self.add_field(item, 'volume',                            ['info','volume'])                                                         
            self.add_field(item, 'versionType',                       ['electronicVersions', 0, 'versionType', 'value'])                     
            self.add_field(item, 'licenseType',                       ['electronicVersions', 0, 'licenseType', 'value'])

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
                            self.data += f'"name": "Name not specified", '

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

            self.post_to_invenio()


    #   ---         ---         ---
    def add_field(self, item, inv_field, path):

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
            resp_json = json.load(open(self.dirpath + '/iso6393.json', 'r'))
            for i in resp_json:
                if i['name'] == element:
                    element = i['iso6393']

        self.data += '"' + inv_field + '": "' + element + '", '


    #   ---         ---         ---
    def post_to_invenio(self):

        time.sleep(1.3)                                 # ~ 5000 records per hour

        data_utf8 = self.data.encode('utf-8')
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('prettyprint', '1'),
        )
        # POST REQUEST
        response = requests.post('https://localhost:5000/api/records/', headers=headers, params=params, data=data_utf8, verify=False)

        # RESPONSE
        print(response)
        if response.status_code > 300:
            print(response.content)

        # adds all response http codes into array
        if response.status_code in self.cnt_resp:       self.cnt_resp[response.status_code] += 1
        else:                                           self.cnt_resp[response.status_code] =  1

        if response.status_code == 429:     
            time.sleep(900)                     # 429 too many requests, wait 15 min

        uuid = self.item["uuid"]

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        report = f'{current_time} - {str(response)} - {uuid} - {self.item["title"]}\n'

        file_toReTransfer = self.dirpath + "/reports/to_re_transfer.log"

        if self.exec_type == 'by_id':
            # Removes last submitted uuid.
            # If the transmission doesnt work then it will be added next
            with open(file_toReTransfer, 'r') as fin:
                data = fin.read().splitlines(True)
            with open(file_toReTransfer, 'w') as fout:
                fout.writelines(data[1:])

        if response.status_code >= 300:

            # append records to re-transfer
            open(file_toReTransfer, "a").write(uuid + "\n")
        
            # post json
            filename = self.dirpath + "/reports/error_jsons/" + uuid + ".json"
            open(filename, "w").write(str(self.data))
            
            # error description from invenioRDM
            report += str(response.content) + '\n'
            
        filename = self.dirpath + "/reports/" + str(date.today()) + "_report.log"
        open(filename, "a").write(report)

