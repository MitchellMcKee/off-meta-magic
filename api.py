from flask import Flask, jsonify
import requests
import json
from typing import Union, Dict, Any

app = Flask(__name__)

topdeck_base_url = "https://topdeck.gg/api"
topdeck_auth_header = {
    'Authorization': '27d14d9f-b081-44d8-8dfc-2c9ff9384712'
}
topdeck_req_body = {
    'last': 180,
    "columns": ["decklist", "wins", "draws", "losses"],
    'game': 'Magic: The Gathering',
    'format': 'EDH',
    "participantMin": 16
}

moxfield_base_url = "https://api2.moxfield.com/"
mox_path = "v3/decks/all/"

class CardAndCommander:
    def __init__(self, card_name: str, commanders: list[str], moxfield_deck_id: str):
        self.card_name = card_name
        self.commanders = commanders
        self.moxfield_deck_id = moxfield_deck_id

    def __repr__(self):
        return f"Deck(commanders={self.commanders}, cardName='{self.card_name}', moxfieldDeckId='{self.moxfield_deck_id}')"

def fetch_topdeck_lists() -> Union[None, Dict[str, Any]]:
    response = requests.post(topdeck_base_url + '/v2/tournaments', json=topdeck_req_body, headers=topdeck_auth_header)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def fetch_moxfield_list(deckId) ->  Union[None, Dict[str, Any]]:
    response = requests.get(moxfield_base_url + mox_path + deckId)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
# Collects all values of a specified key
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

# finds all values for a given key of 
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
        commanders = moxfield_list['boards']['commanders']['cards']
        commander_card_names = find_values_by_key(commanders, "name")
        # standardize order of partners (alphabetically)
        commander_card_names = sorted(commander_card_names)
        mainboard = moxfield_list['boards']['mainboard']['cards']
        mainboard_card_names = find_values_by_key(mainboard, "name")  
        if len(mainboard_card_names) != 0:
            for card in mainboard_card_names:
                commander_obj = CardAndCommander(card, commander_card_names, id)
                result.append(commander_obj)
    return result

def map_commanders_to_cards(data: list[CardAndCommander]) -> Dict:
    result = {}
    for entry in data:
        # Get the card name and moxfield deck id from the entry
        card_name = entry.card_name
        moxfield_deck_id = entry.moxfield_deck_id
        
        # Use the commander directly as a key
        commander_arr = entry.commanders
        commander = ''
        if(len(commander_arr) > 1):
            commander = "+".join(commander_arr)
        else:
            try:
                commander = commander_arr[0]
            except:
                commander = 'error'
                print('error')
                print(entry)
        
        # If the commander is not in the result, initialize with an empty list
        if commander not in result and len(commander) != 0:
            result[commander] = []
        
        # Append the tuple (cardName, moxfieldDeckId) to the list for this commander
        result[commander].append((card_name, moxfield_deck_id))
        
    return result

def get_unique_second_values(tuples_list):
    result = {}
    print(tuples_list)
    for first_value, second_value in tuples_list:
        if first_value not in result:
            result[first_value] = set()
        result[first_value].add(second_value)

    for key in result:
        result[key] = list(result[key])
    return result

def write_to_json(data, filename):
    json_file_path = filename + '.json'
    with open(json_file_path, mode='w') as file:
        json.dump(data, file, indent=4)

# Returns all instances of cards used in cEDH
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

        print('map cmdrs')
        print(moxfield_lists[:3])
        commander_list = map_commanders_to_cards(moxfield_lists)
        result = {}
        for commander_object in commander_list.items():
            print(commander_object)
            result[commander_object[0]] = get_unique_second_values(commander_object[1])
            # split clause is to handle flip commanders with '//' in their name
            commander_filename = "./output/" + commander_object[0].split(' /')[0]
            write_to_json(result[commander_object[0]], commander_filename)
             
        write_to_json(result, './output/output')
        return result
    else:
        return jsonify({'error': 'Failed to fetch data'}), 500

# -------------------------------------------------------------

# Returns the source of truth
@app.route('/top')
def commanders():
    data = fetch_topdeck_lists()
    return data


if __name__ == '__main__':
    app.run(debug=True)