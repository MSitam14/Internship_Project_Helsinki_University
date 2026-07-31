import json
import requests
import datetime

if __name__ == "__main__":

    request_params = {
        "params": {},
        "pdb1": {"name": "", "content": ""},
        "pdb2": {"name": "", "content": ""}
    }

    print("reading parameters...")
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    with open('../config/parameters.json', 'r') as file:
        request_params["params"] = json.load(file)

    print("preparing pdb file...")
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    with open('../data/input/structures_comparison/4KW4.pdb', 'r') as file:
        request_params["pdb1"]["name"] = "4KW4.pdb"
        request_params["pdb1"]["content"] = file.read()

    with open('../data/input/structures_comparison/9w1t.pdb', 'r') as file:
        request_params["pdb2"]["name"] = "9w1t.pdb"
        request_params["pdb2"]["content"] = file.read()
         

    print("fetching comparison...")
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    response = requests.post("http://localhost:5000/api-hot-comp/comparison", json = request_params)

    print(response.json().get('status'))

    if response.json().get('status') == 'error':
        print(response.json().get('message'))
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))