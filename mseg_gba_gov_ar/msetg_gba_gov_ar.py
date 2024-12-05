import locale
import os
import re
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import unicodedata
from deep_translator import GoogleTranslator  # More stable translator library
from datetime import datetime
from re import findall
from urllib.parse import urljoin, quote
import requests
from parsel import Selector
import pandas as pd

data_lock=Lock()
# Helper functions
def replace_spaces_only(url):
    return url.replace(" ", "%20")


def convert_dates_to_yy_mm_dd(date_list):
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, 'es_ES')

    if not isinstance(date_list, list):
        raise TypeError("Input must be a list of strings or tuples")

    month_name_corrections = {'setiembre': 'septiembre'}
    converted_dates = []

    for date_entry in date_list:
        date_str = date_entry[0] if isinstance(date_entry, tuple) else date_entry

        if not date_str:
            converted_dates.append(None)
            continue

        for incorrect_month, correct_month in month_name_corrections.items():
            if incorrect_month in date_str:
                date_str = date_str.replace(incorrect_month, correct_month)

        date_str = " ".join(date_str.split())
        formats = [
            "%d de %B de %Y", "%d %B de %Y", "%d de %B del año %Y",
            "%Y", "%d de %B %Y", "%d %B %Y"
        ]

        date_obj = None
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue

        if date_obj:
            converted_dates.append(date_obj.strftime("%Y-%m-%d"))
        else:
            print(f"Error processing date '{date_entry}': Unsupported format")
            converted_dates.append(None)

    return converted_dates


def remove_specific_punctuation(text):
    # Normalize the text to remove accents
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    # Decode any non-standard Unicode sequences
    text = text.encode('latin1', 'ignore').decode('utf-8', 'ignore')
    # List of punctuation marks to remove
    punctuation_marks = [
        ".", ",", "?", "!", ":", ";", "—", "-", "'", '"', "(", ")", "[", "]", "{", "}", "…", "\\", "@", "&", "*",
        "_", "^", "~", "`", "/", "", "", "\x89", "","'"
    ]
    # Remove specified punctuation marks
    for char in punctuation_marks:
        text = text.replace(char, '')
    return text


def page_data(response, url, encoded_url, data_list):
    parsed_data = Selector(text=response.text)
    name = parsed_data.xpath('//div[@class="row  d-flex align-items-stretch"]//h2/text()').get()
    final_name = remove_specific_punctuation(name)

    translated_name = GoogleTranslator(source='auto', target='en').translate(final_name) if final_name else "N/A"

    data = parsed_data.xpath(
        '//div[@class="row  d-flex align-items-stretch"]//p[@class="text-justify"]//text()').getall()
    full_data = ''.join(data)
    try:
        cleaned_text = full_data.encode('latin1', errors='ignore').decode('utf-8', errors='ignore')
    except (UnicodeEncodeError, UnicodeDecodeError):
        cleaned_text = full_data
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

    translated_case_summary = GoogleTranslator(source='auto', target='en').translate(cleaned_text) if cleaned_text else "N/A"

    dni_patterns = [
        r"DNI\s*N[º°]?\s*([\d.]+)",
        r"D\.N\.I\.\s*N[º°]?\s*([\d.]+)",
        r"D\.N\.I\.\s*([\d.]+)",
        r"D\.N\.I\. ([\d.]+)",
        r"DNI ([\d.]+)"
    ]

    dni_number = []
    for pattern in dni_patterns:
        match = re.findall(pattern, cleaned_text)
        if match:
            dni_number = match
            break

    birth_date_patterns = [
        r"nacido el (\d{1,2} de \w+ de \d{4})",
        r"nacido el (\d{1,2} \w+ de \d{4})",
        r"nacido en (\d+)",
        r"nacido el día (\d{1,2} de \w+ del año \d{4})",
        r"nacido el (\d{1,2} de \w+ \d{4})",
        r"nacido el día ([\d de \w+ de \d]+)",
        r"nacido en Rojas el (\d{1,2} de \w+ \d{4})",
    ]

    birth_date = []
    for pattern in birth_date_patterns:
        match = re.findall(pattern, cleaned_text)
        if match:
            birth_date = match
            break

    converted_date = convert_dates_to_yy_mm_dd(birth_date)
    reward_amount = findall("\([\$ \d,.]+\)", cleaned_text)
    final_reward = '|'.join(reward_amount).replace("(", '').replace(')', '')
    print(translated_name)
    with data_lock:
        data_list.append({
            "url": url,
            "name": translated_name,
            "alias_name": "N/A",
            "data_url": encoded_url,
            "dni_number": dni_number[0] if dni_number else "N/A",
            "date_of_birth": converted_date[0] if converted_date else "N/A",
            "parentage": "N/A",
            "address": "N/A",
            "reason": "N/A",
            "case_summary": translated_case_summary,
            "reward_amount": final_reward ,
            "complexion": "N/A",
            "height": "N/A",
            "hair_color": "N/A",
            "additional_information": "N/A"
        })


def page_link(response, header, url, data_list):
    parsed_data = Selector(response.text)
    all_links = parsed_data.xpath('//table/tbody/tr/td/a')

    def process_link(data):
        href = data.xpath('./@href').get()
        if href:
            href = href.replace("", '').replace("", '').replace("Ã", 'Á')
            fullhref = urljoin("https://www.mseg.gba.gov.ar/areas/recompensas/", href)
            final = replace_spaces_only(fullhref)
            replace_url = final.replace("MARTÁN", "MARTÍN").replace("VÁCTOR", "VÍCTOR").replace("MATÁAS",
                                                                                                "MATÍAS").replace(
                "AGUSTÁN", "AGUSTÍN").replace("NÁSTOR", "NÉSTOR")
            encoded_url = quote(replace_url, safe=":/%20")
            response = requests.get(encoded_url, headers=header)
            page_data(response, url, encoded_url, data_list)

    # Using ThreadPoolExecutor for concurrent execution
    with ThreadPoolExecutor() as executor:
        executor.map(process_link, all_links)

def create_output_folder(folder_name="output"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def main():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }
    url = 'https://www.mseg.gba.gov.ar/areas/recompensas/profugos.html'
    response = requests.get(url, headers=headers)

    data_list = []
    page_link(response, headers, url, data_list)

    # Create the output folder if it doesn't exist
    output_folder = "output"
    create_output_folder(output_folder)

    # Save the data to Excel inside the created folder
    output_file = os.path.join(output_folder, "mseg_gba_gov_ar.xlsx")
    df = pd.DataFrame(data_list)
    df.to_excel(output_file, index=False)

    print(f"Data successfully written to {output_file}")


if __name__ == "__main__":
    main()
