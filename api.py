from flask import Flask, jsonify

app = Flask(__name__)


# Returns all cards that show up between 1-5 decks in all Rog Silas tournament Decks
def filter_decklists():
    result_dict = {}
    return result_dict


@app.route('/')
def home():
    data = filter_decklists()  # Store the GET request result
    if data:
        return data # Return the data as JSON
    else:
        return jsonify({'error': 'Failed to fetch data'}), 500
    
if __name__ == '__main__':
    app.run(debug=True)