import requests
import time
from setup                          import token_rdm, rdm_records_url, temporary_files_name, wait_429
from source.reports                 import Reports

class Requests:
    
    def __init__(self):
        self.report = Reports()

    def _request_headers(self, parameters: list):
        headers = {}
        if 'content_type' in parameters:
            headers['Content-Type'] = 'application/json'
        if 'file' in parameters:
            headers['Content-Type'] = 'application/octet-stream'
        if 'token' in parameters:
            headers['Authorization'] = f'Bearer {token_rdm}'
        return headers

    def _request_params(self):
        return (('prettyprint', '1'),)


    def rdm_get_metadata(self, additional_parameters: str, recid = ''):

        headers = self._request_headers(['content_type', 'token'])
        params  = self._request_params()

        url = f'{rdm_records_url}{recid}'

        # Add parameters to url
        if len(additional_parameters) > 0:
            url += '?'
            for key in additional_parameters:
                url += f'{key}={additional_parameters[key]}&'
            # Remove last character
            url = url[:-1]

        # Sending request
        response = requests.get(url, headers=headers, params=params, verify=False)
        open(temporary_files_name['get_rdm_metadata'], "wb").write(response.content)

        self._check_response(response)
        return response


    def rdm_post_metadata(self, data: str):
        """ Used to create a new record """

        open(temporary_files_name['post_rdm_metadata'], "w").write(data)

        headers = self._request_headers(['content_type'])
        params  = self._request_params()

        data_utf8 = data.encode('utf-8')
        
        response = requests.post(rdm_records_url, headers=headers, params=params, data=data_utf8, verify=False)

        self._check_response(response)
        return response


    def rdm_put_metadata(self, recid: str, data: str):
        """ Used to update an existing record """

        headers = self._request_headers(['content_type', 'token'])
        params  = self._request_params()

        data_utf8 = data.encode('utf-8')
        url = f'{rdm_records_url}{recid}'

        response = requests.put(url, headers=headers, params=params, data=data_utf8, verify=False)

        self._check_response(response)
        return response


    def rdm_put_file(self, file_path_name: str, recid: str):

        headers = self._request_headers(['file', 'token'])
        data    = open(file_path_name, 'rb').read()

        # Get only the file name
        file_name = file_path_name.split('/')[-1]

        url = f'{rdm_records_url}{recid}/files/{file_name}'

        return requests.put(url, headers=headers, data=data, verify=False)


    def rdm_delete_metadata(self, recid: str):

        headers = self._request_headers(['content_type', 'token'])
        url = f'{rdm_records_url}{recid}'

        response = requests.delete(url, headers=headers, verify=False)

        self._check_response(response)
        return response

    
    def _check_response(self, response):
        http_code = response.status_code
        if http_code >= 300 and http_code != 429:
            self.report.add(['console'], response.content)
            return False

        # Checks if too many requests are submitted to RDM (more then 5000 / hour)
        if response.status_code == 429:
            report = f'{response.content}\nToo many RDM requests.. wait {wait_429 / 60} minutes\n'
            self.report.add(['console'], report)
            time.sleep(wait_429)
            return False
        return True


    def get_rdm_metadata_by_query(self, query_value: str):
        """ Query RDM record metadata """

        params = {'sort': 'mostrecent', 'size': 250, 'page': 1, 'q': f'"{query_value}"'}
        response = self.rdm_get_metadata(params)

        self._check_response(response)
        return response


    def get_metadata_by_recid(self, recid: str):
        """ Having the record recid gets from RDM its metadata """

        if len(recid) != 11:
            report = f'\nERROR - The recid must have 11 characters. Given: {recid}\n'
            self.report.add(['console'], report)
            return False

        # RDM request
        response = self.rdm_get_metadata({}, recid)
        
        self._check_response(response)
        return response