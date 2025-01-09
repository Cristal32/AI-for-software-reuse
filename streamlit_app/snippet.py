import json

def load_snippets(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_snippets(file_path, snippets):
    with open(file_path, 'w') as file:
        json.dump(snippets, file, indent=4)
