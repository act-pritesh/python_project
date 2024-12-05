import os
from datetime import datetime
import pandas as pd
import requests
from parsel import Selector
from googletrans import Translator  # Import the Translator class

# Initialize the translator
translator = Translator()


# Format date to yy-mm-dd
def convert_date(date_str):
    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
    return date_obj.strftime('%Y-%m-%d')


# Get the page data
def page_data(href, url, header, all_data):
    response = requests.get(href, headers=header)
    parsed_data = Selector(response.text)
    case_summary = parsed_data.xpath('//div[@class="entry-content"]/p/text()').getall()
    final_case_summary = "".join(case_summary)

    # Translate the case summary to English
    translated_case_summary = translator.translate(final_case_summary, src='auto', dest='en').text

    date = parsed_data.xpath('//time[@class="entry-date published"]/text()').get()
    formated_date = convert_date(date)

    # Storing the extracted data in a dictionary
    extracted_data = {
        "url": url,
        "name": "N/A",
        "alias_name": "N/A",
        "news_url": href,
        "age": "N/A",
        "address": "N/A",
        "seized_items": "N/A",
        "reason": "N/A",
        "case_summary": translated_case_summary,  # Store translated summary here
        "date_of_press_release": formated_date
    }
    all_data.append(extracted_data)


# Fetch page link and their data
def page_link(response, header, url, all_data):
    parsed_data = Selector(response.text)
    all_links = parsed_data.xpath('//h2[@class="entry-title"]/a')
    for data in all_links:
        href = data.xpath('./@href').get()
        print(href)
        page_data(href, url, header, all_data)


def create_output_folder(folder_name="output"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def main():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
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

    url = 'https://asp.gov.al/category/lajmi-i-fundit/'
    response = requests.get(url, headers=headers)
    all_data = []

    page_link(response, headers, url, all_data)

    # Create the output folder if it doesn't exist
    output_folder = "output"
    create_output_folder(output_folder)

    # Save the data to Excel inside the created folder
    output_file = os.path.join(output_folder, "asp_gov_al.xlsx")
    df = pd.DataFrame(all_data)
    df.to_excel(output_file, index=False)

    print(f"Data successfully written to {output_file}")


if __name__ == "__main__":
    main()
