

# GET ----------------------------
headers = {
    'Authorization': f'Bearer {token_rdm}',
    'Content-Type': 'application/json',
}
params = (('prettyprint', '1'),)
url = f'{rdm_api_url_records}api/records/?{sort}&{query}&{size}&{page}'
response = shell_interface.requests.get(url, headers=headers, params=params, verify=False)
# ---------------------------
headers = {
    'Authorization': f'Bearer {token_rdm}',
    'Content-Type': 'application/json',
}
params = (('prettyprint', '1'),)
url = f'{rdm_api_url_records}api/records/{recid}'
response = shell_interface.requests.get(url, headers=headers, params=params, verify=False)
# ---------------------------
headers = {
    'Authorization': f'Bearer {token_rdm}',
    'Content-Type': 'application/json',
}
params = (('prettyprint', '1'),)
url = f'{rdm_api_url_records}api/records/?{sort}&{query}&{size}&{page}'
response = shell_interface.requests.get(url, headers=headers, params=params, verify=False)
# ---------------------------
headers = {
    'Authorization': f'Bearer {token_rdm}',
    'Content-Type': 'application/json',
}
params = (('prettyprint', '1'),)
url = f'{rdm_api_url_records}api/records/?sort=mostrecent&size={pag_size}&page={pag}'
response = shell_interface.requests.get(url, headers=headers, params=params, verify=False)
# ---------------------------
headers = {
'Accept': 'application/json',
}
params = (
    ('apiKey', pure_api_key),
)
url = f'{pure_rest_api_url}/persons/{person_uuid}'
response = shell_interface.requests.get(url, headers=headers, params=params)
# ---------------------------
headers = {
    'Accept': 'application/json',
    'api-key': pure_api_key,
}
params = (
    ('apiKey', pure_api_key),
)
url = f'{pure_rest_api_url}research-outputs/{uuid}'
response = shell_interface.requests.get(url, headers=headers, params=params)
# ---------------------------
headers = {
    'Accept': 'application/json',
}
params = (
    ('page', '1'),
    ('pageSize', '5000'),
    ('apiKey', pure_api_key),
)
url = f'{pure_rest_api_url}changes/{changes_date}'
response = shell_interface.requests.get(url, headers=headers, params=params)
# ---------------------------
headers = {
    'Accept': 'application/json',
}
params = (
    ('page', '1'),
    ('pageSize', '1'),
    ('apiKey', pure_api_key),
)
url = f'{pure_rest_api_url}organisational-units/{externalId}/research-outputs'
response = shell_interface.requests.get(url, headers=headers, params=params)
# ---------------------------
headers = {
    'Accept': 'application/json',
}
params = (
    ('apiKey', pure_api_key),
    ('page', page),
    ('pageSize', page_size),
)
url = f'{pure_rest_api_url}persons/{user_uuid}/research-outputs'
response = shell_interface.requests.get(url, headers=headers, params=params)
# ---------------------------
headers = {
    'Accept': 'application/json',
}
params = (
    ('q', f'"{key_value}"'),
    ('apiKey', pure_api_key),
    ('pageSize', page_size),
    ('page', page),
)
url = f'{pure_rest_api_url}persons'
response = shell_interface.requests.get(url, headers=headers, params=params)
# ---------------------------
headers = {
    'Accept': 'application/json',
    'api-key': pure_api_key,
}
params = (
    ('page', pag),
    ('pageSize', pag_size),
    ('apiKey', pure_api_key),
)
url = f'{pure_rest_api_url}research-outputs'
response = shell_interface.requests.get(url, headers=headers, params=params)


















# PUT ----------------------------
headers = {
    'Authorization': f'Bearer {token_rdm}',
    'Content-Type': 'application/json',
}
params = (
    ('prettyprint', '1'),
)
url = f'{rdm_api_url_records}api/records/{recid}'
response = shell_interface.requests.put(url, headers=headers, params=params, data=data_utf8, verify=False)


# PUT FILE ---------------------------
headers = {
    'Authorization': f'Bearer {token_rdm}',
    'Content-Type': 'application/octet-stream',
}
data = open(file_path_name, 'rb').read()
url = f'{rdm_api_url_records}api/records/{recid}/files/{file_name}'
response = shell_interface.requests.put(url, headers=headers, data=data, verify=False)


# POST----------------------------
data_utf8 = shell_interface.data.encode('utf-8')
headers = {
    'Content-Type': 'application/json',
}
params = (
    ('prettyprint', '1'),
)
url = f'{rdm_api_url_records}api/records/'
response = shell_interface.requests.post(url, headers=headers, params=params, data=data_utf8, verify=False)
# ---------------------------
# ---------------------------
# ---------------------------