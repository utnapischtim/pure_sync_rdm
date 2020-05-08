import os
from setup                          import temporary_files_name
from source.rdm.requests            import Requests
from source.reports                 import Reports

requests = Requests()
reports = Reports()

def rdm_add_file(file_name: str, recid: str):
    file_path_name = f"{temporary_files_name['base_path']}/{file_name}"

    # PUT FILE TO RDM
    response = requests.rdm_put_file(file_path_name, recid)

    # Report
    reports.add(['console'], f'\tRDM put file          - {response}                       - {file_name}')

    if response.status_code >= 300:
        reports.add(['console'], response.content)
        return False

    else:
        # if the upload was successful then delete file from /reports/temporary_files
        os.remove(file_path_name) 
        return True