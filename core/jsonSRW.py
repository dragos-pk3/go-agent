import json

def save_to_json(strings, output_file):
    data = {string.strip(): "placeholder_text" for string in strings}
    
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def write_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
