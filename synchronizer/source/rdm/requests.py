import requests
from setup                      import token_rdm, rdm_records_url, temporary_files_name

class Requests:

    def __rdm_request_headers(self, parameters):
        headers = {}
        if 'content_type' in parameters:
            headers['Content-Type'] = 'application/json'
        if 'file' in parameters:
            headers['Content-Type'] = 'application/octet-stream'
        if 'token' in parameters:
            headers['Authorization'] = f'Bearer {token_rdm}'
        return headers

    def __rdm_request_params(self):
        return (('prettyprint', '1'),)


    def rdm_get_metadata(self, additional_parameters: str, recid = ''):

        headers = self.__rdm_request_headers(['content_type', 'token'])
        params  = self.__rdm_request_params()

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

        return response


    def rdm_post_metadata(self, data: str):
        """ Used to create a new record """

        open(temporary_files_name['post_rdm_metadata'], "w").write(data)

        headers = self.__rdm_request_headers(['content_type'])
        params  = self.__rdm_request_params()

        data_utf8 = data.encode('utf-8')

        return requests.post(rdm_records_url, headers=headers, params=params, data=data_utf8, verify=False)


    def rdm_put_metadata(self, recid: str, data: str):
        """ Used to update an existing record """

        headers = self.__rdm_request_headers(['content_type', 'token'])
        params  = self.__rdm_request_params()

        data_utf8 = data.encode('utf-8')
        url = f'{rdm_records_url}{recid}'

        return requests.put(url, headers=headers, params=params, data=data_utf8, verify=False)


    def rdm_put_file(self, file_path_name: str, recid: str):

        headers = self.__rdm_request_headers(['file', 'token'])
        data    = open(file_path_name, 'rb').read()

        # Get only the file name
        file_name = file_path_name.split('/')[-1]

        url = f'{rdm_records_url}{recid}/files/{file_name}'

        return requests.put(url, headers=headers, data=data, verify=False)


    def rdm_delete_metadata(self, recid: str):

        headers = self.__rdm_request_headers(['content_type', 'token'])
        url = f'{rdm_records_url}{recid}'

        return requests.delete(url, headers=headers, verify=False)
