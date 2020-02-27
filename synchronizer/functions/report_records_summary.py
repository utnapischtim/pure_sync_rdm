from setup import *

def report_records_summary(my_prompt, process_type):

    current_datetime = my_prompt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if my_prompt.count_total == 0:
        report =  f'{process_type} - success\n'
        report += f"{current_datetime}\n"
        report += "Nothing to transmit\n"
    else:
        percent_success = my_prompt.count_successful_push_metadata * 100 / my_prompt.count_total

        if percent_success >= upload_percent_accept:
            report = f"\n{process_type} - success\n"
        else:
            report = f"\n{process_type} - error\n"

        report += f"{current_datetime}\n"

        report += f"Metadata:   ->  successful: {my_prompt.count_successful_push_metadata} - "
        report += f"errors: {my_prompt.count_errors_push_metadata}\n"
        report += f"File:       ->  successful: {my_prompt.count_successful_push_file} - "
        report += f"errors: {my_prompt.count_errors_put_file}"
        
        if process_type != 'Pages':
            report += f"\nDelete:     ->  successful: {my_prompt.count_successful_record_delete} - "
            report += f"errors: {my_prompt.count_errors_record_delete}"

    print(report)

    # RECORDS.LOG
    file_records = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_rdm-push-records.log'
    open(file_records, "a").write(report)

    # SUMMARY.LOG
    file_summary = f'{my_prompt.dirpath}/reports/{my_prompt.date.today()}_summary.log'
    open(file_summary, "a").write(report)

