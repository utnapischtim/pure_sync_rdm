from setup                              import dirpath
from datetime                           import date


#   ---         ---         ---
def add_spaces(value: str):
    max_length = 5                              # 5 is the maximum length of the given value
    spaces = max_length - len(str(value))
    return ''.ljust(spaces) + str(value)        # ljust -> adds spaces after a string


#   ---         ---         ---
def initialize_count_variables(shell_interface):
    """ Initialize variables that will be used in report_records_summary method """

    shell_interface.count_total                       = 0
    shell_interface.count_errors_push_metadata        = 0
    shell_interface.count_errors_put_file             = 0
    shell_interface.count_errors_record_delete        = 0
    shell_interface.count_successful_push_metadata    = 0
    shell_interface.count_successful_push_file        = 0
    shell_interface.count_successful_record_delete    = 0
    shell_interface.count_abstracts                   = 0
    shell_interface.count_orcids                      = 0


#   ---         ---         ---
def add_to_full_report(report: str):
    file_records = f'{dirpath}/reports/{date.today()}_records_full.log'
    open(file_records, "a").write(f'{report}\n')
    print(report)

