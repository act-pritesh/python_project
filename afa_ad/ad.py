import re
from datetime import datetime
import requests
from parsel import Selector
import pandas as pd

#formate date to yy-mm-dd
def convert_date(date_str):
    # Convert the string to a datetime object
    date_obj = datetime.strptime(date_str, '%d/%m/%Y')
    # Format the datetime object to the desired format (yy-mm-dd)
    return date_obj.strftime('%Y-%m-%d')

#remove punctuation
def remove_specific_punctuation(text):
    punctuation_marks = [
        ".", ",", "?", "!", ":", ";", "—", "-", "'", '"', "[", "]", "{", "}", "…", "\\", "@", "&", "*",
        "_", "^", "~", "`", "/", "“", "”", "(", ")", "  ","’"
    ]
    for char in punctuation_marks:
        text = str(text).replace(char, '')
    return text


#get the page data
def page_data(href, url, status, date, name, header, cookies, all_data):
    # Sending a GET request to fetch the page content
    response = requests.get(href, headers=header, cookies=cookies)

    # Parse the page content using Selector from Scrapy
    parsed_data = Selector(text=response.text)  # Use response.text directly here
    response_data = parsed_data.xpath('//div[@id="parent-fieldname-text"]//text()').getall()
    full_response = "".join(response_data)
    pattern = "amounting to.([\d.,]+ euros)"
    pattern2 = "Penalty of.([\d.,]+ euros)"
    pattern3 = "penalty of.([\d.,]+ euros)"
    match = re.search(pattern, full_response)
    if match:
        # If pattern1 matches, get the amount from pattern1
        penalty_amount = match.group(1)
    else:
        # If pattern1 does not match, search for the second pattern (Penalty of)
        matches2 = re.findall(pattern2, full_response)
        if matches2:
            # Join all found matches from pattern2 with a pipe ("|") separator
            penalty_amount = "|".join(matches2)
        else:
            # If pattern2 does not match, search for pattern3 (penalty of)
            matches3 = re.findall(pattern3, full_response)
            if matches3:
                # Join all found matches from pattern3 with a pipe ("|") separator
                penalty_amount = "|".join(matches3)
            else:
                penalty_amount = "N/A"  # If no matches for pattern2 or pattern3, return "N/A"

    # Storing the extracted data in a dictionary
    extracted_data = {
        "url":url,
        'name': name,
        "article_url":href,
        'section': "N/A",
        'date_of_Order': date,  # You can modify how to get the actual Date of Order if available in the page
        'penalty_amount': penalty_amount,
        'status': status,
        'reason': "N/A",
    }

    # Append the extracted data to the list
    all_data.append(extracted_data)

#fetch page link and their data
def page_link(response, header, cookies, url, all_data):
    parsed_data = Selector(response.text)
    all_links = parsed_data.xpath('//div[@id="list_items"]/a')
    for data in all_links:
        href = data.xpath('./@href').get()
        status = data.xpath('.//div[@class="col-md-12 roboto-light-10"]/text()').get().replace('Status: ', '')
        date = data.xpath('.//div[@class="col-xs-12 discreet"]/text()').get()
        final_date = convert_date(date)
        name = data.xpath('./@title').get().split(':')[1]
        final_name=remove_specific_punctuation(name)
        print(href)
        page_data(href, url, status, final_date, final_name, header, cookies, all_data)

def main():
    """Main function to initiate web scraping."""
    cookies = {
        'CookieConsent': '{stamp:%274b9YXo12r+cn2YHVtEaIvldaWvcJrsXiOnUVmtUmnmMTIYYF8bT1gg==%27%2Cnecessary:true%2Cpreferences:false%2Cstatistics:false%2Cmarketing:false%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1729504855640%2Cregion:%27gb%27}',
    }
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

    url = 'https://www.afa.ad/en/entitats-supervisades/sancions-a-entitats-supervisades'
    response = requests.get(url, cookies=cookies, headers=headers)

    # List to hold all extracted data
    all_data = []

    page_link(response, headers, cookies, url, all_data)

    # After collecting all the data, convert the list to a pandas DataFrame
    df = pd.DataFrame(all_data)

    # Save the DataFrame to an Excel file
    df.to_excel('ad.xlsx', index=False, engine='openpyxl')


if __name__ == "__main__":
    main()
