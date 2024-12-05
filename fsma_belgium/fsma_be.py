import os
from datetime import datetime
from urllib.parse import urljoin
import pandas as pd
import requests
from parsel import Selector
import re

# Cookies and headers for the request
cookies = {
    'TS01d7add0028': '0168adc1b04a0c8a4f8cb85029eb6189bd21085671fdbac71715e1f437ea135d20f2570a9916f453e810040723aad7d854d77ea670',
    'cookiebot-consent--necessary': '1',
    'cookiebot-consent--preferences': '0',
    'cookiebot-consent--statistics': '0',
    'cookiebot-consent--marketing': '0',
    'CookieConsent': '{stamp:%27KYFV6ha5Kv4pXmrHNTttZVMBq3Qu1AUCXT+d5ThasDWXPTmJE8cz+w==%27%2Cnecessary:true%2Cpreferences:false%2Cstatistics:false%2Cmarketing:false%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1729485471332%2Cregion:%27gb%27}',
    'TS01d7add0': '01ce9bf1688df6ea5b504f04ae72ab480e04d069d2d8d20b4ac10410f45327f4cdaf89fe31233bd7fc0c55153c8d51e1056cacb094',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    # 'Cookie': 'TS01d7add0028=0168adc1b04a0c8a4f8cb85029eb6189bd21085671fdbac71715e1f437ea135d20f2570a9916f453e810040723aad7d854d77ea670; cookiebot-consent--necessary=1; cookiebot-consent--preferences=0; cookiebot-consent--statistics=0; cookiebot-consent--marketing=0; CookieConsent={stamp:%27KYFV6ha5Kv4pXmrHNTttZVMBq3Qu1AUCXT+d5ThasDWXPTmJE8cz+w==%27%2Cnecessary:true%2Cpreferences:false%2Cstatistics:false%2Cmarketing:false%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1729485471332%2Cregion:%27gb%27}; TS01d7add0=01ce9bf1688df6ea5b504f04ae72ab480e04d069d2d8d20b4ac10410f45327f4cdaf89fe31233bd7fc0c55153c8d51e1056cacb094',
    'If-None-Match': '"1729498993"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

def remove_extra_space(row_data):
    # Remove 'x000D' and replace it with a space
    value = re.sub(r'x000D', ' ', row_data)
    # Remove any extra spaces or newlines created by this replacement
    value = re.sub(r'\s+', ' ', value).strip()
    # Update the cleaned value back in row_data
    return value

def remove_specific_punctuation(self, text):
    # List of punctuation marks to remove from the input text
    punctuation_marks = [
        ".", ",", "?", "!", ":", ";", "—", "-", "'", '"', "(", ")", "[", "]", "{", "}", "…", "\\", "@", "&", "*",
        "_", "^", "~","`","/"
    ]
    # Loop through each punctuation mark in the list
    for char in punctuation_marks:
        # Replace each punctuation mark in the text with an empty string
        text = str(text).replace(char, '')
    # Return the cleaned text without punctuation
    return text

# Function to fetch page content and return Selector object
def fetch_page_content(url, cookies, headers):
    response = requests.get(url, cookies=cookies, headers=headers)
    if response.status_code == 200:
        return Selector(text=response.text)
    return None

# Function to scrape column headers from the table
def scrape_column_names(selector):
    return [h.replace("\r", "").replace("\t", "").replace("\n", "").replace(" ", "_").lower().strip() for h in
            selector.xpath("//table[@class='table table-hover table-striped views-table views-view-table cols-2']//th//text()").getall()]

# Function to extract row data
def extract_row_data(row, column_names, url):
    row_data = {}
    row_data['url'] = url
    for i, cell in enumerate(row.xpath("td")):
        cell_text = remove_extra_space(cell.xpath("string()").get().strip().replace("\n", " ").replace("\t", "").replace("\r", "")).strip()
        # Try to parse the date, otherwise keep the original text
        try:
            cell_text = datetime.strptime(cell_text, '%d/%m/%Y').strftime('%Y-%m-%d')
        except:
            pass
        row_data[column_names[i]] = cell_text

        # Check if there is a link in the cell
        link = cell.xpath(".//a/@href").get()
        if link:
            full_link = urljoin(url, link)
            row_data[f"{column_names[i]}_url"] = full_link

            # Fetch additional data from the full_link if needed
            additional_info = fetch_additional_info(full_link, cookies, headers)
            row_data['description'] = additional_info

    return row_data


# Function to fetch additional information from the detail page
def fetch_additional_info(link, cookies, headers):
    try:
        page = fetch_page_content(link, cookies, headers)
        if page:
            # Example: Scrape additional data from the page
            additional_info = page.xpath('//div[@class="text-content text-content--ct-body"]//text()[not(ancestor::div[@class="box box-small box-tip"])]').getall()
            return remove_extra_space(" ".join(additional_info).strip()) or 'N/A'
    except Exception as e:
        return f"Error: {e}"
    return 'N/A'

# Main scraping function
def scrape_fsma_data():
    url = 'https://www.fsma.be/en/warnings'
    selector = fetch_page_content(url, cookies, headers)
    column_names = scrape_column_names(selector)
    rows = selector.xpath("//table[@class='table table-hover table-striped views-table views-view-table cols-2']//tr")[1:]
    data = []
    for row in rows:
        row_data = extract_row_data(row, column_names, url)
        data.append(row_data)

    return pd.DataFrame(data)

def create_output_folder(folder_name="output"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# Save the scraped data to Excel
def save_data_to_excel(df):
    df = df.replace('', 'N/A').replace('None', 'N/A')
    df.fillna('N/A', inplace=True)
    # Create the output folder if it doesn't exist
    output_folder = "output"
    create_output_folder(output_folder)

    # Save the data to Excel inside the created folder
    output_file = os.path.join(output_folder, "fsma_be.xlsx")
    df.to_excel(output_file, index=False)

    print(f"Data successfully written to {output_file}")

# Run the scraper and save the data
def main():
    df = scrape_fsma_data()
    # if df is not None:
    save_data_to_excel(df)
    #     print(f"Data has been saved to Excel successfully.")
    # else:
    #     print(f"Failed to fetch data from FSMA.")


if __name__ == "__main__":
    main()
