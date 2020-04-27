import os
from datetime       import date

dirpath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))

def add_spaces(value: str):
    max_length = 5                              # 5 is the maximum length of the given value
    spaces = max_length - len(str(value))
    return ''.ljust(spaces) + str(value)        # ljust -> adds spaces after a string



def add_to_full_report(report: str):
    file_records = f'{dirpath}/reports/{date.today()}_records_full.log'
    open(file_records, "a").write(f'{report}\n')
    print(report)


def initialize_counters():
    """ Initialize variables that will count through the whole task the success of each process """
    global_counters = {
        'total': 0,
        'errors_push_metadata': 0,
        'errors_put_file': 0,
        'errors_record_delete': 0,
        'successful_push_metadata': 0,
        'successful_push_file': 0,
        'successful_record_delete': 0,
        'abstracts': 0,
        'orcids': 0,
        'http_responses': {}
    }
    return global_counters