import requests
from setup                      import token_rdm, rdm_records_url
from source.general_functions   import dirpath

class Requests:

    def rdm_request_headers(self, parameters):
        headers = {}
        if 'content_type' in parameters:
            headers['Content-Type'] = 'application/json'
        if 'file' in parameters:
            headers['Content-Type'] = 'application/octet-stream'
        if 'token' in parameters:
            headers['Authorization'] = f'Bearer {token_rdm}'
        return headers

    def rdm_request_params(self):
        return (('prettyprint', '1'),)


    def rdm_get_metadata(self, additional_parameters: str, recid = ''):

        headers = self.rdm_request_headers(['content_type', 'token'])
        params  = self.rdm_request_params()

        url = f'{rdm_records_url}{recid}'

        # Add parameters to url
        if len(additional_parameters) > 0:
            url += '?'
            for key in additional_parameters:
                url += f'{key}={additional_parameters[key]}&'
            # Remove last character
            url = url[:-1]

        # Sending request
        return requests.get(url, headers=headers, params=params, verify=False)


    def rdm_post_metadata(self, data: str):
        """ Used to create a new record """

        open(f'{dirpath}/data/temporary_files/rdm_post_metadata.json', "w").write(data)

        headers = self.rdm_request_headers(['content_type'])
        params  = self.rdm_request_params()

        data_utf8 = data.encode('utf-8')

        return requests.post(rdm_records_url, headers=headers, params=params, data=data_utf8, verify=False)


    def rdm_put_metadata(self, recid: str, data: str):
        """ Used to update an existing record """

        headers = self.rdm_request_headers(['content_type', 'token'])
        params  = self.rdm_request_params()

        data_utf8 = data.encode('utf-8')
        url = f'{rdm_records_url}{recid}'

        return requests.put(url, headers=headers, params=params, data=data_utf8, verify=False)


    def rdm_put_file(self, file_path_name: str, recid: str):

        headers = self.rdm_request_headers(['file', 'token'])
        data    = open(file_path_name, 'rb').read()

        # Get only the file name
        file_name = file_path_name.split('/')[-1]

        url = f'{rdm_records_url}{recid}/files/{file_name}'

        return requests.put(url, headers=headers, data=data, verify=False)


    def rdm_delete_metadata(self, recid: str):

        headers = self.rdm_request_headers(['content_type', 'token'])
        url = f'{rdm_records_url}{recid}'

        return requests.delete(url, headers=headers, verify=False)






# def rdm_request_headers(parameters):
#     headers = {}
#     if 'content_type' in parameters:
#         headers['Content-Type'] = 'application/json'
#     if 'file' in parameters:
#         headers['Content-Type'] = 'application/octet-stream'
#     if 'token' in parameters:
#         headers['Authorization'] = f'Bearer {token_rdm}'
#     return headers


# def rdm_request_params():
#     return (('prettyprint', '1'),)


# def rdm_get_metadata(additional_parameters: str, recid = ''):

#     headers = rdm_request_headers(['content_type', 'token'])
#     params  = rdm_request_params()

#     url = f'{rdm_records_url}{recid}'

#     # Add parameters to url
#     if len(additional_parameters) > 0:
#         url += '?'
#         for key in additional_parameters:
#             url += f'{key}={additional_parameters[key]}&'
#         # Remove last character
#         url = url[:-1]

#     # Sending request
#     return requests.get(url, headers=headers, params=params, verify=False)


# def rdm_post_metadata(data: str):
#     """ Used to create a new record """

#     open(f'{dirpath}/data/temporary_files/rdm_post_metadata.json', "w").write(data)

#     headers = rdm_request_headers(['content_type'])
#     params  = rdm_request_params()

#     data_utf8 = data.encode('utf-8')

#     return requests.post(rdm_records_url, headers=headers, params=params, data=data_utf8, verify=False)


# def rdm_put_metadata(recid: str, data: str):
#     """ Used to update an existing record """

#     headers = rdm_request_headers(['content_type', 'token'])
#     params  = rdm_request_params()

#     data_utf8 = data.encode('utf-8')
#     url = f'{rdm_records_url}{recid}'

#     return requests.put(url, headers=headers, params=params, data=data_utf8, verify=False)


# def rdm_put_file(file_path_name: str, recid: str):

#     headers = rdm_request_headers(['file', 'token'])
#     data    = open(file_path_name, 'rb').read()

#     # Get only the file name
#     file_name = file_path_name.split('/')[-1]

#     url = f'{rdm_records_url}{recid}/files/{file_name}'

#     return requests.put(url, headers=headers, data=data, verify=False)


# def rdm_delete_metadata(recid: str):

#     headers = rdm_request_headers(['content_type', 'token'])
#     url = f'{rdm_records_url}{recid}'

#     return requests.delete(url, headers=headers, verify=False)