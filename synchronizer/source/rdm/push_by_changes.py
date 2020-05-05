import json
from datetime                       import date, datetime, timedelta
from setup                          import pure_rest_api_url, upload_percent_accept, data_files_name
from source.general_functions       import add_spaces, initialize_counters, current_time
from source.pure.general_functions  import get_pure_metadata
from source.rdm.general_functions   import get_recid
from source.rdm.delete_record       import delete_record, delete_from_list
from source.rdm.add_record          import RdmAddRecord
from source.reports                 import Reports

# To execute preferably between 22:30 and 23:30, so to get all changes from that day

class PureChangesByDate:

    def __init__(self):
        self.report = Reports()
        

    def get_pure_changes(self):
        """ Gets from Pure API all changes that took place of a certain date
            and modifies accordingly the RDM repository """
        
        # Get date of last update
        missing_updates = self._get_missing_updates()
        missing_updates = ['2020-05-05']      # TEMPORARY !!!!!
        
        if missing_updates == []:
            self.report.add(['console'], '\nNothing to update.\n')
            return

        for date_to_update in reversed(missing_updates):
            self._changes_by_date(date_to_update)
        return


    def _decorator(func):
        def _wrapper(self, changes_date) :

            # Initialize global counters
            self.global_counters = initialize_counters()

            self.all_report_files = ['console', 'records', 'changes']
            
            self.report.add_template(self.all_report_files, ['general', 'title'], ['CHANGES', current_time()])
            self.report.add(self.all_report_files, f'\nProcessed date: {changes_date}\n')

            # Decorated function
            func(self, changes_date)

            self._report_summary()
        return _wrapper

    @_decorator
    def _changes_by_date(self, changes_date: str):

        # Get from pure all changes of a certain date
        response = get_pure_metadata('changes', changes_date, {'pageSize': 1000, 'page': 1})

        if response.status_code >= 300:
            self.report.add(['console', 'changes'], response.content)
            return False

        # Load response json
        json_response = json.loads(response.content)

        number_records = json_response["count"]
        report_line = f'Pure get changes      - {response} - Number of items: {add_spaces(number_records)}'
        self.report.add(self.all_report_files, report_line)

        # If there are no changes
        if number_records == 0:
            self.report.add(self.all_report_files, f'\n\nNothing to transfer.\n\n')
            return

        # used to check if there are doubled tasks (e.g. update uuid and delete same uuid)
        self.duplicated_uuid  = []
        
        self._initialize_local_counters()

        # Iterates over all records that need to be deleted
        self._delete_records(json_response)

        # - Create / Add / Update -
        self._update_records(json_response)

        # If the process was successful adds the date to successful_changes.txt
        self._add_date_to_successful_changes_file(changes_date)

    
    #       ---     ---     ---
    def _initialize_local_counters(self):
        self.local_counters = {
            'delete': 0,
            'update': 0,
            'create': 0,
            'incomplete': 0,
            'duplicated': 0,
            'not_ResearchOutput': 0,
        }
    
    #       ---     ---     ---
    def _add_date_to_successful_changes_file(self, changes_date):
    
        # Calculates if the process was successful
        percent_success = self.global_counters['metadata']['success'] * 100 / self.global_counters['total']
        data = f'{changes_date}\n'
        
        # If the percentage of successfully transmitted records is higher then the limit specified in setup.py
        # And changes_date is not in successful_changes.txt
        file_name = data_files_name['successful_changes']
        if (percent_success >= upload_percent_accept and data not in open(file_name, 'r').read()):
            
            file_success = data_files_name['successful_changes']
            open(file_success, "a").write(data)


    #       ---     ---     ---
    def _delete_records(self, json_response: dict):

        for item in json_response['items']:

            if 'changeType' not in item or 'uuid' not in item:
                continue
            elif item['familySystemName'] != 'ResearchOutput':
                continue
            elif item['changeType'] != 'DELETE':
                continue

            uuid = item['uuid']
            self.duplicated_uuid.append(uuid)   
            self.local_counters['delete'] += 1

            report = f"\n{self.local_counters['delete']} - {item['changeType']}"
            self.report.add(['console'], report)
      
            # Gets the record recid
            recid = get_recid(uuid)

            if recid:
                # Deletes the record from RDM
                delete_record(recid)
            else:
                # The record is not in RDM
                self.global_counters['delete']['success'] += 1
        return True


    #       ---     ---     ---
    def _update_records(self, json_response):

        rdm_add_record = RdmAddRecord()
        
        for item in json_response['items']:
            
            if 'changeType' not in item or 'uuid' not in item:
                self.local_counters['incomplete'] += 1
                continue
            elif item['familySystemName'] != 'ResearchOutput':
                self.local_counters['not_ResearchOutput'] += 1
                continue
            elif item['changeType'] == 'DELETE':
                continue

            uuid = item['uuid']
            if uuid in self.duplicated_uuid:
                self.local_counters['duplicated'] += 1
                continue
            
            self.report.add(['console'], f"\n{item['changeType']}")

            if item['changeType'] == 'ADD' or item['changeType'] == 'CREATE':
                self.local_counters['create'] += 1

            if item['changeType'] == 'UPDATE':
                self.local_counters['update'] += 1
            
            # Checks if this uuid has already been created / updated / deleted
            self.duplicated_uuid.append(uuid)

            # Adds record to RDM
            rdm_add_record.push_record_by_uuid(self.global_counters, uuid)


    #       ---     ---     ---
    def _get_missing_updates(self):
        """ Search for missing updates in the last 7 days """

        file_name = data_files_name['successful_changes']

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


    def _report_summary(self):

        # Global counters
        self.report.summary_global_counters(self.all_report_files, self.global_counters)

        # Local counters
        # Incomplete:  when the uuid or changeType are not specified
        # Duplicated:  e.g. when a record has been modified twice in a day  
        # Irrelevant:  when familySystemName is not ResearchOutput

        arguments = []
        arguments.append(add_spaces(self.local_counters['update']))
        arguments.append(add_spaces(self.local_counters['create']))
        arguments.append(add_spaces(self.local_counters['delete']))
        arguments.append(add_spaces(self.local_counters['incomplete']))
        arguments.append(add_spaces(self.local_counters['duplicated']))
        arguments.append(add_spaces(self.local_counters['not_ResearchOutput']))

        self.report.add_template(self.all_report_files, ['changes', 'summary'], arguments)

        return