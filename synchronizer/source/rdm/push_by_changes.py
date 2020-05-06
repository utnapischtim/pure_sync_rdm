import json
from datetime                       import date, datetime, timedelta
from setup                          import upload_percent_accept, data_files_name
from source.general_functions       import add_spaces, initialize_counters, current_time
from source.pure.general_functions  import get_pure_metadata, get_next_page
from source.rdm.general_functions   import get_recid
from source.rdm.add_record          import RdmAddRecord
from source.reports                 import Reports
from source.rdm.delete_record       import Delete

# To execute preferably between 22:30 and 23:30, so to get all changes from that day

class PureChangesByDate:

    def __init__(self):
        self.add_record = RdmAddRecord()
        self.report = Reports()
        self.delete = Delete()
        

    def get_pure_changes(self):
        """ Gets from Pure 'changes' endpoint all records that have been created / updated / deleted 
            and modifies accordingly the relative RDM records """
        
        # Get date of last update
        missing_updates = self._get_missing_updates()
        missing_updates = ['2020-01-05']      # TEMPORARY !!!!!
        
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

            self.all_report_files = ['console', 'changes']
            
            self.report.add_template(self.all_report_files, ['general', 'title'], ['CHANGES', current_time()])
            self.report.add(self.all_report_files, f'\nProcessed date: {changes_date}')

            # Decorated function
            func(self, changes_date)

            self._report_summary()
        return _wrapper

    @_decorator
    def _changes_by_date(self, changes_date: str):
        """ Gets from Pure all changes that took place in a certain date """

        reference = changes_date
        count = 0

        while reference:
            count += 1
            # Get from pure all changes of a certain date
            response = get_pure_metadata('changes', reference, {})

            if response.status_code >= 300:
                self.report.add(['console', 'changes'], response.content)
                return False

            # Load response json
            json_response = json.loads(response.content)

            number_records = json_response["count"]
            report_line = f'\nPag{add_spaces(count)} - Pure get changes   - {response} - Number of items: {add_spaces(number_records)}'
            self.report.add(self.all_report_files, report_line)

            # Gets the reference code of the next page
            reference = get_next_page(json_response).split('/')[-1]

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

        # Adds the date to successful_changes.txt
        open(data_files_name['successful_changes'], "a").write(f'{changes_date}\n')

    
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
    def _delete_records(self, json_response: dict):
        """ Iterates over the Pure response and process all records that need to be deleted """

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
                self.delete.record(recid)
            else:
                # The record is not in RDM
                self.global_counters['delete']['success'] += 1
        return True


    #       ---     ---     ---
    def _update_records(self, json_response):
        """ Iterates over the Pure response and process all records that need to be created/updated """
        
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
            
            self.report.add(['console'], f"\n\tChange type           - {item['changeType']}")

            if item['changeType'] == 'ADD' or item['changeType'] == 'CREATE':
                self.local_counters['create'] += 1

            if item['changeType'] == 'UPDATE':
                self.local_counters['update'] += 1
            
            # Checks if this uuid has already been created / updated / deleted
            self.duplicated_uuid.append(uuid)

            # Adds record to RDM
            self.add_record.push_record_by_uuid(self.global_counters, uuid)



    def _get_missing_updates(self):
        """ Reading successful_changes.txt gets the dates in 
            which Pure changes have not been processed """

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