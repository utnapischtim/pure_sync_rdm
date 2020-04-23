import json
from setup                          import pure_rest_api_url, dirpath, rdm_api_url_records, token_rdm
from source.general_functions       import add_to_full_report, itinialize_counters, add_spaces
from source.pure.general_functions  import pure_get_metadata
from source.rdm.general_functions   import rdm_get_metadata, rdm_get_recid_metadata, rdm_get_recid, update_rdm_record
from source.rdm.push_record         import create_invenio_data, rdm_push_record
from source.rdm.add_record          import RdmAddRecord
from source.rdm.database            import RdmDatabase

rdm_db = RdmDatabase()

class RdmOwners:

    #   ---         ---         ---
    def rdm_owner_check(self):
        """ Gets from pure all the records related to a certain user,
            afterwards it modifies/create RDM records accordingly. """

        # self.external_id = '56038' # TEMP
        # self.external_id = '3261' # TEMP
        self.external_id = '30' # TEMP

        add_to_full_report(f'\nUser external_id: {self.external_id}\n')

        # Gets the ID of the logged in user
        self.user_id = self.rdm_get_user_id()

        # If the user was not found in RDM then there is no owner to add to the record.
        if not self.user_id:
            return

        # Get from pure user_uuid
        self.user_uuid = self.pure_get_user_uuid('externalId', self.external_id)
        
        if not self.user_uuid:
            return False

        # Add user to user_ids_match table
        self.add_user_ids_match()

        # Gets from pure all records related to the user
        self.get_owner_records()


    #   ---         ---         ---
    def rdm_owner_by_orcid(self):

        orcid = '0000-0002-4154-6945'  # TEMP

        add_to_full_report(f'\norcid: {orcid}\n')

        if len(orcid) != 19:
            add_to_full_report('Warning - Orcid length it is not 19\n')

        # Gets the ID and IP of the logged in user
        self.user_id = self.rdm_get_user_id()

        # If the user was not found in RDM then there is no owner to add to the record.
        if not self.user_id:
            return

        # Get from pure user_uuid
        self.user_uuid = self.pure_get_user_uuid('orcid', orcid)
        
        if not self.user_uuid:
            return False

        self.get_owner_records()
        

    #   ---         ---         ---
    def get_owner_records(self):
        
        self.global_counters = itinialize_counters()

        rdm_add_record = RdmAddRecord()

        go_on     = True
        page      = 1
        page_size = 5
        count     = 0

        while go_on:

            url = f'{pure_rest_api_url}persons/{self.user_uuid}/research-outputs?page={page}&pageSize={page_size}'
            response = pure_get_metadata(url)

            if response.status_code >= 300:
                return False

            # Load response json
            resp_json = json.loads(response.content)

            total_items = resp_json['count']
            add_to_full_report(f'\nGet person records - {response} - Page {page} (size {page_size})    - Total records: {total_items}')

            if total_items == 0 and page == 1:
                add_to_full_report('\nThe user has no records - End task\n')
                return True

            go_on = self.is_there_a_next_page(resp_json, page)

            for item in resp_json['items']:
            
                uuid  = item['uuid']
                title = item['title']
                count += 1
                
                add_to_full_report(f'\n\tRecord uuid           - {uuid}   - {title[0:55]}...')

                # Get from RDM the recid
                recid = rdm_get_recid(uuid)

                # If the record is not in RDM, it is added
                if recid == False:
                    item['owners'] = [self.user_id]

                    add_to_full_report('\t+ Create record    +')
                    rdm_add_record.create_invenio_data(self.global_counters, item)

                else:
                    # Checks if the owner is already in RDM record metadata
                    # Get metadata from RDM
                    response = rdm_get_recid_metadata(recid)
                    record_json = json.loads(response.content)['metadata']

                    add_to_full_report(f"\tRDM get metadata      - {response} - Current owners:     - {record_json['owners']}")

                    # If the owner is not among metadata owners
                    if self.user_id and self.user_id not in record_json['owners']:

                        record_json['owners'].append(self.user_id)
                        add_to_full_report(f"\t+   Adding owner      -                  - New owners:         - {record_json['owners']}")

                        record_json = json.dumps(record_json)

                        file_name = f'{dirpath}/data/temporary_files/rdm_record_update.json'
                        open(file_name, 'a').write(record_json)

                        # Add owner to the record
                        update_rdm_record(record_json, recid)
                    else:
                        add_to_full_report('\t+ Owner in record  +')

            page += 1


    def is_there_a_next_page(self, resp_json, page):
            
        if 'navigationLinks' not in resp_json:
            return False
        elif page == 1:
            if 'next' not in resp_json['navigationLinks'][0]['ref']:
                return False
        else:
            if 'next' not in resp_json['navigationLinks'][1]['ref']:
                return False
        return True


    #   ---         ---         ---
    def pure_get_user_uuid(self, key_name: str, key_value: str):
        """ PURE get person records """

        keep_searching = True
        page_size = 250
        page = 1

        while keep_searching:

            url = f'{pure_rest_api_url}persons?page={page}&pageSize={page_size}&q=' + f'"{key_value}"'
            response = pure_get_metadata(url)

            if response.status_code >= 300:
                add_to_full_report(response.content)
                return False

            open(f'{dirpath}/data/temporary_files/pure_get_user_uuid.json', "wb").write(response.content)
            record_json = json.loads(response.content)

            total_items = record_json['count']

            add_to_full_report(f'Pure get user uuid - {response} - Total items: {total_items}')

            for item in record_json['items']:

                if item[key_name] == key_value:

                    first_name  = item['name']['firstName']
                    lastName    = item['name']['lastName']
                    uuid        = item['uuid']

                    add_to_full_report(f'User uuid          - {first_name} {lastName}  -  {uuid}')

                    if len(uuid) != 36:
                        add_to_full_report('\n- Warning! Incorrect user_uuid length -\n')
                        return False

                    return uuid

            if 'navigationLinks' in record_json:
                page += 1
            else:
                keep_searching = False

        add_to_full_report(f'\nUser uuid not found - Exit task\n')
        return False


    #   ---         ---         ---
    def rdm_get_user_id(self):
        """ Gets the ID and IP of the logged in user """

        response = rdm_db.db_query(f"SELECT user_id, ip FROM accounts_user_session_activity")

        if not response:
            add_to_full_report('\n- accounts_user_session_activity: No user is logged in -\n')
            return False

        elif len(response) > 1:
            add_to_full_report('\n- accounts_user_session_activity: Multiple users in \n')
            return False

        add_to_full_report(f'user IP: {response[0][1]} - user_id: {response[0][0]}')

        self.rdm_record_owner = response[0][0]

        return self.rdm_record_owner


    def add_user_ids_match(self):

        file_name = f"{dirpath}/data/user_ids_match.txt"

        needs_to_add = self.check_user_ids_match(file_name)

        if needs_to_add:
            open(file_name, 'a').write(f'{self.user_id} {self.user_uuid} {self.external_id}\n')
            add_to_full_report(f'user_ids_match     - Adding id toList - {self.user_id}, {self.user_uuid}, {self.external_id}')


    def check_user_ids_match(self, file_name: str):

        file_data = open(file_name).readlines()
        for line in file_data:
            line = line.split('\n')[0]
            line = line.split(' ')

            # Checks if at least one of the ids match
            if str(self.user_id) == line[0] or self.user_uuid == line[1] or self.external_id == line[2]:
                
                if line == [str(self.user_id), self.user_uuid, self.external_id]:
                    add_to_full_report('user_ids_match     - full match')
                    return False
        
        return True





