import json
import time
from datetime                       import date
from setup                          import versioning_running, applied_restrictions_possible_values, \
                                           data_files_name, iso6393_file_name, push_dist_sec, accessright_pure_to_rdm
from source.rdm.general_functions   import get_recid, get_userid_from_list_by_externalid
from source.rdm.put_file            import rdm_add_file
from source.pure.general_functions  import get_pure_record_metadata_by_uuid, get_pure_metadata, get_pure_file
from source.rdm.versioning          import rdm_versioning 
from source.rdm.emails              import send_email
from source.rdm.groups              import RdmGroups
from source.rdm.database            import RdmDatabase
from source.rdm.requests            import Requests
from source.reports                 import Reports


class RdmAddRecord:

    def __init__(self):
        self.requests = Requests()
        self.report = Reports()
        self.groups = RdmGroups()
        

    def push_record_by_uuid(self, global_counters, uuid):
        # Gets from Pure the metadata of the given uuid
        item = get_pure_record_metadata_by_uuid(uuid)
        if not item:
            return False
        return self.create_invenio_data(global_counters, item)


    def _decorator(func):
        def _wrapper(self, global_counters, item) :
    
            self.global_counters = global_counters
            self.global_counters['total'] += 1      

            self.uuid = item['uuid']
            self.item = item
            self.data = {}
            self.record_files = []

            # Decorated function
            func(self, global_counters, item)

        return _wrapper

    @_decorator
    def create_invenio_data(self, global_counters, item):
        """ Reads pure metadata and creates the json that will be pushed to RDM """

        # Versioning
        self._check_record_version()

        # Record owners
        self._check_record_owners()

        # TO REVIEW - TO REVIEW
        # self.data['owners'].append(3)
        self.data['appliedRestrictions'] = ['owners', 'groups', 'ip_single', 'ip_range']
        self.data['_access'] = {'metadata_restricted': False, 'files_restricted': False}        # Default value for _access field
        # TO REVIEW - TO REVIEW

        # Process various general fields
        self._process_common_fields(item)
    
        # Electronic Versions
        self._process_electronic_versions()

        # Additional Files
        if 'additionalFiles' in item:
            for i in item['additionalFiles']:
                self.get_files_data(i)

        # Person Associations
        self._process_person_associations()

        # Organisational Units
        self._process_organisational_units()

        # Checks if the restriction given by pure is accepted in RDM
        self._applied_restrictions_check()

        self.data = json.dumps(self.data)

        # Post request to RDM
        return self._post_metadata()



    def _check_record_version(self):
        if versioning_running:
            # Get metadata version
            response = rdm_versioning(self.uuid)
            if response:
                self.data['metadataVersion']       = response[0]
                self.data['metadataOlderVersions'] = response[1]



    def _check_record_owners(self):
        if 'owners' in self.item:
            # Remove duplicate owners
            self.data['owners'] = list(set(self.item['owners']))        
            self.report.add(['console'], f"\tOwners:               - {self.data['owners']}")
        else:
            self.data['owners'] = [1]



    def _process_common_fields(self, item):
                            # RDM field name                # PURE json path
        self._add_field(item, 'title',                       ['title'])
        self._add_field(item, 'access_right',                ['openAccessPermissions', 0, 'value'])
        self._add_field(item, 'uuid',                        ['uuid'])
        self._add_field(item, 'pureId',                      ['pureId'])
        self._add_field(item, 'publicationDate',             ['publicationStatuses', 0, 'publicationDate', 'year'])
        self._add_field(item, 'createdDate',                 ['info', 'createdDate'])
        self._add_field(item, 'pages',                       ['info','pages'])   
        self._add_field(item, 'volume',                      ['info','volume'])
        self._add_field(item, 'journalTitle',                ['info', 'journalAssociation', 'title', 'value'])
        self._add_field(item, 'journalNumber',               ['info', 'journalNumber'])
        self._add_field(item, 'metadataModifBy',             ['info', 'modifiedBy'])
        self._add_field(item, 'metadataModifDate',           ['info', 'modifiedDate'])
        self._add_field(item, 'pureId',                      ['pureId'])
        self._add_field(item, 'recordType',                  ['types', 0, 'value'])    
        self._add_field(item, 'category',                    ['categories', 0, 'value'])  
        self._add_field(item, 'peerReview',                  ['peerReview'])    
        self._add_field(item, 'publicationStatus',           ['publicationStatuses', 0, 'publicationStatuses', 0, 'value'])
        self._add_field(item, 'language',                    ['languages', 0, 'value'])
        self._add_field(item, 'numberOfAuthors',             ['totalNumberOfAuthors'])
        self._add_field(item, 'workflow',                    ['workflows', 0, 'value'])
        self._add_field(item, 'confidential',                ['confidential'])
        self._add_field(item, 'publisherName',               ['publisher', 'names', 0, 'value'])
        self._add_field(item, 'abstract',                    ['abstracts', 0, 'value'])
        self._add_field(item, 'managingOrganisationalUnit_name',       ['managingOrganisationalUnit', 'names', 0, 'value'])
        self._add_field(item, 'managingOrganisationalUnit_uuid',       ['managingOrganisationalUnit', 'uuid'])
        self._add_field(item, 'managingOrganisationalUnit_externalId', ['managingOrganisationalUnit', 'externalId'])



    def _process_electronic_versions(self):
        self.data['versionFiles'] = []
        self.rdm_file_review = []

        if 'electronicVersions' in self.item or 'additionalFiles' in self.item:
            # Checks if the file has been already uploaded to RDM and if it has been internally reviewed
            self._get_rdm_file_review()

        if 'electronicVersions' in self.item:
            for i in self.item['electronicVersions']:
                self.get_files_data(i)
    


    def _process_person_associations(self):
        if 'personAssociations' in self.item:
            self.data['contributors'] = []

            # Used to get, when available, the contributor's RDM userid
            file_name = data_files_name['user_ids_match']
            file_data = open(file_name).readlines()

            for i in self.item['personAssociations']:

                sub_data = {}
                first_name = self._get_value(i, ['name', 'firstName'])
                last_name  = self._get_value(i, ['name', 'lastName'])

                if first_name and last_name:
                    sub_data['name'] = f'{last_name}, {first_name}'
                elif last_name and not first_name:
                    sub_data['name'] = f'{last_name}, (first name not specified)'
                elif first_name and not last_name:
                    sub_data['name'] = f'(last name not specified), {first_name}'

                # Standard fields
                sub_data = self._add_to_sub_data(sub_data, i, 'uuid',                   ['person', 'uuid'])
                sub_data = self._add_to_sub_data(sub_data, i, 'externalId',             ['person', 'externalId'])
                sub_data = self._add_to_sub_data(sub_data, i, 'authorCollaboratorName', ['authorCollaboration', 'names', 0, 'value'])   
                sub_data = self._add_to_sub_data(sub_data, i, 'personRole',             ['personRoles', 0, 'value'])    
                sub_data = self._add_to_sub_data(sub_data, i, 'organisationalUnit',     ['organisationalUnits', 0, 'names', 0, 'value'])
                sub_data = self._add_to_sub_data(sub_data, i, 'type_p',                 ['externalPerson', 'types', 0, 'value'])
                sub_data = self._add_to_sub_data(sub_data, i, 'uuid',                   ['externalPerson', 'uuid'])
                
                # Checks if the record owner is available in user_ids_match.txt
                person_external_id = self._get_value(i, ['person', 'externalId'])
                owner = get_userid_from_list_by_externalid(person_external_id, file_data)

                if owner and owner not in self.data['owners']: 
                    self.data['owners'].append(int(owner))

                # Get Orcid
                if 'uuid' in sub_data:
                    orcid = self._get_orcid(sub_data['uuid'], sub_data['name'])
                    if orcid:
                        sub_data['orcid'] = orcid

                self.data['contributors'].append(sub_data)


    def _process_organisational_units(self):
        
        if 'organisationalUnits' in self.item:
            self.data['organisationalUnits'] = []
            self.data['groupRestrictions']   = []

            for i in self.item['organisationalUnits']:
                sub_data = {}

                organisational_unit_name       = self._get_value(i, ['names', 0, 'value'])
                organisational_unit_uuid       = self._get_value(i, ['uuid'])
                organisational_unit_externalId = self._get_value(i, ['externalId'])

                sub_data['name']        = organisational_unit_name
                sub_data['uuid']        = organisational_unit_uuid
                sub_data['externalId']  = organisational_unit_externalId

                self.data['organisationalUnits'].append(sub_data)

                # Adding organisational unit as group owner
                self.data['groupRestrictions'].append(organisational_unit_externalId)

                # Create group
                self.groups.rdm_create_group(organisational_unit_externalId, organisational_unit_name)


    def _applied_restrictions_check(self):
        if not 'appliedRestrictions' in self.data:
            return False

        for i in self.data['appliedRestrictions']:
            if i not in applied_restrictions_possible_values:
                report = f"Warning: the value '{i}' is not amont the accepted restrictions\n"
                self.report.add(['console'], report)
        return True



    def _post_metadata(self):

        uuid = self.item['uuid']
        success_check = {
            'metadata': False,
            'file': False
        }
        # RDM accepts 5000 records per hour (one record every ~ 1.4 sec.)
        time.sleep(push_dist_sec)                        
        
        # POST REQUEST metadata
        response = self.requests.rdm_post_metadata(self.data)

        # Count http responses
        self._http_response_counter(response.status_code)

        self.report.add(['console'], f"\tRDM post metadata     - {response} - Uuid:                 {uuid}")

        if response.status_code >= 300:
            self.global_counters['metadata']['error'] += 1
            return False

        self.global_counters['metadata']['success'] += 1
        success_check['metadata'] = True

        # After pushing a record's metadata to RDM it takes about one second to be able to get its recid
        time.sleep(1)

        # Gets recid from RDM
        recid = get_recid(uuid)
        if not recid:
            return False

        # add record to all_rdm_records.txt
        uuid_recid_line = f'{uuid} {recid}\n'
        open(data_files_name['all_rdm_records'], "a").write(uuid_recid_line)

        # Upload record files to RDM
        for file_name in self.record_files:
        
            # Send request
            response = rdm_add_file(file_name, recid)

            if response:
                self.global_counters['file']['success'] += 1
                success_check['file'] = True

                # # Sends email to remove record from Pure
                # send_email(uuid, file_name)
            else:
                self.global_counters['file']['error'] += 1
        
        # Checks if both metadata and files were correctly transmitted
        self._metadata_and_file_submission_check(success_check)



    def _metadata_and_file_submission_check(self, success_check):

        if(success_check['metadata'] == False or success_check['file'] == False):
            # Add uuid to to_transmit.txt to be re-transmitted
            open(data_files_name['transfer_uuid_list'], "a").write(f'{self.uuid}\n')
            
            return False
        else:
            # # Push RDM record link to Pure                                # TODO
            # self.api_url      # self.landing_page_url

            # Remove uuid from to_transmit.txt
            self._remove_uuid_from_list(self, data_files_name['transfer_uuid_list'])
        return True    



    def _add_field(self, item: list, rdm_field: str, path: list):
        """ Adds the field to the data json """
        value = self._get_value(item, path)

        if rdm_field == 'language':
            value = self._language_conversion(value)
        elif rdm_field == 'access_right':
            value = self._accessright_conversion(value)

        if value:
            self.data[rdm_field] = value
        return



    def _accessright_conversion(self, pure_value: str):

        if pure_value in accessright_pure_to_rdm:
            return accessright_pure_to_rdm[pure_value]

        self.report.add(['console'], '\n--- new access_right ---> not in accessright_pure_to_rdmk array\n\n')
        return False


    def _language_conversion(self, pure_language: str):
        """ Converts from pure full language name to iso6393 (3 characters) """

        if pure_language == 'Undefined/Unknown':
            return False
        
        resp_json = json.load(open(iso6393_file_name, 'r'))
        for i in resp_json:
            if i['name'] == pure_language:
                return i['iso6393']

            # in case there is no match (e.g. spelling mistake in Pure) ignore field
            return False


    def _get_value(self, item, path: list):
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



    def _get_rdm_file_review(self):
        """ When a record is updated in Pure, there will be a check if the new file from Pure is the same as the old file in RDM.
        To do so it makes a comparison on the file size.
        If the size is not the same, then it will be uploaded to RDM and a new internal review will be required. """

        # Get from RDM file size and internalReview
        params = {'sort': 'mostrecent', 'size': '100', 'page': '1', 'q': self.uuid}
        response = self.requests.rdm_get_metadata(params)

        if response.status_code >= 300:
            self.report.add(['console'], f'\nget_rdm_file_size - {self.uuid} - {response}')
            return False

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
        return



    def get_files_data(self, i: dict):
        """ Gets metadata information from electronicVersions and additionalFiles files.
            It also downloads the relative files. The Metadata without file will be ignored """

        if 'file' not in i:
            return False
        elif 'fileURL' not in i['file'] or 'fileName' not in i['file']:
            return False

        internal_review = False     # Default value

        pure_size   = self._get_value(i, ['file', 'size'])
        pure_name   = self._get_value(i, ['file', 'fileName'])

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

        sub_data = self._add_to_sub_data(sub_data, i, 'name',            ['file', 'fileName'])
        sub_data = self._add_to_sub_data(sub_data, i, 'size',            ['file', 'size'])
        sub_data = self._add_to_sub_data(sub_data, i, 'mimeType',        ['file', 'mimeType'])
        sub_data = self._add_to_sub_data(sub_data, i, 'digest',          ['file', 'digest'])
        sub_data = self._add_to_sub_data(sub_data, i, 'digestAlgorithm', ['file', 'digestAlgorithm'])
        sub_data = self._add_to_sub_data(sub_data, i, 'createdBy',       ['creator'])
        sub_data = self._add_to_sub_data(sub_data, i, 'createdDate',     ['created'])
        sub_data = self._add_to_sub_data(sub_data, i, 'versionType',     ['versionTypes', 0, 'value'])
        sub_data = self._add_to_sub_data(sub_data, i, 'licenseType',     ['licenseTypes', 0, 'value'])
        sub_data = self._add_to_sub_data(sub_data, i, 'accessType',      ['accessTypes', 0, 'value'])

        # Append to sub_data to .data
        self.data['versionFiles'].append(sub_data)

        # Download file from Pure
        get_pure_file(self, i)
        return
    


    def _add_to_sub_data(self, sub_data: dict, item: list, rdm_field: str, path: list):
        """ Adds the field to sub_data """
        value = self._get_value(item, path)

        if rdm_field == 'accessType':
            value = self._accessright_conversion(value)

        if value:
            sub_data[rdm_field] = value
        return sub_data



    def _get_orcid(self, person_uuid: str, name: str):

        # Pure request
        response = get_pure_metadata('persons', person_uuid, {})

        message = f'\tPure get orcid        - {response} -'

        # External person
        if response.status_code == 404:
            self.report.add(['console'], f'{message} External person     - {person_uuid} - {name}')
            return False

        # Error
        elif response.status_code >= 300:
            self.report.add(['console'], f'{message} Error: {response.content}')
            return False

        # Load json
        resp_json = json.loads(response.content)

        # Read orcid
        if 'orcid' in resp_json:
            orcid = resp_json['orcid']
            self.report.add(['console'], f'{message} {orcid} - {name}')
            return orcid

        # Not found
        self.report.add(['console'], f'{message} Orcid not found     - {name}')
        return False        



    def _http_response_counter(self, status_code):
        if status_code not in self.global_counters['http_responses']:
            self.global_counters['http_responses'][status_code] = 0
        self.global_counters['http_responses'][status_code] += 1



    def _remove_uuid_from_list(self, uuid, file_name):
        """ If the given uuid is in the given file then the line will be removed """
        with open(file_name, "r") as f:
            lines = f.readlines()
        with open(file_name, "w") as f:
            for line in lines:
                if line.strip("\n") != uuid:
                    f.write(line)