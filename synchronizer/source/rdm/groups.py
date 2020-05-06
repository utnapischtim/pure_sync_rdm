import json
import os
from source.general_functions       import add_spaces, current_time
from source.pure.general_functions  import get_pure_metadata
from source.rdm.general_functions   import update_rdm_record, get_metadata_by_query
from source.rdm.database            import RdmDatabase
from source.reports                 import Reports


class RdmGroups:

    def __init__(self):
        self.rdm_db = RdmDatabase()
        self.report = Reports()
        self.report_files = ['console', 'groups']

    
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
        self.report.add_template(self.report_files, ['general', 'title'], ['GROUP SPLIT', current_time()])
        self.report.add(self.report_files, f'\nOld group: {old_group_externalId} - New groups: {new_groups_externalIds}\n')

        # Get name and uuid of new groups
        self.new_groups_data = []

        for externalId in new_groups_externalIds:
            # Get group information
            group_name = self._get_pure_group_metadata(externalId)
            if not group_name:
                return False

            # Create new group
            response = self.rdm_create_group(externalId, group_name)

        # Get old group id
        old_group_id = self._get_rdm_group_id(old_group_externalId)

        # Removes users from old group and adds to new groups
        self._rdm_split_users_from_old_to_new_group(old_group_id, old_group_externalId, new_groups_externalIds)

        # Modify all related records
        self._rdm_split_modify_record(old_group_externalId, new_groups_externalIds)



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
        self.report.add_template(self.report_files, ['general', 'title'], ['GROUP MERGE', current_time()])
        self.report.add(self.report_files, f'\nOld groups: {old_groups_externalId} - New group: {new_group_externalId}\n')

        # Get new group information
        self.new_groups_data = []
        group_name = self._get_pure_group_metadata(new_group_externalId)
        if not group_name:
            return False

        # Create new group
        response = self.rdm_create_group(new_group_externalId, group_name)

        # Adds users to new group and removes them from the old ones
        self._merge_users_from_old_to_new_group(old_groups_externalId, new_group_externalId)

        # Modify all related records
        self._rdm_merge_modify_records(old_groups_externalId, self.new_groups_data[0], new_group_externalId)



    def _get_rdm_group_id(self, externalId):
        response = self.rdm_db.select_query('id, description', 'accounts_role', {'name': f"'{externalId}'"})

        group_id    = response[0][0]
        group_name  = response[0][1]

        report = f'\tOld group             - ExtId:     {add_spaces(externalId)} - RDM id:      {add_spaces(group_id)} - {group_name}'
        self.report.add(['console', 'groups'], report)
        return group_id



    def _rdm_split_modify_record(self, old_group_externalId, new_groups_externalIds):

        # Get from RDM all old group's records
        response = get_metadata_by_query(old_group_externalId)

        resp_json = json.loads(response.content)
        total_items = resp_json['hits']['total']

        report = f"\tModify old g. records - ExtId:     {add_spaces(old_group_externalId)} - Num. of records: {total_items}"
        self.report.add(['console', 'groups'], report)

        if total_items == 0:
            self.report.add(['console', 'groups'], '\tNothing to modify     - End')
            return True

        # Iterates over all old group records
        for item in resp_json['hits']['hits']:
            item = item['metadata']

            # Removes old organisationalUnit from organisationalUnits
            for i in item['organisationalUnits']:
                if i['externalId'] == old_group_externalId:
                    item['organisationalUnits'].remove(i)

            # Adds new organisationalUnits
            for i in self.new_groups_data:
                item['organisationalUnits'].append(i)

            # Change group restrictions
            if old_group_externalId in item['groupRestrictions']:
                item['groupRestrictions'].remove(old_group_externalId)
            for i in new_groups_externalIds:
                item['groupRestrictions'].append(i)

            # Change managingOrganisationalUnit
            if item['managingOrganisationalUnit_externalId'] == old_group_externalId:
                item['managingOrganisationalUnit_name']       = self.new_groups_data[0]['name']
                item['managingOrganisationalUnit_uuid']       = self.new_groups_data[0]['uuid']
                item['managingOrganisationalUnit_externalId'] = self.new_groups_data[0]['externalId']

            record_json = json.dumps(item)

            # Update record
            recid = item['recid']
            response = update_rdm_record(record_json, recid)

        return True



    def _rdm_split_users_from_old_to_new_group(self, old_group_id, old_group_externalId, new_groups_externalIds):

        # Get all users in old group
        response = self.rdm_db.select_query('user_id', 'accounts_userrole', {'role_id': old_group_id})

        report = 'Old group                                - Num. of users:  '
        if not response:
            self.report.add(['console', 'groups'], f'\t{report} 0')
            return

        self.report.add(['console', 'groups'], f'\t{report} {len(response)}')

        for i in response:
            user_id = i[0]

            # Get user email
            user_email = self.rdm_db.select_query('email', 'accounts_user', {'id': user_id})[0][0]
            
            for new_group_externalId in new_groups_externalIds:
                # Add user to new groups
                self._group_add_user(user_email, new_group_externalId, user_id)

            # Remove user from old group
            response = self._group_remove_user(user_email, old_group_externalId)



    def _rdm_merge_modify_records(self, old_groups_externalId, new_group_data, new_group_externalId):

        # Get from RDM all records with old groups
        for old_group_externalId in old_groups_externalId:

            self._rdm_check_if_group_exists(old_group_externalId)
            
            # Get record metadata
            response = get_metadata_by_query(old_group_externalId)


            resp_json = json.loads(response.content)
            total_items = resp_json['hits']['total']

            report = f"\tModify records        - Group:     {add_spaces(old_group_externalId)} - Num. of records: {total_items}"
            self.report.add(['console', 'groups'], report)

            if total_items == 0:
                continue
            
            # Iterates over all old group records
            for item in resp_json['hits']['hits']:

                item = item['metadata']

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
                recid = item['recid']
                response = update_rdm_record(record_json, recid)




    def _merge_users_from_old_to_new_group(self, old_groups_externalId, new_group_externalId):
        # Iterate over old groups
        for old_group_externalId in old_groups_externalId:

            # Get group id
            response = self.rdm_db.select_query('id, description', 'accounts_role', {'name': f"'{old_group_externalId}'"})

            if not response:
                self.report.add(['console'], '\nWarning - Old group ({old_groups_externalId}) not in database - END TASK\n')
                return False

            old_group_id   = response[0][0]
            old_group_name = response[0][1]

            # Get all users id that are in this group
            old_group_users = self.rdm_db.select_query('user_id', 'accounts_userrole', {'role_id': old_group_id})

            if not old_group_users:
                old_group_users = []
	
            report = f"\tOld group             - ExtId:     {add_spaces(old_group_externalId)} - Num. users:  {add_spaces(len(old_group_users))} - {old_group_name}"
            self.report.add(['console', 'groups'], report)
            
            for i in old_group_users:
                user_id = i[0]

                # Get user email
                user_email = self.rdm_db.select_query('email', 'accounts_user', {'id': user_id})[0][0]

                # - - Add user to new group - -
                self._group_add_user(user_email, new_group_externalId, user_id)

                # - - Remove user from old group - -
                response = self._group_remove_user(user_email, old_group_externalId)

            # Delete old group



    def _get_pure_group_metadata(self, externalId: str):
        """ Get organisationalUnit name and uuid """

        # PURE REQUEST
        response = get_pure_metadata('organisational-units', f'{externalId}/research-outputs', {'page': 1, 'pageSize': 100})

        report = f'\tGroup information     - ExtId:     {add_spaces(externalId)} - '

        # Check response
        if response.status_code >= 300:
            report += 'Not in pure - END TASK\n'
            self.report.add(['console', 'groups'], report)
            self.report.add(['console', 'groups'], response.content)
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

                report += f"{organisationalUnit_data['uuid']} - {organisationalUnit_data['name']}"
                self.report.add(['console', 'groups'], report)

                self.new_groups_data.append(organisationalUnit_data)
                return organisationalUnit_data['name']
        return False



    def _rdm_check_if_group_exists(self, group_externalId):
        """ Checks if the group already exists"""

        response = self.rdm_db.select_query('*', 'accounts_role', {'name': f"'{group_externalId}'"})

        if response:
            report = f'\tNew group creation                       - ExtId:        {add_spaces(group_externalId)} - Already exists'
            self.report.add(['console', 'groups'], report)
            return True
        return False



    def rdm_create_group(self, externalId: str, group_name: str):

        # Checks if the group already exists
        response = self._rdm_check_if_group_exists(externalId)
        if response:
            return True

        group_name = group_name.replace('(', '\(')
        group_name = group_name.replace(')', '\)')
        group_name = group_name.replace(' ', '_')
        command = f'pipenv run invenio roles create {externalId} -d {group_name}'
        response = os.system(command)

        report = f'\tNew group creation                       -'

        if response != 0:
            self.report.add(['console'], f'{report} Error: {response}')
            return False

        self.report.add(['console'], f'{report} Success')
        return True



    def _rdm_add_user_to_group(self, user_id: int, group_externalId: str, group_name: str):

        # Get user's rdm email
        user_email = self.rdm_db.select_query('email', 'accounts_user', {'id': user_id})[0][0]

        # Get group id
        response = self.rdm_db.select_query('id', 'accounts_role', {'name': f"'{group_externalId}'"})

        if not response:
            # If the group does not exist then creates it
            self.rdm_create_group(group_externalId, group_name)
            # Repeats the query to get the group id
            response = self.rdm_db.select_query('id', 'accounts_role', {'name': f"'{group_externalId}'"})

        group_id = response[0][0]

        # Checks if match already exists
        response = self.rdm_db.select_query('*', 'accounts_userrole', {'user_id': user_id, 'role_id': group_id})

        if response:
            report = f'\tRDM user in group  - User id: {add_spaces(user_id)}   -                     - Already belongs to group {group_externalId} (id {group_id})'
            self.report.add(['console'], report)
            return True

        # Adds user to group
        command = f'pipenv run invenio roles add {user_email} {group_externalId}'
        response = os.system(command)
        if response != 0:
            self.report.add(['console'], f'Warning - Creating group response: {response}')



    def _group_add_user(self, user_email, new_group_externalId, user_id):
        
        # Get group id
        group_id = self.rdm_db.select_query('id', 'accounts_role', {'name': f"'{new_group_externalId}'"})[0][0]
        
        # Check if the user is already in the group
        response = self.rdm_db.select_query('*', 'accounts_userrole', {'user_id': user_id, 'role_id': group_id})

        if response:
            return True

        command = f'pipenv run invenio roles add {user_email} {new_group_externalId}'
        response = os.system(command)

        report =  f'\tAdd user to group     - ExtId:     {add_spaces(new_group_externalId)} - User id:     {add_spaces(user_id)}' 
        if response != 0:
            self.report.add(['console', 'groups'], f'{report} - Error: {response}')
            return False

        self.report.add(['console', 'groups'], f'{report} - Success')
        return True



    def _group_remove_user(self, user_email, group_name):
        
        # Get user id
        user_id = self.rdm_db.select_query('id', 'accounts_user', {'email': f"'{user_email}'"})[0][0]
        
        # Get group id
        group_id = self.rdm_db.select_query('id', 'accounts_role', {'name': f"'{group_name}'"})[0][0]
        
        # Check if the user is already in the group
        response = self.rdm_db.select_query('*', 'accounts_userrole', {'user_id': user_id, 'role_id': group_id})

        report =  f'Remove user fromGroup - ExtId:     {add_spaces(group_name)} - User id:     {add_spaces(user_id)}'

        if not response:
            self.report.add(['console', 'groups'], f'\t{report} - Not in group (already removed)')
            return True

        # Remove user from old group
        command = f'pipenv run invenio roles remove {user_email} {group_name}'
        response = os.system(command)

        if response != 0:
            self.report.add(['console', 'groups'], f'\t{report} - Error: {response}')
            return False

        self.report.add(['console', 'groups'], f'\t{report} - Success')
        return True