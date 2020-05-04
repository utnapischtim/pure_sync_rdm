import smtplib
import os
from datetime                       import datetime
from setup                          import log_files_name, email_receiver, temporary_files_name, \
    email_sender, email_sender_password, email_smtp_server, email_smtp_port, email_message
from source.general_functions       import current_time
from source.rdm.requests            import Requests
from source.reports                 import Reports

rdm_requests = Requests()
reports = Reports()

def rdm_add_file(shell_interface, file_name: str, recid: str, uuid: str):
    file_path_name = f"{temporary_files_name['base_path']}/{file_name}"

    # PUT FILE TO RDM
    response = rdm_requests.rdm_put_file(file_path_name, recid)

    # Report
    reports.add(['console'], f'\tRDM put file          - {response}')

    reports.add(['records'], f'{current_time()} - file_put_to_rdm - {response} - {recid}\n')

    if response.status_code >= 300:
        shell_interface.file_success = False
        reports.add(['console', 'records'], response.content)

    else:
        shell_interface.file_success = True

        # if the upload was successful then delete file from /reports/temporary_files
        os.remove(file_path_name) 

        # # Sends email to remove record from Pure
        # send_email(uuid, file_name)               # - # - SEND EMAIL - # - #

    return response


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