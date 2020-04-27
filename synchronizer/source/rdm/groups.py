import json
import os
from datetime                       import date, datetime
from setup                          import rdm_host_url, pure_rest_api_url
from source.general_functions       import add_spaces, add_to_full_report, dirpath
from source.pure.general_functions  import pure_get_metadata
from source.rdm.general_functions   import update_rdm_record, get_metadata_by_query
from source.rdm.database            import RdmDatabase
from source.reports                 import Reports


class RdmGroups:

    def __init__(self):
        # Create instance of RDM database manager
        self.rdm_db = RdmDatabase()
        self.reports = Reports()

        self.report_name = 'groups'

    
    def rdm_group_split(self, old_group_externalId: str, new_groups_externalIds: list):
        """ 
        1 - Create new groups
        2 - Add users to new groups
        3 - Remove users from old group
        4 - Delete old group
        5 - Modify RDM record: 
            . groupRestrictions
            . managingOrganisationUnit (if necessary)
            . organisationUnits
        """

        current_time = datetime.now().strftime("%H:%M:%S")

        # Report
        report = f"""

    --   --   --

    {current_time} - RDM GROUP SPLIT -

    Old group             - externalId: {old_group_externalId}
    """
        self.reports.add_to_report(self.report_name, report)

        report = f'\nOld group: {old_group_externalId} - New groups: {new_groups_externalIds}\n'
        add_to_full_report(report)

        # Get name and uuid of new groups
        new_groups_data = []

        for externalId in new_groups_externalIds:
            # Get group information
            response = self.pure_get_organisationalUnit_data(externalId)

            if not response:
                add_to_full_report(f'\nGroup {old_group_externalId} not found in Pure\n')
                return False

            new_groups_data.append(response)

            report = f"\nNew group             - externalId: {externalId}   - {response['uuid']} - {response['name']}\n"
            self.reports.add_to_report(self.report_name, report)

            # Create new group
            response = self.rdm_create_group(externalId, response['name'])
            
            report = f'New group creation    - {response}\n'
            self.reports.add_to_report(self.report_name, report)

        # Get group id
        query = f"SELECT id FROM accounts_role WHERE name = '{old_group_externalId}';"
        old_group_id = self.rdm_db.db_query(query)[0][0]
        full_report = f'\tOld group             - Id:        {add_spaces(old_group_id)}'
        add_to_full_report(full_report)

        # Removes users from old group and adds to new groups
        self.rdm_split_users_from_old_to_new_group(old_group_id, report_name, old_group_externalId, new_groups_externalIds)

        # Modify all related records
        self.rdm_split_modify_record(old_group_externalId, report_name, new_groups_data, new_groups_externalIds)


    #   ---         ---         ---
    def rdm_group_merge(self, old_groups_externalId: list, new_group_externalId: str):
        """ 
        1 - Create new group
        2 - Remove users from old groups
        3 - Add users to new group
        4 - Delete old groups
        5 - Modify RDM records: 
            . groupRestrictions
            . managingOrganisationUnit (if necessary)
            . organisationUnits
        """
        # Report
        current_time = datetime.now().strftime("%H:%M:%S")
        self.report_name = report_name = f'{dirpath}/reports/{date.today()}_groups.log'

        report = f"\n\n--   --   --\n\n{current_time} - RDM GROUP MERGE -\n\n"
        open(report_name, "a").write(report)

        add_to_full_report(f'{report}Old groups: {old_groups_externalId}\n')

        # Get name and uuid of new organisationalUnit
        new_group_data = self.pure_get_organisationalUnit_data(new_group_externalId)
        if not new_group_data:
            add_to_full_report(f'\nWarning - New group ({new_group_externalId}) not in Pure - Abort task\n')
            return False

        report = f"New group             - externalId: {add_spaces(new_group_externalId)}   - {new_group_data['name']}\n"
        open(report_name, "a").write(report)

        # Create new group
        response = self.rdm_create_group(new_group_externalId, new_group_data['name'])
        open(report_name, "a").write(f'New group creation    - {response}\n')

        # Adds users to new group and removes them from the old ones
        self.rdm_merge_users_from_old_to_new_group(old_groups_externalId, report_name, new_group_externalId)

        # Modify all related records
        self.rdm_merge_modify_records(old_groups_externalId, report_name, new_group_data, new_group_externalId)


    #   ---         ---         ---
    def rdm_split_modify_record(self, old_group_externalId, report_name, new_groups_data, new_groups_externalIds):

        # Get from RDM all old group's records
        response = get_metadata_by_query(old_group_externalId)

        resp_json = json.loads(response.content)
        total_items = resp_json['hits']['total']

        report = f"\nModify records - Group: {old_group_externalId} - Number records: {total_items}\n"
        open(report_name, "a").write(report)
        add_to_full_report(f'\t{report}')

        if total_items == 0:
            return True

        # Iterates over all old group records
        for item in resp_json['hits']['hits']:
            item = item['metadata']

            recid = item['recid']
            url = f'{rdm_host_url}api/records/{recid}'
            add_to_full_report(f'\tRecid:               {url}')

            # Removes old organisationalUnit from organisationalUnits
            for i in item['organisationalUnits']:
                if i['externalId'] == old_group_externalId:
                    item['organisationalUnits'].remove(i)

            # Adds new organisationalUnits
            for i in new_groups_data:
                item['organisationalUnits'].append(i)

            # Change group restrictions
            if old_group_externalId in item['groupRestrictions']:
                item['groupRestrictions'].remove(old_group_externalId)
            for i in new_groups_externalIds:
                item['groupRestrictions'].append(i)

            # Change managingOrganisationalUnit
            if item['managingOrganisationalUnit_externalId'] == old_group_externalId:
                item['managingOrganisationalUnit_name']       = new_groups_data[0]['name']
                item['managingOrganisationalUnit_uuid']       = new_groups_data[0]['uuid']
                item['managingOrganisationalUnit_externalId'] = new_groups_data[0]['externalId']

            record_json = json.dumps(item)

            # Update record
            response = update_rdm_record(record_json, recid)

            current_time = datetime.now().strftime("%H:%M:%S")
            open(report_name, "a").write(f'{current_time} - {response} - {url}\n')

        return True


    #   ---         ---         ---
    def rdm_split_users_from_old_to_new_group(self, old_group_id, report_name, old_group_externalId, new_groups_externalIds):
        # Get all users in old group
        query = f"SELECT user_id FROM accounts_userrole WHERE role_id = {old_group_id};"
        response = self.rdm_db.db_query(query)

        report = 'Old group             - Num. of users: '
        if not response:
            report += '0'
            add_to_full_report(f'\t{report}')
            open(report_name, "a").write(f'\n{report}\n')
        else:
            report += f'{len(response)}'
            add_to_full_report(f'\t{report}')
            open(report_name, "a").write(f'\n{report}\n')

            for i in response:

                user_id = i[0]

                # Get user email
                user_email = self.get_user_email(user_id)
                
                for new_group_externalId in new_groups_externalIds:
                    # Add user to new groups
                    self.group_add_user(user_email, new_group_externalId, user_id)

                # Remove user from old group
                response = self.group_remove_user(user_email, old_group_externalId)

        # Delete old group


    #   ---         ---         ---
    def rdm_merge_modify_records(self, old_groups_externalId, report_name, new_group_data, new_group_externalId):

        add_to_full_report('\n- Modify records -')
        
        # Get from RDM all records with old groups
        for old_group_externalId in old_groups_externalId:
            
            # Get record metadata
            response = get_metadata_by_query(old_group_externalId)


            resp_json = json.loads(response.content)
            total_items = resp_json['hits']['total']

            report = f"\nModify records - Group: {old_group_externalId} - Number records: {total_items}"
            open(report_name, "a").write(report)
            add_to_full_report(f'\t{report}')

            if total_items == 0:
                continue
            
            # Iterates over all old group records
            for item in resp_json['hits']['hits']:

                item = item['metadata']
                recid = item['recid']

                url = f'{rdm_host_url}api/records/{recid}'
                add_to_full_report(f"\tRecid:               {url}")

                # + Organisational units +
                new_organisationalUnits_data = [new_group_data]

                for i in item['organisationalUnits']:
                    if (i['externalId'] in old_groups_externalId or 
                        i['externalId'] == new_group_data['externalId']):
                        continue
                    
                    new_organisationalUnits_data.append(i)

                item['organisationalUnits'] = new_organisationalUnits_data

                # + Group restrictions +
                # Remove old group
                if old_group_externalId in item['groupRestrictions']:
                    item['groupRestrictions'].remove(old_group_externalId)
                # Add new group
                if new_group_externalId not in item['groupRestrictions']:
                    item['groupRestrictions'].append(new_group_externalId)

                # + Managing Organisational Unit +
                if item['managingOrganisationalUnit_externalId'] == old_group_externalId:
                    item['managingOrganisationalUnit_name']       = new_group_data['name']
                    item['managingOrganisationalUnit_uuid']       = new_group_data['uuid']
                    item['managingOrganisationalUnit_externalId'] = new_group_data['externalId']

                record_json = json.dumps(item)

                # Update record
                response = update_rdm_record(record_json, recid)

                current_time = datetime.now().strftime("%H:%M:%S")
                report = f'{current_time} - {response} - {url}\n'
                open(report_name, "a").write(report)


    #   ---         ---         ---
    def rdm_merge_users_from_old_to_new_group(self, old_groups_externalId, report_name, new_group_externalId):
        # Iterate over old groups
        for old_group_externalId in old_groups_externalId:

            # Get group id
            query          = f"SELECT id, description FROM accounts_role WHERE name = '{old_group_externalId}';"
            response       = self.rdm_db.db_query(query)

            if not response:
                add_to_full_report('\nWarning - Old group ({old_groups_externalId}) not in database - Abort task\n')
                return False

            old_group_id   = response[0][0]
            old_group_name = response[0][1]

            # Get all users id that are in this group
            query = f"SELECT user_id FROM accounts_userrole WHERE role_id = {old_group_id};"
            old_group_users = self.rdm_db.db_query(query)

            if not old_group_users:

                old_group_users = []
            
            report = f"Old group (id {add_spaces(old_group_id)})  - Number users: {add_spaces(len(old_group_users))}\
    - externalId:  {add_spaces(old_group_externalId)} - {old_group_name}"
            open(report_name, "a").write(f'{report}\n')
            add_to_full_report(report)
            
            for i in old_group_users:
                user_id = i[0]

                # Get user email
                user_email = self.get_user_email(user_id)

                # - - Add user to new group - -
                self.group_add_user(user_email, new_group_externalId, user_id)

                # - - Remove user from old group - -
                response = self.group_remove_user(user_email, old_group_externalId)

            # Delete old group


    #   ---         ---         ---
    def pure_get_organisationalUnit_data(self, externalId: str):
        """ Get organisationalUnit name and uuid """

        # # PURE REQUEST
        page = 'page=1'
        size = 'pageSize=100'
        url = f'{pure_rest_api_url}organisational-units/{externalId}/research-outputs?{size}&{page}'
        response = pure_get_metadata(url)

        # Add response content to pure_get_uuid_metadata.json
        file_response = f'{dirpath}/data/temporary_files/pure_get_uuid_metadata.json'
        open(file_response, 'wb').write(response.content)

        # Check response
        if response.status_code >= 300:
            add_to_full_report(response.content)
            return False

        # Load json
        data = json.loads(response.content)
        data = data['items'][0]['organisationalUnits']

        for organisationalUnit in data:
            if organisationalUnit['externalId'] == externalId:

                organisationalUnit_data = {}
                organisationalUnit_data['externalId'] = externalId
                organisationalUnit_data['uuid']       = organisationalUnit['uuid']
                organisationalUnit_data['name']       = organisationalUnit['names'][0]['value']

                return organisationalUnit_data

        
    #   ---         ---         ---
    def get_user_email(self, user_id):
        # Get user email
        query      = f"SELECT email FROM accounts_user WHERE id = {user_id};"
        user_email = self.rdm_db.db_query(query)[0][0]

        report     = f'\tChange user groups    - User id:      {add_spaces(user_id)} - Email: {user_email}'
        add_to_full_report(report)

        return user_email


    #   ---         ---         ---
    def rdm_create_group(self, group_externalId: str, group_name: str):
        response = self.rdm_db.db_query(f"SELECT * FROM accounts_role WHERE name = '{group_externalId}'")
        message   = f'\tRDM search group      -  ExtId:   {add_spaces(group_externalId)}  -'
        message_2 = f'          - {group_name[0:40]}'

        # If the group has already been created
        if response:
            report = f'{message} Found     {message_2}'
            add_to_full_report(report)
            return 'Already exists'

        report = f'{message} Not found {message_2}'
        add_to_full_report(report)

        group_name = group_name.replace('(', '\(')
        group_name = group_name.replace(')', '\)')
        group_name = group_name.replace(' ', '_')
        command = f'pipenv run invenio roles create {group_externalId} -d {group_name}'
        response = os.system(command)

        if response != 0:
            add_to_full_report(f'\tWarning - Creating group response: {response}')
            return f'Error: {response}'

        return 'Success'


    #   ---         ---         ---
    def rdm_add_user_to_group(self, user_id: int, group_externalId: str, group_name: str):

        # Get user's rdm email
        user_email = self.rdm_db.db_query(f"SELECT email FROM accounts_user WHERE id = {user_id}")[0][0]

        # Get group id
        query = f"SELECT id FROM accounts_role WHERE name = '{group_externalId}'"
        response = self.rdm_db.db_query(query)

        if not response:
            # If the group does not exist then creates it
            self.rdm_create_group(group_externalId, group_name)
            # Repeats the query to get the group id
            group_id = self.rdm_db.db_query(query)

        group_id = response[0][0]

        # Checks if match already exists
        response = self.rdm_db.db_query(f"SELECT * FROM accounts_userrole WHERE user_id = {user_id} AND role_id = {group_id}")

        if response:
            report = f'\tRDM user in group  - User id: {add_spaces(user_id)}   -                     - Already belongs to group {group_externalId} (id {group_id})'
            add_to_full_report(report)
            return True

        # Adds user to group
        command = f'pipenv run invenio roles add {user_email} {group_externalId}'
        response = os.system(command)
        if response != 0:
            add_to_full_report(f'Warning - Creating group response: {response}')


    #   ---         ---         ---
    def group_add_user(self, user_email, new_group_externalId, user_id):
        
        # Get group id
        query = f"SELECT id FROM accounts_role WHERE name = '{new_group_externalId}';"
        group_id = self.rdm_db.db_query(query)[0][0]
        
        # Check if the user is already in the group
        query = f"SELECT * FROM accounts_userrole WHERE user_id = {user_id} AND role_id = {group_id};"
        response = self.rdm_db.db_query(query)

        report =  f'Add to group          - User id:      {add_spaces(user_id)} - Group:       {add_spaces(new_group_externalId)}'

        if response:
            return True

        # Add user to new groups
        full_report  = f'\t                     - Adding user to group {new_group_externalId}'
        full_report += '\t                      - Remove user from old group'
        add_to_full_report(full_report)

        command = f'pipenv run invenio roles add {user_email} {new_group_externalId}'
        response = os.system(command)

        if response != 0:
            # add_to_full_report(f'Warning - Creating group response: {response}')
            # open(shell_interface.report_name, "a").write(f'{report} - Error: {response}\n')
            return False

        # open(shell_interface.report_name, "a").write(f'{report} - Success\n')
        return True


    #   ---         ---         ---
    def group_remove_user(self, user_email, group_name):
        
        # Get user id
        query = f"SELECT id FROM accounts_user WHERE email = '{user_email}';"
        user_id = self.rdm_db.db_query(query)[0][0]
        
        # Get group id
        query = f"SELECT id FROM accounts_role WHERE name = '{group_name}';"
        group_id = self.rdm_db.db_query(query)[0][0]
        
        # Check if the user is already in the group
        query = f"SELECT * FROM accounts_userrole WHERE user_id = {user_id} AND role_id = {group_id};"
        response = self.rdm_db.db_query(query)

        report =  f'Remove from group     - User id:      {add_spaces(user_id)} - Group:       {add_spaces(group_name)}'

        if not response:
            # open(shell_interface.report_name, "a").write(f'{report} - Already removed from group\n')
            return True

        # Remove user from old group
        full_report = '\t                      - Remove user from old group'
        add_to_full_report(full_report)

        command = f'pipenv run invenio roles remove {user_email} {group_name}'
        response = os.system(command)

        if response != 0:
            add_to_full_report(f'Warning - Creating group response: {response}')
            # open(shell_interface.report_name, "a").write(f'{report} - Error: {response}\n')
            return False

        # open(shell_interface.report_name, "a").write(f'{report} - Success\n')
        return True