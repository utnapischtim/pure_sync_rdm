
from setup import *
import requests

params = (('prettyprint', '1'),)
url = f'{rdm_api_url_records}?sort=mostrecent&size={10}&page={1}'
response = requests.get(url, params=params, verify=False)

print(response.content)