import requests
import os
dirpath = os.path.dirname(os.path.abspath(__file__))


def file_transfer(file_name, url, record_id):
    try:
        file_path = dirpath + '/tmp_files/'

        # # - DOWNLOAD FROM PURE -
        # resp = requests.get(url)
        # print('DL: ', resp)
        # open(file_path + file_name, 'wb').write(resp.content)

        # - PUSH TO RDM -
        headers = {
            'Content-Type': 'application/octet-stream',
        }
        data = open(file_path + file_name, 'rb').read()
        response = requests.put('https://127.0.0.1:5000/api/records/' + record_id + '/files/' + file_name, headers=headers, data=data, verify=False)
        print('RDM: ', response)

        # DELETE FILE
        # os.remove(file_path + file_name) 
    except:
        print('\n- Error in file_transfer method -\n')



# url = "https://pure01.tugraz.at/ws/files/2487733/From_Smart_Health_to_Smart_Hospitals_2015.pdf"
# filename = "From_Smart_Health_to_Smart_Hospitals_2015.pdf"

url = 'https://i.ytimg.com/vi/wizWVFJWYrE/maxresdefault.jpg'
filename = 'img3.jpg'
record_id = 'ss3ye-gtk36'

file_transfer(filename, url, record_id)