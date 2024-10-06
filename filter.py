import json
import os

def filter_lists_by_length(input_dict, limit):
    result_dict = {}
    
    for key, value_list in input_dict.items():
        if len(value_list) < limit:
            result_dict[key] = value_list
    
    return result_dict

def write_to_json(data, filename):
    json_file_path = filename + '.json'
    with open(json_file_path, mode='w') as file:
        json.dump(data, file, indent=4)

def create_card_list(data):
    result = []
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

def get_all_image_links(image_type):
    result = {}
    for obj in all_cards:
        # Check if Card has 2 faces
        if 'name' in obj and 'image_uris' in obj and image_type in obj['image_uris']:
            result[obj['name']] = obj['image_uris'][image_type]
        else:
            try:
                result[obj['name']] = obj['card_faces'][0]['image_uris'][image_type], obj['card_faces'][1]['image_uris'][image_type]
            except:
                print('Failed to retrieve image link for ' + obj['name'])

    return result

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

with open('./bulk/oracle-cards.json', 'r') as file:
    all_cards = json.load(file)
with open('./bulk/output.json', 'r') as file:
    all_decklists = json.load(file)

all_image_links = get_all_image_links('border_crop')
all_art_links = get_all_image_links('art_crop')

dircetory_path = './mocks/raw'
filenames = []
try:
    names = os.listdir(dircetory_path)
    filenames = names
except:
    print(f"'{dircetory_path}' does not exist")

commander_names = []
for file in filenames:
    with open(f"./mocks/raw/{file}", 'r') as file:
        data = json.load(file)
    count = max(len(value) for value in data.values())
    filtered_data = filter_lists_by_length(data, 6)
    card_object_list = create_card_list(filtered_data)
    
    # print the data in a readable format in the console 
    # pretty_list = json.dumps(card_object_list, indent=4)
    # print(pretty_list)

    # remove file path and json extension from the name
    name_of_file = file.name[12:].split('.json')[0]
    #write_to_json(card_object_list, f"./mocks/{name_of_file}")
    print(name_of_file)
    print(count)
    commander_with_count = {
        'name': name_of_file,
        'count': count,
        'related': filter_lists_by_length(data, 2)
    }
    commander_names.append(commander_with_count)

result = []

for commander in commander_names:
    cmdr = commander['name']
    if '+' in cmdr:
        partners = cmdr.split('+')
        image_link = [all_art_links[partners[0]], all_art_links[partners[1]]]
    else:
        image_link = all_art_links[cmdr]
    
    if isinstance(image_link, str):
        image_link = [image_link]

    total_entries = commander['count']
    related_dict = commander['related']
    related_items = []
    for related_card in related_dict.keys():
        related_items.append(related_card)
    
    new_card = {
        'id': len(result),
        'card': [cmdr],
        'relatedItems': related_items,
        'imageLinks': image_link,
        'totalEntries': total_entries
    }
    result.append(new_card)

pretty_result = json.dumps(result, indent=4)
print(pretty_result)
write_to_json(result, f"./mocks/commanders")