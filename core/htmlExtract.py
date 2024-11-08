import re
import json

def extract_braced_strings(html_content):
    # Find all unique occurrences of strings between {{ and }}
    pattern = r"\{\{(.*?)\}\}"
    matches = re.findall(pattern, html_content, re.DOTALL)
    unique_strings = list(set(matches))  # Remove duplicates
    return unique_strings
    
def clean_string(string):
    # Replace \n<span id="..."></span> with a single whitespace
    cleaned_string = re.sub(r"\n<span id=\".*?\"></span>", " ", string)
    return cleaned_string.strip()  # Strip extra whitespace

def save_to_json(strings, output_file):
    # Clean each string and save it with placeholder values
    data = {clean_string(string): "placeholder_text" for string in strings}
    
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

def main(input_html, output_json):
    # Read HTML file content
    with open(input_html, 'r') as file:
        html_content = file.read()
    
    # Extract unique strings between {{ }}
    strings = extract_braced_strings(html_content)
    print(strings)
    # Save extracted strings to JSON
    save_to_json(strings, output_json)
    print(f"Extracted strings saved to {output_json}")

# Example usage
input_html = 'emailTemplateBrackets.htm'  # Replace with your input HTML file
output_json = 'output.json'   # Replace with desired output JSON file name
main(input_html, output_json)
