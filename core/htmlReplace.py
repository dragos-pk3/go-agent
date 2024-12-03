import json


class HTMLReplacer:
    def __init__(self):
        self.config = self.load_config()
        self.template_path = self.config['OFFER_TEMPLATE_PATH']

    def load_config(self):
        with open('__userfiles__/user_config.json', 'r') as f:
            return json.load(f)

    def load_template(self):
        with open(self.template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def replace_placeholders(self, html_content, data):
        for key, value in data.items():
            placeholder = '{{' + key + '}}'
            html_content = html_content.replace(placeholder, str(value))
        return html_content

    def process_template(self, processed_data):
        docData = {
            'Autovan': str(processed_data['Autovan']),
            'Start Date': str(processed_data['Start Date']),
            'End Date': str(processed_data['End Date']),
            'Total Days': str(processed_data['Total Days']),
            'Location': str(processed_data['Location']),
            'Total Rent': str(int(processed_data['Total Rent'])),
            'Link to Photo': str(processed_data['Link to Photo'])
        }

        template_content = self.load_template()
        
        rates_html = []
        season_rates = processed_data.get('Rent Per Day', [])  # [standard, high, low]
        discount_rates = processed_data.get('Discount Rates', [])  # [standard, high, low]
        
        non_zero_seasons = sum(1 for rate in season_rates if rate != 0)

        if non_zero_seasons == 1:
            if season_rates[0] != 0:
                rates_html.append(f"Tarif standard de închiriere = <b>{int(season_rates[0])} euro / noapte </b>")
                if discount_rates[0] != 0:
                    rates_html.append(f"Tarif standard cu discount -10% = <b>{int(discount_rates[0])} euro / noapte </b>")
            elif season_rates[1] != 0:
                rates_html.append(f"Tarif standard de închiriere = <b>{int(season_rates[1])} euro / noapte </b>")
                if discount_rates[1] != 0:
                    rates_html.append(f"Tarif standard cu discount -10% = <b>{int(discount_rates[1])} euro / noapte </b>")
            elif season_rates[2] != 0:
                rates_html.append(f"Tarif standard de închiriere = <b>{int(season_rates[2])} euro / noapte </b>")
                if discount_rates[2] != 0:
                    rates_html.append(f"Tarif standard cu discount -10% = <b>{int(discount_rates[2])} euro / noapte </b>")
        else:
            # Standard season
            if season_rates[0] != 0:
                rates_html.append(f"Tarif sezon standard de închiriere = <b>{int(season_rates[0])} euro / noapte </b>")
                if discount_rates[0] != 0:
                    rates_html.append(f"Tarif sezon standard cu discount -10% = <b>{int(discount_rates[0])} euro / noapte </b>")

            # High season
            if season_rates[1] != 0:
                rates_html.append(f"Tarif sezon de vârf de închiriere = <b>{int(season_rates[1])} euro / noapte </b>")
                if discount_rates[1] != 0:
                    rates_html.append(f"Tarif sezon de vârf cu discount -10% = <b>{int(discount_rates[1])} euro / noapte </b>")

            # Low season
            if season_rates[2] != 0:
                rates_html.append(f"Tarif low season de închiriere = <b>{int(season_rates[2])} euro / noapte </b>")
                if discount_rates[2] != 0:
                    rates_html.append(f"Tarif low season cu discount -10% = <b>{int(discount_rates[2])} euro / noapte </b>")

        rates_section = "<br>\n    ".join(rates_html)
        
        template_content = template_content.replace(
            "{{Rent Per Day}}",
            rates_section
        )
        
        return self.replace_placeholders(template_content, docData)