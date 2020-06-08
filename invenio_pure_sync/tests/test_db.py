import yaml

data = yaml.safe_load(open("docker-services.yml", 'r'))
db_data = data['services']['db']['environment']

credentials = {}

for i in db_data:
    
    key   = i.split('=')[0]
    value = i.split('=')[1]

    if key == 'POSTGRES_USER':
        credentials['user'] = value
    elif key == 'POSTGRES_PASSWORD':
        credentials['psw'] = value
    elif key == 'POSTGRES_DB':
        credentials['db'] = value

print(credentials)