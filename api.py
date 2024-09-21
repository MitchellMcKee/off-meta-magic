from flask import Flask
import json
import requests

base_url = "https://edhtop16.com/api/"
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

app = Flask(__name__)

data = {
    'standing': {'$lte': 16}, 
    'commander': 'Rograkh, Son of Rohgahh / Silas Renn, Seeker Adept',
    'tourney_filter': {
        'size': {'$gte': 64}
    }
}
entries = json.loads(requests.post(base_url + 'req', json=data, headers=headers).text)
commanders = json.loads(requests.get(base_url + 'get_commanders', headers=headers).text)

@app.route('/')
def home():
    return entries

@app.route('/commanders')
def commanders():
    return json.loads(requests.get(base_url + 'get_commanders', headers=headers).text)

if __name__ == '__main__':
    app.run(debug=True)