from setup import *

def report_records_summary(my_prompt, process_type):

    date_today = str(my_prompt.date.today())
    file_summary = f'{my_prompt.dirpath}/reports/{date_today}_summary.log'
    file_records = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_rdm-push-records.log'
    
    print('\n---------------------')

    current_datetime = my_prompt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if my_prompt.count_total == 0:
        report =  f'\n{process_type} - success\n'
        report += f"{current_datetime}\n"
        report += "Nothing to transmit\n"
    else:
        percent_success = my_prompt.count_successful_push_metadata * 100 / my_prompt.count_total

        if percent_success >= upload_percent_accept:
            report = f"\n{process_type} - success\n"
        else:
            report = f"\n{process_type} - error\n"

        report += f"{current_datetime}\n"

        report += f"Total records:\t\t\t\t{my_prompt.count_total}\n"
        report += f"Successful push metadata:\t{my_prompt.count_successful_push_metadata}\n"
        report += f"Errors push metadata:\t\t{my_prompt.count_errors_push_metadata}\n"
        report += f"Successful put file: \t\t{my_prompt.count_successful_push_file}\n"
        report += f"Error put file:\t\t\t\t{my_prompt.count_errors_put_file}\n"
        report += f"Uuid not found in pure: \t{my_prompt.count_uuid_not_found_in_pure}\n"


    # Adds report to yyyy-mm-dd_summary.log
    open(file_summary, "a").write(report)
    print(report)

    # Adding count http respons to report records
    report_records = 'RDM HTTP response codes:\n'
    for key in my_prompt.count_http_response_codes:
        report_records += f'{str(key)}: {str(my_prompt.count_http_response_codes[key])},\n'
    open(file_records, "a").write(report_records)

