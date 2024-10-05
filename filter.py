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

# Open the JSON file and load its data into a Python object
with open('./mocks/Talion, the Kindly Lord.json', 'r') as file:
    data = json.load(file)

filtered_data = filter_lists_by_length(data)
pretty_json = json.dumps(filtered_data, indent=4)
print(pretty_json)
write_to_json(filtered_data, './mocks/Filtered Talion, the Kindly Lord.json')