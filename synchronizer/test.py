from setup import *
import requests
import json
    	
pag = 1
pag_size = 50

count = 0
go_on = True

while go_on == True:

	# REQUEST to RDM
	headers = {
        'Authorization': f'Bearer {token_rdm}',
        'Content-Type': 'application/json',
    }
	params = (('prettyprint', '1'),)
	url = f'{rdm_api_url_records}api/records/?sort=mostrecent&size={pag_size}&page={pag}'

	response = requests.get(url, headers=headers, params=params, verify=False)
	print(f'\n{response}\n')

	open(f"{dirpath}/data/temporary_files/resp_rdm.json", 'wb').write(response.content)

	if response.status_code >= 300:
		print(response.content)
		break

	else:
		resp_json = json.loads(response.content)

		for i in resp_json['hits']['hits']:
			count += 1
			uuid = i['metadata']['uuid']
			recid = i['metadata']['recid']
			print(f'{uuid} - {recid}')

		print(f'\nPag {str(pag)} - Records {count}')

	if 'next' not in resp_json['links']:
		go_on = False
	
	pag += 1