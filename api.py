from flask import Flask, jsonify
from collections import Counter
import json
import requests

base_url = "https://edhtop16.com/api/"
mox_base_url = "https://api2.moxfield.com/"
mox_path = "v3/decks/all/"
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

app = Flask(__name__)

data = {
    'commander': 'Rograkh, Son of Rohgahh / Silas Renn, Seeker Adept',
    'tourney_filter': {
        'size': {'$gte': 1},
        'dateCreated': {'$gte': 1695774198} # September 1st 2022
    }
}
entries = json.loads(requests.post(base_url + 'req', json=data, headers=headers).text)

def fetch_all_commanders():
    response = requests.get(base_url + 'get_commanders')
    if response.status_code == 200:
        return response.json()  # Or response.text for plain text
    else:
        return None
    
def fetch_moxfield_list(deckId):
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

def fetch_all_decklists():
    result = []
    decks = entries[:10]
    for entry in decks:
        if 'moxfield.com/decks/' in entry['decklist']:
            deckId = entry['decklist'].split('decks/')[1]
            mox_req =  fetch_moxfield_list(deckId)
            if mox_req != None:
                card_object = mox_req['boards']['mainboard']['cards']
                all_card_names = collect_values(card_object, "name")
                result.append(all_card_names)
    result = count_unique_items_in_lists(result)
    result = {item: count for item, count in result.items() if count < 5}
    
    return result

def count_unique_items_in_lists(list_of_lists):
    # Combine all lists into a single list
    combined_list = [item for sublist in list_of_lists for item in sublist]
    
    # Count occurrences of each unique item
    item_counts = Counter(combined_list)
    
    return dict(item_counts)

@app.route('/')
def home():
    data = fetch_all_decklists()  # Store the GET request result
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