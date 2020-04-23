from setup                              import pure_rest_api_url, upload_percent_accept
from functions.general_functions        import add_to_full_report, add_spaces, itinialize_counters, dirpath
from functions.rdm_general_functions    import rdm_get_recid
from functions.pure_general_functions   import pure_get_metadata
from functions.delete_record            import delete_record, delete_from_list
from functions.rdm_add_record           import RdmAddRecord
from datetime                           import date, datetime, timedelta
import json

# To execute preferably between 22:30 and 23:30

#       ---     ---     ---
def pure_get_changes():
    """ Gets from Pure API all changes that took place of a certain date
        and modifies accordingly the RDM repository """
    
    # Get date of last update
    missing_updates = get_missing_updates()
    # missing_updates = ['2020-04-22']      # TEMPORARY !!!!!
    
    if missing_updates == []:
        add_to_full_report('\nNothing to update.\n')
        return

    pure_changes_by_date = PureChangesByDate()

    for date_to_update in reversed(missing_updates):
        pure_changes_by_date.run_process(date_to_update)

    return


#       ---     ---     ---
def get_missing_updates():
    """ Search for missing updates in the last 7 days """

    file_name = f'{dirpath}/data/successful_changes.txt'

    missing_updates = []
    count = 0
    days_span = 7

    date_today = str(datetime.today().strftime('%Y-%m-%d'))
    date_check = datetime.strptime(date_today, "%Y-%m-%d").date()

    while count < days_span:

        if str(date_check) not in open(file_name, 'r').read():
            missing_updates.append(str(date_check))        

        date_check = date_check - timedelta(days=1)
        count += 1

    return missing_updates


class PureChangesByDate:

    def run_process(self, changes_date: str):

        # Initialize global counters
        self.global_counters = itinialize_counters()
        
        file_records = f'{dirpath}/reports/{date.today()}_records.log'
        file_changes = f'{dirpath}/reports/{date.today()}_changes.log'

        page = 'page=1'
        size = 'pageSize=100'

        # Get from pure all changes of a certain date
        url = f'{pure_rest_api_url}changes/{changes_date}?{size}&{page}'
        response = pure_get_metadata(url)

        if response.status_code >= 300:
            # add_to_full_report(response.content)
            return False

        # Load response json
        json_response = json.loads(response.content)

        # used to check if there are doubled tasks (e.g. update uuid and delete same uuid)
        self.duplicated_uuid  = []
        
        self.local_counters = {
            'count_delete': 0,
            'count_update': 0,
            'count_create': 0,
            'count_incomplete': 0,
            'count_duplicated': 0,
            'count_not_ResearchOutput': 0,
        }
        current_time = datetime.now().strftime("%H:%M:%S")

        report_intro = f"""

    --   --   --

    {current_time}
    Changes date: {changes_date}
    Number of items in response: {json_response["count"]}

    """
        # append to yyyy-mm-dd_records.log
        open(file_records, "a").write(report_intro)
        add_to_full_report(report_intro)

        #   ---     DELETE      ---
        # Iterates over all records that need to be deleted
        response = self.delete_records(json_response)

        #   ---     CREATE / ADD / UPDATE      ---
        self.create_add_update_records(json_response)

        # If there are no changes
        if self.global_counters['count_total'] == 0:
            open(file_changes, "a").write(f'{report_intro}Nothing to transfer.\n\n')
            return

        # Calculates if the process was successful
        percent_success = self.global_counters['count_successful_push_metadata'] * 100 / self.global_counters['count_total']
        data = f'{changes_date}\n'
        
        # If the percentage of successfully transmitted records is higher then the limit specified in setup.py
        # And changes_date is not in successful_changes.txt
        file_name = f'{dirpath}/data/successful_changes.txt'
        if (percent_success >= upload_percent_accept and data not in open(file_name, 'r').read()):
            
            file_success = f'{dirpath}/data/successful_changes.txt'
            open(file_success, "a").write(data)

        metadata_succs              = add_spaces(self.global_counters['count_successful_push_metadata'])
        metadata_error              = add_spaces(self.global_counters['count_errors_push_metadata'])
        file_succs                  = add_spaces(self.global_counters['count_successful_push_file'])
        file_error                  = add_spaces(self.global_counters['count_errors_put_file'])
        delete_succs                = add_spaces(self.global_counters['count_successful_record_delete'])
        delete_error                = add_spaces(self.global_counters['count_errors_record_delete'])
        count_delete                = add_spaces(self.local_counters['count_delete'])
        count_update                = add_spaces(self.local_counters['count_update'])
        count_create                = add_spaces(self.local_counters['count_create'])
        # Incomplete:  when the uuid or changeType are not specified
        count_incomplete            = add_spaces(self.local_counters['count_incomplete'])
        # Duplicated:  e.g. when a record has been modified twice in a day        
        count_duplicated            = add_spaces(self.local_counters['count_duplicated'])
        # Irrelevant:  when familySystemName is not ResearchOutput
        count_not_ResearchOutput    = add_spaces(self.local_counters['count_not_ResearchOutput'])

        report = f"""
    Metadata         ->  successful: {metadata_succs} - errors:   {metadata_error}
    File             ->  successful: {file_succs} - errors:   {file_error}
    Delete           ->  successful: {delete_succs} - errors:   {delete_error}

    Pure changes:
    Update:     {count_update} - Create:     {count_create} - Delete:    {count_delete}
    Incomplete: {count_incomplete} - Duplicated: {count_duplicated} - Irrelevant:{count_not_ResearchOutput}
        """
        add_to_full_report(report)

        # RECORDS.LOG
        open(file_records, "a").write(report)
        
        # CHANGES.LOG
        open(file_changes, "a").write(report_intro + report)
        return


    #       ---     ---     ---
    def delete_records(self, json_response: dict):

        for item in json_response['items']:

            if 'changeType' not in item or 'uuid' not in item:
                continue
            elif item['familySystemName'] != 'ResearchOutput':
                continue
            elif item['changeType'] != 'DELETE':
                continue

            uuid = item['uuid']
            self.duplicated_uuid.append(uuid)   
            self.local_counters['count_delete'] += 1

            report = f"\n{self.local_counters['count_delete']} - {item['changeType']}"
            add_to_full_report(report)
      
            # Gets the record recid
            recid = rdm_get_recid(uuid)

            if recid:
                # Deletes the record from RDM
                delete_record(recid)
            else:
                # The record is not in RDM
                self.global_counters['count_successful_record_delete'] += 1

        return True


    def create_add_update_records(self, json_response):

        rdm_add_record = RdmAddRecord()
        
        count = 0
        for item in json_response['items']:
            
            if 'changeType' not in item or 'uuid' not in item:
                self.local_counters['count_incomplete'] += 1
                continue
            elif item['familySystemName'] != 'ResearchOutput':
                self.local_counters['count_not_ResearchOutput'] += 1
                continue
            elif item['changeType'] == 'DELETE':
                continue

            uuid = item['uuid']
            if uuid in self.duplicated_uuid:
                self.local_counters['count_duplicated'] += 1
                continue
            
            count += 1
            report = f"\n{count} - {item['changeType']} - {uuid}"
            add_to_full_report(report)

            if item['changeType'] == 'ADD' or item['changeType'] == 'CREATE':
                self.local_counters['count_create'] += 1

            if item['changeType'] == 'UPDATE':
                self.local_counters['count_update'] += 1
            
            # Checks if this uuid has already been created / updated / deleted
            self.duplicated_uuid.append(uuid)

            #   ---       ---       ---
            rdm_add_record.rdm_push_record_by_uuid(self.global_counters, uuid)
            #   ---       ---       ---

