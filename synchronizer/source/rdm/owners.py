import json
from datetime                       import date, datetime
from setup                          import pure_rest_api_url, rdm_host_url, token_rdm, data_files_name
from source.general_functions       import initialize_counters, add_spaces
from source.pure.general_functions  import get_next_page
from source.pure.requests           import get_pure_metadata
from source.rdm.general_functions   import get_recid, update_rdm_record
from source.rdm.add_record          import RdmAddRecord
from source.rdm.database            import RdmDatabase
from source.rdm.requests            import Requests
from source.reports                 import Reports

class RdmOwners:

    def __init__(self):
        self.rdm_requests   = Requests()
        self.rdm_db         = RdmDatabase()
        self.report         = Reports()
        self.rdm_add_record = RdmAddRecord()

    def _decorator(func):
        def _wrapper(self, identifier) :

            self.report.add_template(['console'], ['general', 'title'], ['OWNERS CHECK'])
            self.global_counters = initialize_counters()

            # Decorated function
            func(self, identifier)

        return _wrapper

    @_decorator
    def run_owners(self, identifier: str):
        """ Gets from pure all the records related to a certain user (based on orcid or externalId),
            afterwards it modifies/create RDM records accordingly. """

        identifier_value = '0000-0002-4154-6945'      # TEMPORARY
        if identifier == 'externalId':                # TEMPORARY
            identifier_value = '3261'                 # TEMPORARY
            # identifier_value = '30'                   # TEMPORARY
        
        self.report.add([], f'\n{identifier}: {identifier_value}\n')

        # Gets the ID and IP of the logged in user
        self.user_id = self._get_user_id_from_rdm()
        # If the user was not found in RDM then there is no owner to add to the record.
        if not self.user_id:
            return

        # Get from pure user_uuid
        self.user_uuid = self._get_user_uuid_from_pure(identifier, identifier_value)
        if not self.user_uuid:
            return False

        # Add user to user_ids_match.txt
        if identifier == 'externalId':
            self._add_user_ids_match(identifier_value)

        next_page = True
        page      = 1
        page_size = 100

        self.local_counters = {'create': 0, 'in_record': 0, 'to_update': 0}

        while next_page:

            # Pure request
            params = {'sort': 'modified', 'page': page, 'pageSize': page_size}
            response = get_pure_metadata('persons', f'{self.user_uuid}/research-outputs', params)
            if response.status_code >= 300:
                return False

            # Initial response proceses and json load
            pure_json = self._response_first_process(response, page, page_size)
            # In case the user has no records
            if not pure_json:
                return True

            # Checks if there is a 'next' page to be processed
            next_page = get_next_page(pure_json)

            # Iterates over all items in the page
            for item in pure_json['items']:
            
                uuid  = item['uuid']
                title = item['title']
                
                self.report.add([], f'\n\tRecord uuid           - {uuid}   - {title[0:55]}...')

                # Get from RDM the recid
                recid = get_recid(uuid)

                # Record NOT in RDM, create it
                if recid == False:
                    self._create_rdm_record(item)
                    continue

                # Gets recid metadata from RDM and checks if the user is already a record owner
                response = self.rdm_requests.get_metadata_by_recid(recid)
                rdm_json = json.loads(response.content)['metadata']

                self.report.add([], f"\tRDM get metadata      - {response} - Current owners:     - {rdm_json['owners']}")

                if self.user_id not in rdm_json['owners']:
                    # The record is in RDM but the logged in user is not among the recod owners
                    self._add_user_as_owner(rdm_json, recid)
                else:
                    # The record is in RDM and the user is an owner
                    self.report.add([], '\tRDM record status     -                  - Owner IN record')
                    self.local_counters['in_record'] += 1
            
            page += 1

        self._final_report()

    

    def _add_user_as_owner(self, rdm_json, recid):
        # Adds the current logged in user as record owner
        rdm_json['owners'].append(self.user_id)

        self.report.add([], f"\tRDM record status     - ADDING owner     - New owners:         - {rdm_json['owners']}")

        # Add owner to an existing RDM record
        update_rdm_record(json.dumps(rdm_json), recid)

        self.local_counters['to_update'] += 1


    def _create_rdm_record(self, item: dict):
        item['owners'] = [self.user_id]

        self.report.add([], '\tRDM record status     -                  - CREATE record')
        self.local_counters['create'] += 1

        # Creates record metadata and pushes it to RDM
        self.rdm_add_record.create_invenio_data(self.global_counters, item)


    def _final_report(self):
        # Final report
        report = f"\nCreate: {self.local_counters['create']} - To update: {self.local_counters['to_update']} - In record:{self.local_counters['in_record']}"
        self.report.add(['console', 'owners'], report)
        self.report.summary_global_counters(['console', 'owners'], self.global_counters)


    def _response_first_process(self, response: object, page: int, page_size: int):

        # Load response json
        resp_json = json.loads(response.content)

        total_items = resp_json['count']

        if page == 1:
            self.report.add([], f'Total records: {total_items}')

        if page == 1 and total_items == 0:
            self.report.add([], '\nThe user has no records - End task\n')
            return False

        self.report.add([], f'\nPag {page} - Get person records    - {response} - (size {page_size})')
        return resp_json


    def _get_user_uuid_from_pure(self, key_name: str, key_value: str):
        """ PURE get person records """

        # If the uuid is not found in the first x items then it will continue with the next page
        page = 1
        page_size = 10
        next_page = True

        while next_page:

            params = {'page': page, 'pageSize': page_size, 'q': f'"{key_value}"' }
            response = get_pure_metadata('persons', '', params)

            if response.status_code >= 300:
                self.report.add(['console', 'owners'], response.content)
                return False

            record_json = json.loads(response.content)

            total_items = record_json['count']

            for item in record_json['items']:

                if item[key_name] == key_value:
                    first_name  = item['name']['firstName']
                    lastName    = item['name']['lastName']
                    uuid        = item['uuid']

                    self.report.add(['console', 'owners'], f'Pure get user uuid - {response} - {first_name} {lastName}  -  {uuid}')

                    if len(uuid) != 36:
                        self.report.add(['console', 'owners'], '\n- Warning! Incorrect user_uuid length -\n')
                        return False
                    return uuid

            # Checks if there is a 'next' page to be processed
            next_page = get_next_page(record_json)
            
            page += 1

        self.report.add(['console', 'owners'], f'Pure get user uuid - {response} - NOT FOUND - End task\n')
        return False


    #   ---         ---         ---
    def _get_user_id_from_rdm(self):
        """ Gets the ID and IP of the logged in user """

        response = self.rdm_db.select_query('user_id, ip', 'accounts_user_session_activity')

        if not response:
            self.report.add(['console', 'owners'], '\n- accounts_user_session_activity: No user is logged in -\n')
            return False

        elif len(response) > 1:
            self.report.add(['console', 'owners'], '\n- accounts_user_session_activity: Multiple users logged in \n')
            return False

        self.report.add(['console', 'owners'], f'user IP: {response[0][1]} - user_id: {response[0][0]}')

        self.rdm_record_owner = response[0][0]

        return self.rdm_record_owner


    def _add_user_ids_match(self, external_id: str):
        """ Add user to user_ids_match.txt, where are specified:
            rdm_user_id, user_uuid and user_external_id """
        file_name = data_files_name['user_ids_match']

        needs_to_add = self._check_user_ids_match(file_name, external_id)

        if needs_to_add:
            open(file_name, 'a').write(f'{self.user_id} {self.user_uuid} {external_id}\n')
            report = f'user_ids_match     - Adding id toList - {self.user_id}, {self.user_uuid}, {external_id}'
            self.report.add(['console', 'owners'], report)


    def _check_user_ids_match(self, file_name: str, external_id: str):

        file_data = open(file_name).readlines()
        for line in file_data:
            line = line.split('\n')[0]
            line = line.split(' ')

            # Checks if at least one of the ids match
            if str(self.user_id) == line[0] or self.user_uuid == line[1] or external_id == line[2]:
                
                if line == [str(self.user_id), self.user_uuid, external_id]:
                    self.report.add(['console', 'owners'], 'user_ids_match     - full match')
                    return False
        return True



    def get_rdm_record_owners(self):
        """ Gets all records from RDM and counts how many records belong to each user.
            It also updates the content of all_rdm_records.txt """

        self.report.add_template(['console'], ['general', 'title'], ['RECORDS OWNER'])
                
        pag = 1
        pag_size = 250

        count = 0
        count_records_per_owner = {}
        all_records_list = ''
        next_page = True

        # Empty file
        file_owner = data_files_name['rdm_record_owners']
        open(file_owner, 'w').close()

        while next_page == True:

            # REQUEST to RDM
            params = {'sort': 'mostrecent', 'size': pag_size, 'page': pag}
            response = self.rdm_requests.rdm_get_metadata(params)

            self.report.add([], f'\n{response}\n')

            if response.status_code >= 300:
                self.report.add([], response.content)
                break

            resp_json = json.loads(response.content)
            data = ''

            for item in resp_json['hits']['hits']:
                count += 1

                uuid   = item['metadata']['uuid']
                recid  = item['metadata']['recid']
                owners = item['metadata']['owners']

                line = f'{uuid} - {recid} - {owners}'
                self.report.add([], line)
                data += f'{line}\n'
                
                all_records_list += f'{uuid} {recid}\n'

                for i in owners:
                    if i not in count_records_per_owner:
                        count_records_per_owner[i] = 0
                    count_records_per_owner[i] += 1

            self.report.add([], f'\nPag {str(pag)} - Records {count}\n')
            
            open(file_owner, 'a').write(data)

            if 'next' not in resp_json['links']:
                next_page = False
            
            pag += 1

        self.report.add([], 'Owner  Records')

        for key in count_records_per_owner:
            records = add_spaces(count_records_per_owner[key])
            key     = add_spaces(key)
            self.report.add([], f'{key}    {records}')
        
        # Updates content of all_rdm_records.txt file
        file_all_records_list = data_files_name['all_rdm_records']
        # Empty file
        open(file_all_records_list, 'w').close()
        # Add all records to file
        open(file_all_records_list, 'a').write(all_records_list)