#   ---         ---         ---
def get_rdm_record_owners():
            
    pag = 1
    pag_size = 250

    count = 0
    count_records_per_owner = {}
    all_records_list = ''
    go_on = True

    # Empty file
    file_owner = f"{dirpath}/data/temporary_files/rdm_records_owner.txt"
    open(file_owner, 'w').close()

    while go_on == True:

        # REQUEST to RDM
        url = f'{rdm_api_url_records}api/records/?sort=mostrecent&size={pag_size}&page={pag}'
        response = rdm_get_metadata(url)

        add_to_full_report(f'\n{response}\n')
        
        file_name = f"{dirpath}/data/temporary_files/rdm_get_records.json"
        open(file_name, 'wb').write(response.content)

        if response.status_code >= 300:
            add_to_full_report(response.content)
            break

        resp_json = json.loads(response.content)
        data = ''

        for item in resp_json['hits']['hits']:
            count += 1

            uuid   = item['metadata']['uuid']
            recid  = item['metadata']['recid']
            owners = item['metadata']['owners']

            line = f'{uuid} - {recid} - {owners}'
            add_to_full_report(line)
            data += f'{line}\n'
            
            all_records_list += f'{uuid} {recid}\n'

            for i in owners:
                if i not in count_records_per_owner:
                    count_records_per_owner[i] = 0
                count_records_per_owner[i] += 1

        add_to_full_report(f'\nPag {str(pag)} - Records {count}\n')
        
        open(file_owner, 'a').write(data)

        if 'next' not in resp_json['links']:
            go_on = False
        
        pag += 1

    add_to_full_report('Owner  Records')

    for key in count_records_per_owner:
        records = add_spaces(count_records_per_owner[key])
        key     = add_spaces(key)
        add_to_full_report(f'{key}    {records}')
    
    # Updates content of all_rdm_records.txt file
    file_all_records_list = f"{dirpath}/data/all_rdm_records.txt"
    # Empty file
    open(file_all_records_list, 'w').close()
    # Add all records to file
    open(file_all_records_list, 'a').write(all_records_list)