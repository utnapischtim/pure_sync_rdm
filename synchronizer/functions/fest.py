import json

def test_f(dirpath):
    resp_json = open(dirpath + '/reports/resp_pure.json', 'r')
    resp_json = json.load(resp_json)

    for item in resp_json['items']:
        print(item)