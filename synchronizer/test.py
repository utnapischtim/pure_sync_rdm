from cmd import Cmd
import requests
import json
import os
import time
from datetime import date, datetime, timedelta
from setup import *
dirpath = os.path.dirname(os.path.abspath(__file__))


params = (('prettyprint', '1'),)

pag = 1
pag_size = 10

response = requests.get(
    f'https://localhost:5000/api/records/hv6c9-cvp92', 
    params=params, 
    verify=False
    )
print(response)
open(dirpath + "/reports/resp_rdm.json", 'wb').write(response.content)
