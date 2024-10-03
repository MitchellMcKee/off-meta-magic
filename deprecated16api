from flask import Flask, jsonify
from collections import Counter
import json
import requests

app = Flask(__name__)

base_url = "https://edhtop16.com/api/"
mox_base_url = "https://api2.moxfield.com/"
mox_path = "v3/decks/all/"
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
data = {
    'commander': 'Rograkh, Son of Rohgahh / Silas Renn, Seeker Adept',
    'tourney_filter': {
        'size': {'$gte': 1},
        'dateCreated': {'$gte': 1695774198} # September 1st 2022
    }
}

# Currently fetches all tournament Rog Silas Decks since 9/1/22
entries = json.loads(requests.post(base_url + 'req', json=data, headers=headers).text)

# Returns all cards that show up between 1-5 decks in all Rog Silas tournament Decks
def filter_decklists():
    result_dict = {}
    decks = entries[:15]

    # loop through decks for faster testing until data is cached on S3
    # loop through entries for all decks (Takes about 3m 42s to run) 
    for entry in decks:
        if 'moxfield.com/decks/' in entry['decklist']:
            deckId = entry['decklist'].split('decks/')[1]
            mox_req =  fetch_mox_list(deckId)
            if mox_req != None:
                mox_public_url = mox_req['publicUrl']
                card_object = mox_req['boards']['mainboard']['cards']
                all_card_names = collect_values(card_object, "name")
                result_dict[mox_public_url] = all_card_names
    result_dict = invert_dict_of_lists(result_dict)
    result_dict = {key: value for key, value in result_dict.items() if len(value) <= 5}
    return result_dict
    
def fetch_mox_list(deckId):
    response = requests.get(mox_base_url + mox_path + deckId)
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

def invert_dict_of_lists(input_dict):
    """
    Takes a dictionary with lists as values and returns a new dictionary.
    The keys in the new dictionary are the unique values from the lists,
    and the corresponding value is a list of keys from the original dictionary 
    that contained that unique value.
    
    Args:
        input_dict (dict): A dictionary where values are lists.

    Returns:
        dict: A dictionary where unique list values become keys, and values are lists of keys 
              from the original dictionary.
    """
    result = {}
    
    # Iterate through each key-value pair in the input dictionary
    for key, values_list in input_dict.items():
        for value in values_list:
            if value not in result:
                result[value] = [key]  # Create a new entry in result dict
            else:
                result[value].append(key)  # Append the key to the list
    
    return result

def fetch_all_commanders():
    response = requests.get(base_url + 'get_commanders')
    if response.status_code == 200:
        return response.json()  # Or response.text for plain text
    else:
        return None

@app.route('/')
def home():
    data = filter_decklists()  # Store the GET request result
    if data:
        return data # Return the data as JSON
    else:
        return jsonify({'error': 'Failed to fetch data'}), 500

@app.route('/commanders')
def commanders():
    data = fetch_all_commanders()  # Store the GET request result
    if data:
        return jsonify(data)  # Return the data as JSON
    else:
        return jsonify({'error': 'Failed to fetch data'}), 500

if __name__ == '__main__':
    app.run(debug=True)