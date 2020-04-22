from setup                              import dirpath, versioning_running, rdm_api_url_records, push_dist_sec, \
                                               applied_restrictions_possible_values, pure_rest_api_url
from functions.rdm_general_functions    import rdm_get_metadata, rdm_post_metadata, \
                                               rdm_get_recid, get_rdm_userid_from_list_by_externalid, too_many_rdm_requests_check
from functions.general_functions        import add_to_full_report
from functions.pure_general_functions   import pure_get_uuid_metadata, pure_get_metadata
from functions.get_put_file             import rdm_add_file, get_file_from_pure
from functions.rdm_groups               import rdm_create_group
from functions.rdm_versioning           import rdm_versioning
from functions.rdm_database             import RdmDatabase
from datetime                           import date, datetime
import json
import time

class RdmAddRecord:

    def rdm_push_record_by_uuid(self, global_counters, uuid):
        
        # Gets from Pure the metadata of the given uuid
        item = pure_get_uuid_metadata(uuid)
        if not item:
            return False

        return self.create_invenio_data(global_counters, item)


    def create_invenio_data(self, global_counters, item):
        """ Reads pure metadata and creates the json that will be pushed to RDM """

        self.global_counters = global_counters
        self.global_counters['count_total'] += 1      

        self.record_files = []
        self.uuid = item['uuid']
        self.item = item
        self.data = {}

        # Versioning
        if versioning_running:

            # Get metadata version
            response = rdm_versioning(self.uuid)

            metadata_version        = response[0]
            older_metadata_versions = response[1]

            if response:
                self.data['metadataVersion']       = metadata_version
                self.data['metadataOlderVersions'] = older_metadata_versions

                self.add_field(item, 'metadataModifBy',   ['info', 'modifiedBy'])
                self.add_field(item, 'metadataModifDate', ['info', 'modifiedDate'])

        # 'Owners' data not present in pure metadata
        # It is present instead when getting the record's metadata from RDM (for a record update for instance)
        if 'owners' in item:
            self.data['owners'] = item['owners']
            if 1 not in self.data['owners']:
                # One is the user id of the master user
                self.data['owners'].append(1)
            report = f"\tOwners:               - {self.data['owners']}"
            add_to_full_report(report)
        else:
            # One is the user id of the master user
            self.data['owners'] = [1]

        # TO REVIEW - TO REVIEW
        # self.data['owners'].append(3)
        self.data['appliedRestrictions'] = ['owners', 'ip_single']
        self.data['_access'] = {'metadata_restricted': False, 'files_restricted': False}        # Default value for _access field
        # TO REVIEW - TO REVIEW

                            # RDM field name                # PURE json path
        self.add_field(item, 'title',                       ['title'])
        self.add_field(item, 'access_right',                ['openAccessPermissions', 0, 'value'])
        self.add_field(item, 'uuid',                        ['uuid'])
        self.add_field(item, 'pureId',                      ['pureId'])
        self.add_field(item, 'publicationDate',             ['publicationStatuses', 0, 'publicationDate', 'year'])
        self.add_field(item, 'createdDate',                 ['info', 'createdDate'])
        self.add_field(item, 'pages',                       ['info','pages'])   
        self.add_field(item, 'volume',                      ['info','volume'])
        self.add_field(item, 'journalTitle',                ['info', 'journalAssociation', 'title', 'value'])
        self.add_field(item, 'journalNumber',               ['info', 'journalNumber'])
        self.add_field(item, 'pureId',                      ['pureId'])
        self.add_field(item, 'type_p',                      ['types', 0, 'value'])    
        self.add_field(item, 'category',                    ['categories', 0, 'value'])  
        self.add_field(item, 'peerReview',                  ['peerReview'])    
        self.add_field(item, 'publicationStatus',           ['publicationStatuses', 0, 'publicationStatuses', 0, 'value'])
        self.add_field(item, 'language',                    ['languages', 0, 'value'])
        self.add_field(item, 'totalNumberOfAuthors',        ['totalNumberOfAuthors'])
        self.add_field(item, 'workflow',                    ['workflows', 0, 'value'])
        self.add_field(item, 'confidential',                ['confidential'])
        self.add_field(item, 'publisherName',               ['publisher', 'names', 0, 'value'])
        self.add_field(item, 'abstract',                    ['abstracts', 0, 'value'])
        self.add_field(item, 'managingOrganisationalUnit_name',       ['managingOrganisationalUnit', 'names', 0, 'value'])
        self.add_field(item, 'managingOrganisationalUnit_uuid',       ['managingOrganisationalUnit', 'uuid'])
        self.add_field(item, 'managingOrganisationalUnit_externalId', ['managingOrganisationalUnit', 'externalId'])
    
        # --- Electronic Versions ---
        self.data['versionFiles'] = []
        self.rdm_file_review = []

        if 'electronicVersions' in item or 'additionalFiles' in item:
            # Checks if the file has been already uploaded to RDM and if it has been internally reviewed
            self.get_rdm_file_review()

        if 'electronicVersions' in item:
            for i in item['electronicVersions']:
                self.get_files_data(i)

        # --- Additional Files ---
        if 'additionalFiles' in item:
            for i in item['additionalFiles']:
                self.get_files_data(i)

        # --- personAssociations ---
        if 'personAssociations' in item:
            self.data['contributors'] = []

            # Used to get, when available, the contributor's RDM userid
            file_data = open(f"{dirpath}/data/user_ids_match.txt").readlines()

            for i in item['personAssociations']:

                sub_data = {}
                # Name
                first_name = self.get_value(i, ['name', 'firstName'])
                last_name  = self.get_value(i, ['name', 'lastName'])

                if first_name and last_name:
                    sub_data['name'] = f'{last_name}, {first_name}'
                elif last_name and not first_name:
                    sub_data['name'] = f'{last_name}, (first name not specified)'
                elif first_name and not last_name:
                    sub_data['name'] = f'(last name not specified), {first_name}'

                # Standard fields
                sub_data = self.add_to_var(sub_data, i, 'externalId',               ['person', 'externalId'])     # 'externalPerson' never have 'externalId'
                sub_data = self.add_to_var(sub_data, i, 'uuid',                     ['person', 'uuid'])
                sub_data = self.add_to_var(sub_data, i, 'authorCollaboratorName',   ['authorCollaboration', 'names', 0, 'value'])   
                sub_data = self.add_to_var(sub_data, i, 'personRole',               ['personRoles', 0, 'value'])    
                sub_data = self.add_to_var(sub_data, i, 'organisationalUnit',       ['organisationalUnits', 0, 'names', 0, 'value']) # UnitS...
                sub_data = self.add_to_var(sub_data, i, 'type_p',                   ['externalPerson', 'types', 0, 'value'])
                sub_data = self.add_to_var(sub_data, i, 'uuid',                     ['externalPerson', 'uuid'])
                
                # Checks if the record owner is available in user_ids_match.txt
                person_external_id = self.get_value(i, ['person', 'externalId'])
                owner = get_rdm_userid_from_list_by_externalid(person_external_id, file_data)

                if owner and owner not in self.data['owners']: 
                    self.data['owners'].append(int(owner))

                # Get Orcid
                if 'uuid' in sub_data:
                    orcid = self.get_orcid(sub_data['uuid'], sub_data['name'])
                    if orcid:
                        sub_data['orcid'] = orcid

                self.data['contributors'].append(sub_data)

        # --- organisationalUnits ---
        if 'organisationalUnits' in item:
            self.data['organisationalUnits'] = []
            self.data['groupRestrictions']   = []

            for i in item['organisationalUnits']:
                sub_data = {}

                organisational_unit_name       = self.get_value(i, ['names', 0, 'value'])
                organisational_unit_uuid       = self.get_value(i, ['uuid'])
                organisational_unit_externalId = self.get_value(i, ['externalId'])

                sub_data['name']        = organisational_unit_name
                sub_data['uuid']        = organisational_unit_uuid
                sub_data['externalId']  = organisational_unit_externalId

                self.data['organisationalUnits'].append(sub_data)

                # Adding organisational unit as group owner
                self.data['groupRestrictions'].append(organisational_unit_externalId)

                # Create group
                rdm_create_group(organisational_unit_externalId, organisational_unit_name)

        # --- Abstract ---  
        if 'abstracts' in item:
            self.count_abstracts += 1

        self.applied_restrictions_check()

        self.data = json.dumps(self.data)
        open(f'{dirpath}/data/temporary_files/lash_push.json', "w").write(self.data)

        # Post request to RDM
        return self.post_to_rdm()



    #   ---         ---         ---
    def applied_restrictions_check(self):
        if not 'appliedRestrictions' in self.data:
            return False

        for i in self.data['appliedRestrictions']:
            if i not in applied_restrictions_possible_values:
                report = f"Warning: the value '{i}' is not amont the accepted restrictions\n"
                add_to_full_report(report)
        return True

    #   ---         ---         ---
    def add_field(self, item: list, rdm_field: str, path: list):
        """ Adds the field to the data json """
        value = self.get_value(item, path)

        if rdm_field == 'language':
            value = self.language_conversion(value)
        elif rdm_field == 'access_right':
            value = self.accessright_conversion(value)

        if value:
            self.data[rdm_field] = value
        return


    #   ---         ---         ---
    def accessright_conversion(self, pure_value: str):
        
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
            add_to_full_report('\n--- new access_right ---> not in accessright_pure_to_rdmk array\n\n')
            return False


    #   ---         ---         ---
    def language_conversion(self, pure_language: str):
        if pure_language == 'Undefined/Unknown':
            return False
        
        file_name = f'{dirpath}/data/iso6393.json'
        resp_json = json.load(open(file_name, 'r'))
        for i in resp_json:
            if i['name'] == pure_language:
                return i['iso6393']
            else:
                # in case there is no match (e.g. spelling mistake in Pure) ignore field
                return False


    #   ---         ---         ---
    def get_value(self, item, path: list):
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
    def get_rdm_file_review(self):
        """ When a record is updated in Pure, there will be a check if the new file from Pure is the same as the old file in RDM.
        To do so it makes a comparison on the file size.
        If the size is not the same, then it will be uploaded to RDM and a new internal review will be required. """

        # --- Get file size and internalReview from RDM ---
        sort  = 'sort=mostrecent'
        size  = 'size=100'
        page  = 'page=1'
        query = f'q="{self.uuid}"'

        url = f'{rdm_api_url_records}api/records/?{sort}&{query}&{size}&{page}'
        response = rdm_get_metadata(url)

        if response.status_code >= 300:
            report = f'\nget_rdm_file_size - {self.uuid} - {response}'
            add_to_full_report(report)
            add_to_full_report(response.content)

            return False

        open(f'{dirpath}/data/temporary_files/rdm_get_recid.json', "wb").write(response.content)

        # Load response
        resp_json = json.loads(response.content)

        total_recids = resp_json['hits']['total']
        if total_recids == 0:
            return False

        record = resp_json['hits']['hits'][0]['metadata']  # [0] because they are ordered, therefore it is the most recent

        if 'versionFiles' in record:
            for file in record['versionFiles']:
                file_size   = file['size']
                file_name   = file['name']
                file_review = file['internalReview']

                self.rdm_file_review.append({'size': file_size, 'review': file_review, 'name': file_name})

                # add_to_full_report(f'\tFile/s size   - {response} - Number files:  {total_recids}    - Size: {file_size} - Review: {file_review}')
        return




    def get_files_data(self, i: dict):
        """ Gets metadata information from electronicVersions and additionalFiles files.
            It also downloads the relative files. The Metadata without file will be ignored """

        if 'file' not in i:
            return False
        elif 'fileURL' not in i['file'] or 'fileName' not in i['file']:
            return False

        internal_review = False     # Default value

        pure_size   = self.get_value(i, ['file', 'size'])
        pure_name   = self.get_value(i, ['file', 'fileName'])

        self.pure_rdm_file_match = []        # [file_match, internalReview]

        # Checks if pure_size and pure_name are the same as any of the files in RDM with the same uuid
        for rdm_file in self.rdm_file_review:

            rdm_size   = str(rdm_file['size'])
            rdm_review = rdm_file['review']

            if pure_size == rdm_size and pure_name == rdm_file['name']:
                self.pure_rdm_file_match.append(True)            # Do the old and new file match?
                self.pure_rdm_file_match.append(rdm_review)      # Was the old file reviewed?
                internal_review = rdm_review       # The new uploaded file will have the same review value as in RDM
                break

        sub_data = {}

        sub_data['internalReview'] = internal_review

        sub_data = self.add_to_var(sub_data, i, 'name',            ['file', 'fileName'])
        sub_data = self.add_to_var(sub_data, i, 'size',            ['file', 'size'])
        sub_data = self.add_to_var(sub_data, i, 'mimeType',        ['file', 'mimeType'])
        sub_data = self.add_to_var(sub_data, i, 'digest',          ['file', 'digest'])
        sub_data = self.add_to_var(sub_data, i, 'digestAlgorithm', ['file', 'digestAlgorithm'])
        sub_data = self.add_to_var(sub_data, i, 'createdBy',       ['creator'])
        sub_data = self.add_to_var(sub_data, i, 'createdDate',     ['created'])
        sub_data = self.add_to_var(sub_data, i, 'versionType',     ['versionTypes', 0, 'value'])
        sub_data = self.add_to_var(sub_data, i, 'licenseType',     ['licenseTypes', 0, 'value'])
        sub_data = self.add_to_var(sub_data, i, 'accessType',      ['accessTypes', 0, 'value'])

        # Append to sub_data to .data
        self.data['versionFiles'].append(sub_data)

        # Download file from Pure
        get_file_from_pure(self, i)
        return
    

    #   ---         ---         ---
    def add_to_var(self, sub_data: dict, item: list, rdm_field: str, path: list):
        """ Adds the field to sub_data """
        value = self.get_value(item, path)

        if rdm_field == 'accessType':
            value = self.accessright_conversion(value)

        if value:
            sub_data[rdm_field] = value
        return sub_data


    #   ---         ---         ---
    def get_orcid(self, person_uuid: str, name: str):

        url = f'{pure_rest_api_url}/persons/{person_uuid}'
        
        response = pure_get_metadata(url)
        message = f'\tPure get orcid        - {response} - '

        if response.status_code == 404:
            message += f'External person     - {person_uuid} - {name}'
            add_to_full_report(message)
            return False

        elif response.status_code >= 300:
            message += f'Error: {response.content}'
            add_to_full_report(message)
            return False

        resp_json = json.loads(response.content)


        if 'orcid' in resp_json:
            self.global_counters['count_orcids'] += 1
            orcid = resp_json['orcid']

            message += f'{orcid} - {name}'
            add_to_full_report(message)

            return orcid

        message += f'Orcid not found     - {name}'
        add_to_full_report(message)
        return False


    #   ---         ---         ---
    def post_to_rdm(self):

        self.metadata_success = None
        self.file_success     = None

        # RDM accepts 5000 records per hour (one record every ~ 1.4 sec.)
        time.sleep(push_dist_sec)                        
        
        # POST REQUEST metadata
        url = f'{rdm_api_url_records}api/records/'
        response = rdm_post_metadata(url, self.data)

        # Count http responses 
        # if response.status_code not in self.count_http_responses:
        if response.status_code not in self.global_counters['count_http_responses']:
            self.global_counters['count_http_responses'][response.status_code] = 0
        self.global_counters['count_http_responses'][response.status_code] += 1

        uuid = self.item['uuid']
        report = f"\tRDM post metadata     - {response} - Uuid:                 {uuid}"
        add_to_full_report(report)
        
        current_time = datetime.now().strftime("%H:%M:%S")
        report = f'{current_time} - metadata_to_rdm - {str(response)} - {uuid} - {self.item["title"]}\n'

        # RESPONSE CHECK
        if response.status_code >= 300:

            self.global_counters.count_errors_push_metadata += 1

            # metadata transmission success flag
            self.metadata_success = False
            
            # error description from invenioRDM
            report += f'{response.content}\n'
            add_to_full_report(response.content)

            # Add record to to_transfer.txt to be re pushed afterwards
            open(f'{dirpath}/data/to_transfer.txt', "a").write(f'{uuid}\n')

        file_name = f'{dirpath}/reports/{date.today()}_records.log'
        open(file_name, "a").write(report)

        # If the status_code is 429 (too many requests) then it will wait for some minutes
        too_many_rdm_requests_check(response)

        
        # In case of SUCCESSFUL TRANSMISSION
        if response.status_code < 300:
            self.global_counters['count_successful_push_metadata'] += 1

            # metadata transmission success flag
            self.metadata_success = True

            # After pushing the record's metadata to RDM needs about a second to be able to get its recid from RDM
            time.sleep(1)

            # Gets recid from RDM
            recid = rdm_get_recid(uuid)
            if not recid:
                return False

            # - Upload record FILES to RDM -
            for file_name in self.record_files:
                response = rdm_add_file(self, file_name, recid, uuid)
                if response.status_code >= 300:
                    self.global_counters['count_errors_put_file'] += 1
                else:
                    self.global_counters['count_successful_push_file'] += 1
                        
            if recid:
                # add record to all_rdm_records
                uuid_recid_line = f'{uuid} {recid}\n'
                open(f'{dirpath}/data/all_rdm_records.txt', "a").write(uuid_recid_line)


        # FINALL SUCCESS CHECK
        if(self.metadata_success == False or self.file_success == False):
            return False
        else:
            # # Push RDM record link to Pure                                # TODO
            # self.api_url
            # self.landing_page_url

            # if uuid in to_transfer then removes it
            file_name = f'{dirpath}/data/to_transfer.txt'
            with open(file_name, "r") as f:
                lines = f.readlines()
            with open(file_name, "w") as f:
                for line in lines:
                    if line.strip("\n") != uuid:
                        f.write(line)
        return True