from flask import Flask, jsonify
import requests
import json
import csv

app = Flask(__name__)

topdeck_base_url = "https://topdeck.gg/api"
topdeck_auth_header = {
    'Authorization': '27d14d9f-b081-44d8-8dfc-2c9ff9384712'
}
topdeck_req_body = {
    'last': 5,
    "columns": ["decklist", "wins", "draws", "losses"],
    'game': 'Magic: The Gathering',
    'format': 'EDH',
    "participantMin": 24,
    "participantMax": 24
}

moxfield_base_url = "https://api2.moxfield.com/"
mox_path = "v3/decks/all/"

def fetch_topdeck_lists():
    response = requests.post(topdeck_base_url + '/v2/tournaments', json=topdeck_req_body, headers=topdeck_auth_header)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def fetch_moxfield_list(deckId):
    response = requests.get(moxfield_base_url + mox_path + deckId)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
# Function to collect all values of a specified key
def collect_values(data, key_to_find):
    values = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key_to_find:
                values.append(v)
            values.extend(collect_values(v, key_to_find))
    elif isinstance(data, list):
        for item in data:
            values.extend(collect_values(item, key_to_find))
    return values

def find_values_by_key(obj, target_key):
    values = []
    
    # Recursive function to find values by key
    def search_dict(d):
        for key, value in d.items():
            if key == target_key:
                values.append(value)
            if isinstance(value, dict):
                search_dict(value)  # Recursive call for nested dictionaries

    search_dict(obj)
    return values

# Filter out empty strings, None values, and strings containing 'undefined'
def clean_list(input_list):
    return [s for s in input_list if s and s != None and 'undefined' not in s.lower()]

def get_extract_ids_from_url(url):
    split_url = url.split('/decks/')
    if len(split_url) > 1 and 'moxfield.com/decks/' in url.lower():
        return split_url[1]
    else:
        return ''

def extract_moxfield_info(moxfield_list, id):
    result = []
    if moxfield_list != None:
        mox_public_url = moxfield_list['publicUrl']
        commanders = moxfield_list['boards']['commanders']['cards']
        commander_card_names = find_values_by_key(commanders, "name")
        mainboard = moxfield_list['boards']['mainboard']['cards']
        mainboard_card_names = find_values_by_key(mainboard, "name")
        
        if len(mainboard_card_names) != 0:
            for card in mainboard_card_names:
                cardObj = {
                    'commanders': commander_card_names,
                    'cardName': card,
                    'moxfieldDeckId': id
                }
                result.append(cardObj)

    return result

def write_to_json_and_csv(data):
    # Specify the JSON file name
    json_file = "output.json"

    # Write data to the JSON file
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4) 

    # Specify the CSV file name
    csv_file = "output.csv"

    # Get the fieldnames (keys) from the first dictionary in the list
    fieldnames = data[0].keys()

    # Write the JSON data to a CSV file
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


@app.route('/')
def home():
    print('fetching top deck...')
    data = fetch_topdeck_lists()
    if data:
        print('topdeck response success')
        all_decklists = collect_values(data, 'decklist')
        clean_decklists = clean_list(all_decklists)
        extract_ids = list(map(get_extract_ids_from_url, clean_decklists))
        moxfield_lists = []
        for index, id in enumerate(extract_ids):
            moxfield_response = fetch_moxfield_list(id)
            extract = extract_moxfield_info(moxfield_response, id)
            if extract:
                moxfield_lists.extend(extract)
                print(index)
                print(len(extract_ids))
                write_to_json_and_csv(moxfield_lists)

        return moxfield_lists
    else:
        return jsonify({'error': 'Failed to fetch data'}), 500

# -------------------------------------------------------------

@app.route('/top')
def commanders():
    data = fetch_topdeck_lists()  # Store the GET request result
    return data


if __name__ == '__main__':
    app.run(debug=True)