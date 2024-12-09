import os
from datetime import datetime
import requests
from parsel import Selector
import re
import pandas as pd


def remove_extra_space(row_data):
    """Remove extra spaces or newlines from a string."""
    value = re.sub(r'\s+', ' ', row_data).strip()
    return value

def format_date(date_str):
    """Convert dates  to 'YYYY-MM-DD'."""
    try:
        return datetime.strptime(date_str, '%d %B %Y').strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return date_str  # Return original if the format doesn't match

# Function to remove specific punctuation from text
def remove_specific_punctuation(text):
    punctuation_marks = [
        ".", ",", "?", "!", ":", ";", "—", "-", "'", '"', "[", "]", "{", "}", "…", "\\", "@", "&", "*",
        "_", "^", "~", "`", "/", "“", "”", "(", ")", "  "
    ]
    for char in punctuation_marks:
        text = str(text).replace(char, '')
    return text

def extract_alias(firm_name):
    # Look for parentheses first
    aliases = re.findall(r'\([^()]*\)', firm_name)
    cleaned_aliases = []

    if aliases:
        for alias in aliases:
            if re.search(r'\d', alias):
                continue  # Skip aliases with numbers

            cleaned_alias = remove_specific_punctuation(alias.strip("()"))
            if cleaned_alias:
                cleaned_aliases.append(cleaned_alias)

        combined_alias = ' | '.join(cleaned_aliases)

        # Remove parentheses content and clean firm name
        cleaned_name = re.sub(r'\s*\(.*?\)', '', firm_name).strip()
        cleaned_name = remove_specific_punctuation(cleaned_name)

        return combined_alias, cleaned_name

    # If no alias was found
    cleaned_name = remove_specific_punctuation(firm_name)
    return "N/A", cleaned_name

def html_data(href, outcome_keys):
    """Extracts data from the specified URL and returns a list of data entries."""
    response = requests.get(href)
    parsed_data = Selector(text=response.text)
    full_article = parsed_data.xpath('//article[@class="col-md-8 article articles-floated "]')

    data_entries = []  # List to hold all data entries

    for data in full_article:
        name = data.xpath('.//h1/text()').get()
        fullname = remove_extra_space(name.replace('\r', '').replace('\n', ''))

        # Pass the full name to extract alias and clean full name
        alias, cleaned_fullname = extract_alias(fullname)

        # Get address if available
        if data.xpath('.//h1/small[1]/span'):
            address = data.xpath('.//h1/small/text()').get()
            fulladdress = remove_extra_space(address.replace('\r', '').replace('\n', ''))
        else:
            fulladdress = None  # If no address is found

        boxes = data.xpath('.//div[@class="panel-body"]')  # Ensure this targets child elements correctly

        for box in boxes:
            # Extract h3 and clean it
            h3 = box.xpath('.//h3/text()').get()
            clean_h3 = remove_extra_space(h3.replace('\r', '').replace('\n', ''))

            # Prepare dynamic keys
            formatted_h3 = clean_h3.replace(' - ', '_').replace(' ', '_').lower()

            # Extract outcome details and format dates
            outcome = box.xpath('.//p[contains(text(),"Outcome:")]/text()').get(default=None)
            outcome = outcome.replace("Outcome:", "").strip() if outcome else None

            # Format outcome_date to 'YYYY-MM-DD' using format_date function
            outcome_date = box.xpath('.//p[contains(text(),"Outcome date:")]/text()').get(default=None)
            outcome_date = format_date(outcome_date.replace("Outcome date:", "").strip()) if outcome_date else None

            # Format published_date to 'YYYY-MM-DD' using format_date function
            published_date = box.xpath('.//p[contains(text(),"Published date:")]/text()').get(default=None)
            published_date = format_date(
                published_date.replace("Published date:", "").strip()) if published_date else None

            # Firm details
            firm_details_name = box.xpath('.//p[contains(text(),"Name:")]/text()').get(default=None)
            firm_details_name = firm_details_name.replace("Name:", "").strip() if firm_details_name else None
            firm_details_address = box.xpath('.//p[contains(text(),"Address(es):")]/text()').get(default=None)
            firm_details_address = firm_details_address.replace("Address(es):",
                                                                "").strip() if firm_details_address else None
            firm_details_address = re.sub(r'\s+', ' ', firm_details_address).strip() if firm_details_address else None
            firm_details_id = box.xpath('.//p[contains(text(),"Firm ID:")]/text()').get(default=None)
            firm_details_id = firm_details_id.replace("Firm ID:", "").strip() if firm_details_id else None

            # Extracting outcome details
            outcome_details = " ".join(
                reason.strip() for reason in box.xpath('.//div[@class="accordion-section"][last()]//text()').getall())
            outcome_details = re.sub(r'\s+', ' ', outcome_details).strip() if outcome_details else None

            # Creating a base entry for the extracted data
            data_entry = {
                'fullname': cleaned_fullname,
                'alias': alias,
                'address': fulladdress,
                'firm_details_name': firm_details_name,
                'firm_details_address': firm_details_address,
                'firm_details_id': firm_details_id,
                'outcome_details': outcome_details,
            }

            # Dynamically add outcome data to the entry, ensuring no duplicates
            if outcome is not None:
                data_entry[f'{formatted_h3}_outcome'] = outcome
                outcome_keys.add(f'{formatted_h3}_outcome')  # Keep track of unique outcome keys
            else:
                data_entry[f'{formatted_h3}_outcome'] = None  # Set to None for empty cells

            # Adding formatted outcome_date to data_entry
            if outcome_date is not None:
                data_entry[f'{formatted_h3}_outcome_date'] = outcome_date
                outcome_keys.add(f'{formatted_h3}_outcome_date')
            else:
                data_entry[f'{formatted_h3}_outcome_date'] = None  # Set to None for empty cells

            # Adding formatted published_date to data_entry
            if published_date is not None:
                data_entry[f'{formatted_h3}_published_date'] = published_date
                outcome_keys.add(f'{formatted_h3}_published_date')
            else:
                data_entry[f'{formatted_h3}_published_date'] = None  # Set to None for empty cells

            # Append the entry to the list
            data_entries.append(data_entry)

    return data_entries
