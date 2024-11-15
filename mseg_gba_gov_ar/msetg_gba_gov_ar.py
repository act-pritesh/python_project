import locale
import re
from googletrans import Translator  # Import the Translator class
from datetime import datetime
from re import findall
from urllib.parse import urljoin, quote
import requests
from parsel import Selector
import pandas as pd

# Initialize the translator
translator = Translator()

def replace_spaces_only(url):
    # Replace spaces in the URL with '%20'
    return url.replace(" ", "%20")

def convert_dates_to_yy_mm_dd(date_list):
    # Set locale to Spanish for date parsing
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, 'es_ES')  # Fallback for some systems

    if not isinstance(date_list, list):
        raise TypeError("Input must be a list of strings or tuples")

    converted_dates = []
    for date_entry in date_list:
        # Extract the date string if the entry is a tuple
        date_str = date_entry[0] if isinstance(date_entry, tuple) else date_entry

        # If there's no date string, append None
        if not date_str:
            converted_dates.append(None)
            continue

        # Remove 'del año' if it exists in the date string
        date_str = date_str.replace(" del año", "")

        # Try parsing the date with the two possible formats
        try:
            # Attempt to parse "15 de julio de 1992"
            date_obj = datetime.strptime(date_str, "%d de %B de %Y")
        except ValueError:
            try:
                # Fallback to parsing "15 julio de 1992"
                date_obj = datetime.strptime(date_str, "%d %B de %Y")
            except ValueError:
                print(f"Error processing date '{date_entry}': Unsupported format")
                converted_dates.append(None)
                continue

        # Append the formatted date in "YYYY-MM-DD"
        converted_dates.append(date_obj.strftime("%Y-%m-%d"))

    return converted_dates



def remove_specific_punctuation(text):
    # List of punctuation marks to remove from the input text
    punctuation_marks = [
        ".", ",", "?", "!", ":", ";", "—", "-", "'", '"', "(", ")", "[", "]", "{", "}", "…", "\\", "@", "&", "*",
        "_", "^", "~","`","/","","","\x89"
    ]
    for char in punctuation_marks:
        text = str(text).replace(char, '')
    return text

def page_data(response, url, encoded_url, data_list):
    # Parse data if response is successful
    parsed_data = Selector(text=response.text)
    name = parsed_data.xpath('//div[@class="row  d-flex align-items-stretch"]//h2/text()').get()
    final_name = remove_specific_punctuation(name)

    # Translate the name to English
    translated_name = translator.translate(final_name, src='auto', dest='en').text if final_name else "N/A"

    data = parsed_data.xpath('//div[@class="row  d-flex align-items-stretch"]//p[@class="text-justify"]//text()').getall()
    full_data = ''.join(data)
    try:
        cleaned_text = full_data.encode('latin1').decode('utf-8')
    except UnicodeEncodeError:
        cleaned_text = full_data
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

    # Translate the case summary to English
    translated_case_summary = translator.translate(cleaned_text, src='auto', dest='en').text if cleaned_text else "N/A"

    # Initialize variables for extracted values
    dni_number = None
    birth_date = None

    # Check for different DNI patterns
    if re.search(r"DNI\s*N[º°]?\s*([\d.]+)", cleaned_text):
        dni_number = re.findall(r"DNI\s*N[º°]?\s*([\d.]+)", cleaned_text)
    elif re.search(r"D\.N\.I\.\s*N[º°]?\s*([\d.]+)", cleaned_text):
        dni_number = re.findall(r"D\.N\.I\.\s*N[º°]?\s*([\d.]+)", cleaned_text)
    elif re.search(r"D\.N\.I\.\s*([\d.]+)", cleaned_text):
        dni_number = re.findall(r"D\.N\.I\.\s*([\d.]+)", cleaned_text)
    else:
        dni_number = []

    # Check for different birth date patterns
    if re.search(r"nacido el día (\d{1,2} de \w+ de \d{4})", cleaned_text):
        birth_date = re.findall(r"nacido el día (\d{1,2} de \w+ de \d{4})", cleaned_text)
    elif re.search(r"nacido el día (\d{1,2} \w+ de \d{4})", cleaned_text):
        birth_date = re.findall(r"nacido el día (\d{1,2} \w+ de \d{4})", cleaned_text)
    elif re.search(r"nacido en (\d+)", cleaned_text):
        birth_date = re.findall(r"nacido en (\d+)", cleaned_text)
    elif re.search(r"nacido el día (\d{1,2} de \w+ del año \d{4})", cleaned_text):
        birth_date = re.findall(r"nacido el día (\d{1,2} de \w+ del año \d{4})", cleaned_text)
    else:
        birth_date = []

    converted_date = convert_dates_to_yy_mm_dd(birth_date)
    reward_amount = findall("\([\$ \d.]+\)", cleaned_text)
    final_reward = '|'.join(reward_amount).replace("(", '').replace(')', '')
    print(translated_name,converted_date,dni_number,cleaned_text)
    # Add to data list
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
        "reward_amount": final_reward,
        "complexion": "N/A",
        "height": "N/A",
        "hair_color": "N/A",
        "additional_information": "N/A"
    })

def page_link(response, header, url, data_list):
    # Parse HTML to get all link elements
    parsed_data = Selector(response.text)
    all_links = parsed_data.xpath('//table/tbody/tr/td/a')

    for data in all_links:
        # Extract and clean up the href attribute
        href = data.xpath('./@href').get()
        if href:  # Ensure href is not None
            href = href.replace("", '').replace("", '').replace("Ã", 'Á')
            fullhref = urljoin("https://www.mseg.gba.gov.ar/areas/recompensas/", href)
            final = replace_spaces_only(fullhref)
            replace_url = final.replace("MARTÁN", "MARTÍN").replace("VÁCTOR", "VÍCTOR").replace("MATÁAS", "MATÍAS").replace("AGUSTÁN", "AGUSTÍN").replace("NÁSTOR", "NÉSTOR")
            encoded_url = quote(replace_url, safe=":/%20")

            # Send the request with the encoded URL
            response = requests.get(encoded_url, headers=header)
            page_data(response, url, encoded_url, data_list)

def main():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'If-Modified-Since': 'Tue, 10 Sep 2024 15:01:11 GMT',
        'If-None-Match': '"53da-621c524e83d67-gzip"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    url = 'https://www.mseg.gba.gov.ar/areas/recompensas/profugos.html'
    response = requests.get(url, headers=headers)

    # List to store data
    data_list = []
    # Parse links and extract data
    page_link(response, headers, url, data_list)

    # Create DataFrame
    df = pd.DataFrame(data_list)

    # Write to Excel
    output_file = "ar.xlsx"
    # df.to_excel(output_file, index=False)
    print(f"Data successfully written to {output_file}")

if __name__ == "__main__":
    main()
