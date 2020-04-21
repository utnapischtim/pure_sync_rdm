from setup                              import dirpath, rdm_api_url_records, pure_username, pure_password, \
                                                email_receiver, email_sender, email_sender_password, \
                                                email_smtp_server, email_smtp_port, email_subject, email_message
from requests.auth                      import HTTPBasicAuth
from functions.general_functions        import add_to_full_report
from functions.rdm_general_functions    import rdm_put_file

from datetime                           import date, datetime
import requests
import smtplib
import os


#   ---     ---     ---
def rdm_add_file(shell_interface, file_name: str, recid: str, uuid: str):
    
    file_path_name = f'{dirpath}/data/temporary_files/{file_name}'
    url = f'{rdm_api_url_records}api/records/{recid}/files/{file_name}'

    # PUT FILE TO RDM
    response = rdm_put_file(url, file_path_name)

    # Report
    add_to_full_report(f'\tRDM put file          - {response}')

    current_time = datetime.now().strftime("%H:%M:%S")
    report = f'{current_time} - file_put_to_rdm - {response} - {recid}\n'

    if response.status_code >= 300:

        shell_interface.count_errors_put_file += 1
        shell_interface.file_success = False

        report += f'{response.content}\n'
        add_to_full_report(response.content)

    else:
        shell_interface.count_successful_push_file += 1
        shell_interface.file_success = True

        # if the upload was successful then delete file from /reports/temporary_files
        os.remove(file_path_name) 

        # # Sends email to remove record from Pure
        # send_email(uuid, file_name)               # - # - SEND EMAIL - # - #

    file_records = f'{dirpath}/reports/{date.today()}_records.log'
    open(file_records, "a").write(report)

    return response.status_code



#   ---     ---     ---
def get_file_from_pure(shell_interface, electronic_version: str):

    file_name = electronic_version['file']['fileName']
    file_url  = electronic_version['file']['fileURL']

    # Get request to Pure
    response = requests.get(file_url, auth=HTTPBasicAuth(pure_username, pure_password))

    # If the file is not in RDM
    if len(shell_interface.pure_rdm_file_match) == 0:
        match_review = 'File not in RDM    '

    # If the file in pure is different from the one in RDM
    elif shell_interface.pure_rdm_file_match[0] == False:
        match_review = 'Match: F, Review: -'

    # If the file is the same, checks if the one in RDM has been reviewed by internal stuff
    else:
        match_review = 'Match: T, Review: F'
        if shell_interface.pure_rdm_file_match[1]:
            match_review = 'Match: T, Review: T'
    
    report = f'\tPure get file         - {response} - {match_review} - {file_name}'
    add_to_full_report(report)
    
    if response.status_code < 300:
        # Save file
        open(f'{dirpath}/data/temporary_files/{file_name}', 'wb').write(response.content)

        shell_interface.record_files.append(file_name)

        # ISSUE encountered when putting txt files
        file_extension = file_name.split('.')[file_name.count('.')]
        if file_extension == 'txt':
            report = '\n\tATTENTION, the file extension is txt - \tKnown issue -> jinja2.exceptions.UndefinedError: No first item, sequence was empty.\n'
            add_to_full_report(report)

    else:
        add_to_full_report(f'Error downloading file from pure ({file_url})')

    # shell_interface.time.sleep(0.2)
    return


#   ---     ---     ---
def send_email(uuid: str, file_name: str):
    
    # creates SMTP session 
    s = smtplib.SMTP(email_smtp_server, email_smtp_port) 

    # start TLS for security 
    s.starttls() 

    # Authentication 
    s.login(email_sender, email_sender_password) 

    # sending the mail
    message = email_message.format(uuid, file_name)
    s.sendmail(email_sender, email_receiver, message) 
    
    # terminating the session 
    s.quit() 
    return