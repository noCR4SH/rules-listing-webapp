import re
import csv
import requests


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

def generate_csv(dict_data, filename):
    csv_columns = ['id', 'enabled', 'name', 'order', 'stage', 'client_name']

    print("Generating CSV file...")

    with open(filename, 'w') as f:
        w = csv.DictWriter(f, fieldnames=csv_columns)
        w.writeheader()
        for data in dict_data:
            w.writerow(data)

    print("Done!")