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
    return json_response

def find_client(rules):
    pattern = r"(context.+\')"

    for rule in rules:
        m = re.findall(pattern, rule['script'])
        if m:
            n = re.findall(r"'(.*?)'", m[0])
            rule['client_name'] = n[0]
        else:    
            rule['client_name'] = "none"
        try:
            del rule['script']
        except KeyError:
            print("Key not found")

    return rules

def generate_csv(final_data):
        data = StringIO()
        w = csv.writer(data)

        w.writerow(('id', 'enabled', 'name', 'order', 'stage', 'client_name'))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        for item in final_data:
            w.writerow((item['id'], item['enabled'], item['name'], item['order'], item['stage'], item['client_name']))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)