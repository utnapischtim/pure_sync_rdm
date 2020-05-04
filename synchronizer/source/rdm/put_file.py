import smtplib
import os
from datetime                       import datetime
from source.general_functions       import dirpath
from setup                          import log_files_name, email_receiver, \
    email_sender, email_sender_password, email_smtp_server, email_smtp_port, email_message
                                                
from source.rdm.requests            import Requests
from source.reports                 import Reports

rdm_requests = Requests()
reports = Reports()


def rdm_add_file(shell_interface, file_name: str, recid: str, uuid: str):
    
    file_path_name = f'{dirpath}/data/temporary_files/{file_name}'

    # PUT FILE TO RDM
    response = rdm_requests.rdm_put_file(file_path_name, recid)

    # Report
    reports.add(['console'], f'\tRDM put file          - {response}')

    current_time = datetime.now().strftime("%H:%M:%S")
    report = f'{current_time} - file_put_to_rdm - {response} - {recid}\n'

    if response.status_code >= 300:
        shell_interface.file_success = False

        report += f'{response.content}\n'
        reports.add(['console'], response.content)

    else:
        shell_interface.file_success = True

        # if the upload was successful then delete file from /reports/temporary_files
        os.remove(file_path_name) 

        # # Sends email to remove record from Pure
        # send_email(uuid, file_name)               # - # - SEND EMAIL - # - #

    open(log_files_name['records'], "a").write(report)

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