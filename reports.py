import re
import csv
import requests
from io import StringIO


def get_token(client_id, client_secret, audience, domain):
    print("Requesting bearer token...")

    headers = { 'content-type': "application/json" }
    data = { 'client_id': client_id, 'client_secret': client_secret, 'audience': audience, "grant_type": "client_credentials" }
    
    response = requests.post("https://" + domain + "/oauth/token", json=data, headers=headers)
    
    json_response = response.json()

    return json_response

def get_rules(access_token, audience):
    print("Getting rules...")

    headers = { 'authorization': access_token["token_type"] + " " + access_token["access_token"] }

    response = requests.get(audience + "rules", headers=headers)

    json_response = response.json()

    for rule in json_response:
        cleaned_script = re.sub(r"[^\w]", " ",  rule['script']).split()
        rule['cleaned_script'] = cleaned_script

    return json_response

def get_clients(access_token, audience):
    print("Gettings clients....")

    headers = { 'authorization': access_token["token_type"] + " " + access_token["access_token"] }

    response = requests.get(audience + "clients?fields=client_id%2Cname&include_fields=true", headers=headers)

    json_response = response.json()
    return json_response

def find_client(rules, clients):
    print('Comparing data...')
    for client in clients:
        for rule in rules:
            if client['name'] in rule['cleaned_script'] or client['client_id'] in rule['cleaned_script']:
                rule['client_name'] = client['name']
                rule['client_id'] = client['client_id']
            else:
                rule['client_name'] = "none"
                rule['client_id'] = "none"

    for i in rules:
        try:
            del i['script']
            del i['cleaned_script']
        except KeyError:
            print("Key not found")
    print('OK!')
    return rules

def generate_csv(final_data):
        data = StringIO()
        w = csv.writer(data)

        w.writerow(('id', 'enabled', 'name', 'order', 'stage', 'client_name', 'client_id'))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        for item in final_data:
            w.writerow((item['id'], item['enabled'], item['name'], item['order'], item['stage'], item['client_name'], item['client_id']))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)