def create_output_folder(folder_name="output"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
def page_link(response):
    """Extract links from the response page and process each link."""
    parsed_data = Selector(response.text)
    all_data = parsed_data.xpath('//article[@class="col-md-8 article articles-floated "]//div[@class="list-group"]/a')
    # Initialize a set to keep track of dynamic keys
    outcome_keys = set()
    all_entries = []  # List to hold all entries for final DataFrame

    for data in all_data:
        href = data.xpath('./@href').get()
        full_href = 'https://www.sra.org.uk/' + href
        print(full_href)
        entries = html_data(full_href, outcome_keys)  # Get entries from each link
        all_entries.extend(entries)  # Extend the all_entries list

    # Create a DataFrame from all entries
    # final_df = pd.DataFrame(all_entries)
    #
    # # Add empty columns for any outcome keys that are not present in each entry
    # for key in outcome_keys:
    #     if key not in final_df.columns:
    #         final_df[key] = None  # Add empty column for missing outcomes
    #
    # # Fill empty cells with "N/A"
    # final_df.fillna("N/A", inplace=True)
    #
    # # Save the DataFrame to an Excel file
    # final_df.to_excel('uk_data.xlsx', index=False)  # Save as 'extracted_data.xlsx'
    # print("Data has been written to extracted_data.xlsx")  # Confirmation message
    output_folder = "output"
    create_output_folder(output_folder)
    df = pd.DataFrame(all_entries)
    for key in outcome_keys:
        if key not in df.columns:
            df[key] = None  # Add empty column for missing outcomes

    # Save the data to Excel inside the created folder


    # # Fill empty cells with "N/A"
    df.fillna("N/A", inplace=True)
    output_file = os.path.join(output_folder, "sra_org_uk.xlsx")
    df.to_excel(output_file, index=False)

    print(f"Data successfully written to {output_file}")



def main():
    """Main function to initiate web scraping."""
    cookies = {
        'OptanonAlertBoxClosed': '2024-10-21T09:49:29.780Z',
        'ASP.NET_SessionId': 'vzputke0vdysjbwd1w1bn2sb',
        'ARRAffinity': 'f3fa9d65bbfa688d29a1a91ccdec91ae26ed93dc3155948db01783a752e0543f',
        'ARRAffinitySameSite': 'f3fa9d65bbfa688d29a1a91ccdec91ae26ed93dc3155948db01783a752e0543f',
        'TiPMix': '43.58627385475036',
        'x-ms-routing-name': 'self',
        'OptanonConsent': 'isGpcEnabled=0&datestamp=Mon+Oct+28+2024+16%3A12%3A10+GMT%2B0530+(India+Standard+Time)&version=202405.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=3b4adb24-ab94-4624-94af-c2d20661f501&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0003%3A0%2CC0004%3A0%2CC0007%3A0&intType=3&geolocation=GB%3BENG&AwaitingReconsent=false',
    }
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }
    url = 'https://www.sra.org.uk/consumers/solicitor-check/recent-decisions/'
    response = requests.get(url, cookies=cookies, headers=headers)
    page_link(response)

if __name__ == "__main__":
    main()
