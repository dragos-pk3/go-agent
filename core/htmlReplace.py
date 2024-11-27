import json


class HTMLReplacer:
    def __init__(self):
        self.config = self.load_config()
        self.template_path = self.config['TEMPLATE_PATH']

    def load_config(self):
        with open('__userfiles__/user_config.json', 'r') as f:
            return json.load(f)

    def load_template(self):
        with open(self.template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def replace_placeholders(self, html_content, data):
        # Replace all placeholders in the HTML content
        for key, value in data.items():
            placeholder = '{{' + key + '}}'
            html_content = html_content.replace(placeholder, str(value))
        return html_content

    def process_template(self, processed_data):
        # Prepare data dictionary with proper keys matching template placeholders
        docData = {
            'Autovan': str(processed_data['Autovan']),
            'Start Date': str(processed_data['Start Date']),
            'End Date': str(processed_data['End Date']),
            'Total Days': str(processed_data['Total Days']),
            'Location': str(processed_data['Location']),
            'Rent Per Day': str(int(processed_data['Rent Per Day'])),
            'Total Rent': str(int(processed_data['Total Rent'])),
            'Link to Photo': str(processed_data['Link to Photo'])
        }

        # Load and process template
        template_content = self.load_template()
        return self.replace_placeholders(template_content, docData)