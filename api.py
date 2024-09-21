from flask import Flask, jsonify
import json
import requests

base_url = "https://edhtop16.com/api/"
mox_base_url = "https://api2.moxfield.com/"
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
dataMM = {'tournamentName': {'$regex': r'Mox Masters (January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}'}}

app = Flask(__name__)

data = {
    'commander': 'The First Sliver'
}
entries = json.loads(requests.post(base_url + 'req', json=data, headers=headers).text)

def fetch_all_commanders():
    response = requests.get(base_url + 'get_commanders')
    if response.status_code == 200:
        return response.json()  # Or response.text for plain text
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
    decks = entries[:5]
    for entry in decks:
        if 'moxfield.com/decks/' in entry['decklist']:
            deckId = entry['decklist'].split('decks/')[1]
            path = 'v3/decks/all/'
            moxReq =  requests.get(mox_base_url + path + deckId, json=dataMM, headers=headers).json()
            cardObject = moxReq['boards']['mainboard']['cards']
            allCardNames = collect_values(cardObject, "name")
            result.append(allCardNames)
    return result

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