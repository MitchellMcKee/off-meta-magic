import json

def filter_lists_by_length(input_dict):
    # Create a new dictionary to store the filtered data
    result_dict = {}
    
    # Iterate through each key and value in the input dictionary
    for key, value_list in input_dict.items():
        # Only keep lists with fewer than 6 items
        if len(value_list) < 6:
            result_dict[key] = value_list
    
    return result_dict

def write_to_json(data, filename):
    json_file_path = filename + '.json'
    with open(json_file_path, mode='w') as file:
        json.dump(data, file, indent=4)

def create_card_list(data):
    result = []
    all_image_links = get_all_image_links()
    for key, value_list in data.items():
        image_link = all_image_links[key]
        if isinstance(image_link, str):
            image_link = [image_link]
        total_entries = get_total_entries(key)
        new_card = {
            'id': len(result),
            'card': [key],
            'relatedItems': value_list,
            'imageLinks': image_link,
            'totalEntries': total_entries
        }
        result.append(new_card)
    
    return result

with open('./bulk/oracle-cards.json', 'r') as file:
    all_cards = json.load(file)

def get_all_image_links():
    result = {}
    for obj in all_cards:
        # Extract the name as the key and the 'normal' field from image_uris as the value
        if 'name' in obj and 'image_uris' in obj and 'border_crop' in obj['image_uris']:
            result[obj['name']] = obj['image_uris']['border_crop']
        else:
            try:
                result[obj['name']] = obj['card_faces'][0]['image_uris']['border_crop'], obj['card_faces'][1]['image_uris']['border_crop']
            except:
                print('Failed to retrieve image link for ' + obj['name'])

    return result



with open('./bulk/output.json', 'r') as file:
    all_decklists = json.load(file)

def get_total_entries(card_name):
    decklists = find_values_by_key(all_decklists, card_name)
    count = 0
    for deck in decklists:
        count += len(deck) 
    return count

# finds all values for a given key of 
def find_values_by_key(obj, key_name):
    values = []
    
    # Recursive function to find values by key
    def search_dict(d):
        for key, value in d.items():
            if key == key_name:
                values.append(value)
            if isinstance(value, dict):
                search_dict(value)  # Recursive call for nested dictionaries

    search_dict(obj)
    return values

# Open the JSON file and load its data into a Python object
with open('./mocks/Talion, the Kindly Lord.json', 'r') as file:
    data = json.load(file)

filtered_data = filter_lists_by_length(data)
card_object_list = create_card_list(filtered_data)
pretty_list = json.dumps(card_object_list, indent=4)
print(pretty_list)
write_to_json(card_object_list, './mocks/Talion, the Kindly Lord')
