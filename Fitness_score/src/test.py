import json
import requests
import datetime

if __name__ == "__main__":

    print("reading parameters...")
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    params = None

    with open('../data/input/parameters.json', 'r') as file:
        params = json.load(file)

    print("preparing pdb file...")
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    params["pdb"]["pdb_name"] = "4KW4.pdb"

    with open('4KW4.pdb', 'r') as file:
        params["pdb"]["pdb_content"] = file.read()

    print("fetching score...")
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    fetch_url = '/api-score/score'

    response = requests.post("http://localhost:5000/api-score/score", json = params)

    print(response.json().get('status'))
    if response.json().get('status') == 'error':
        print(response.json().get('message'))
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))