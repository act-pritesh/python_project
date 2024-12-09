import os
from datetime import datetime

import pandas as pd
import requests
from parsel import Selector
import re

cookies = {
    'AWSALB': '+53KWbbnG/gUD6IzeqRUNkNDdmBbl8tco+GdB9uRV/jbdDYUGqtzPFvyHS7yz4LovYyrrNfXWgisU0lbfvifOEf7preumoBWngTkmBKwQaBpxn17KNMZvO33UlvI',
    'AWSALBCORS': '+53KWbbnG/gUD6IzeqRUNkNDdmBbl8tco+GdB9uRV/jbdDYUGqtzPFvyHS7yz4LovYyrrNfXWgisU0lbfvifOEf7preumoBWngTkmBKwQaBpxn17KNMZvO33UlvI',
    'XSRF-TOKEN': 'eyJpdiI6IlNQTnh6eGJNak90aGQ0NjlcL2lRbUJBPT0iLCJ2YWx1ZSI6Ik05bSt2MVhzSGJlY2pVRjNRajJoR0FYK2g5Q2lFXC9SWWNSaE5XTDBzTk1DaGY1ZHB2bTYxZ25jbTZwc3FuUXJnIiwibWFjIjoiMjZkMmUwNGM2NmY3OTE5YmYyNDkyMzI0M2Y4YmU0YjgxOWFhODMyNmY1ZjY5OTA4YjkyZDllNzJlZGM1ZDhjYSJ9',
    'laravel_session': 'eyJpdiI6Impid0FjaTN2RlRrVlA1Q1ZFc1YyOXc9PSIsInZhbHVlIjoicW1JeHA0R2hHS1lkKzFJdER2XC9nNzZcLyt0V0pjdmd0eXdMY3ZBa0RIRktqbzVzakJpa0Q2NFF4XC9va0NlRHZ5ZiIsIm1hYyI6ImMwYzJhZjFjNmQ5ZDc1MTg5Y2ViZTAyMGMxNjFjN2NkOWExODg5MTY4ZWEzYzg5MTIyN2Y1OThjOWJmZjk5NmQifQ%3D%3D',
    '_ga': 'GA1.2.5781860.1729247969',
    '_gid': 'GA1.2.31449640.1729247969',
    'popup': 'Y',
    '_ga_NHP0ZDVJGY': 'GS1.1.1729247968.1.1.1729248078.60.0.0',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
}

response = requests.get('https://www.bma.bm/warning-list', cookies=cookies, headers=headers)

selector = Selector(str(response.text.replace('<br>', '').replace('<br />', ' ')))

# Clean up the header values (remove tags, trim spaces, handle newlines)
column_names = [h.replace("\r", "").replace("\t", "").replace("\n", "").replace(" ", "_").lower().strip() for h in selector.xpath("//div[contains(@class, 'col-sm-12')]//th//text()").getall()]

# Find the rows dynamically
rows = selector.xpath("//div[contains(@class, 'col-sm-12')]//tr")[1:]

# List to store each row as a dictionary
table_data = []

def remove_extra_space(row_data):
    # Remove 'x000D' and replace it with a space
    value = re.sub(r'x000D', ' ', row_data)
    # Remove any extra spaces or newlines created by this replacement
    value = re.sub(r'\s+', ' ', value).strip()
    # Update the cleaned value back in row_data
    return value

def remove_specific_punctuation(text):
    punctuation_marks = [
        ".", ",", "?", "!", ":", "\n", "\t", ";", "—", "-", "'", '"', "(", ")", "[", "]", "{", "}", "…", "\\", "@", "&", "*",
        "_", "^", "~","`","/"
    ]
    if text=='N/A':
        return text
    else:
        for char in punctuation_marks:
            text = str(text).replace(char, '')
        return text

def create_output_folder(folder_name="output"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


# Iterate through each row and map it to the column headers
data = []
url = 'https://www.bma.bm/warning-list'  # Define the base URL outside the loop

for row in rows:
    row_data = {}
    row_data['url'] = url
    # Loop through each cell in the row
    for i, cell in enumerate(row.xpath("td")):
        cell_text = remove_extra_space(
            cell.xpath("string()").get().strip().replace("-", "").replace("\n", " ").replace("\t", "").replace("\r",
                                                                                                               "")).strip()
        try:
            cell_text = datetime.strptime(cell_text, '%d %B %Y').strftime('%Y-%m-%d')
        except:
            pass
        if 'company_or_person' in column_names[i]:
            cell_text = remove_specific_punctuation(cell_text)
        row_data[column_names[i]] = cell_text

        # Handle anchor tag (links) if present
        link = cell.xpath(".//a/@href").get()
        if link:
            row_data[f"{column_names[i]}_url"] = link  # Store the link if available

    # Add the URL to the row_data


    # Append the row_data to the data list
    data.append(row_data)

output_folder = "output"
create_output_folder(output_folder)

# Save the data to Excel inside the created folder
output_file = os.path.join(output_folder, "bma_bm.xlsx")
df = pd.DataFrame(data)
df = df.replace('', 'N/A').replace('None', 'N/A')
df.fillna('N/A', inplace=True)
df.to_excel(output_file, index=False)

print(f"Data successfully written to {output_file}")