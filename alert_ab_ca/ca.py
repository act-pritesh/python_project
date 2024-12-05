import os
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import pandas as pd
import requests
from parsel import Selector


def format_date(date_str):
    # Check if the date string contains a weekday (e.g., Monday, Tuesday)
    if re.match(r'^[A-Za-z]+,', date_str):
        # If the date contains the weekday, remove the weekday part
        date_str = date_str.split(', ', 1)[1]

    try:
        date_obj = datetime.strptime(date_str, "%d %B, %Y")
    except ValueError:
        date_obj = datetime.strptime(date_str, "%B %d, %Y")

    # Return the date in "yyyy-mm-dd" format
    return date_obj.strftime("%Y-%m-%d")

data_entries = []  # List to hold all data entries

def page_data(href,header,cookies,url):
    # if href=='https://alert-ab.ca/major-cocaine-seizure-in-edmonton/':
    response = requests.get(href,headers=header,cookies=cookies)
    parsed_data = Selector(text=response.text)
    title = parsed_data.xpath('//h3[@class="dce-title"]/text()').get()
    date=parsed_data.xpath('//span[@class="elementor-icon-list-text elementor-post-info__item elementor-post-info__item--type-date"]/text() | //span[@class="d1"]/text()').get().strip()
    formatted_date = format_date(date)
    description=parsed_data.xpath('//div[@class="elementor-column elementor-col-100 elementor-top-column elementor-element elementor-element-4334163"]/div//text() | //div[@class="dynamic-content-for-elementor-acf "]//text()').getall()
    final_dis=' '.join(description).replace('\n','').replace('\t','').replace('&nbsp','').strip()
    final_dis = re.sub(r'\s+', ' ', final_dis)
    data_entry = {
        'url': url,
        'title': title if title else "N/A",
        'article_url': href if href else "N/A",
        'date': formatted_date if formatted_date else "N/A",
        'description': final_dis if final_dis else "N/A"
    }
    data_entries.append(data_entry)

def create_output_folder(folder_name="output"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
# Function to save data to an Excel file
def save_to_excel(filename='ca_data.xlsx'):
    # Create the output folder if it doesn't exist
    output_folder = "output"
    create_output_folder(output_folder)
    # Save the data to Excel inside the created folder
    output_file = os.path.join(output_folder, "alert_ab_ca.xlsx")
    df = pd.DataFrame(data_entries)
    df.to_excel(output_file, index=False)
    print(f"Data successfully written to {output_file}")

def page_link(response,header,cookies,url):
    parsed_data = Selector(response.text)
    all_data = parsed_data.xpath('//h3[@class="elementor-post__title"]/a')
    with ThreadPoolExecutor(max_workers=9) as executor:
        for data in all_data:
            href = data.xpath('./@href').get()
            executor.submit(page_data,href, header, cookies,url) # Submitting each page for data scraping
    next_page=parsed_data.xpath('//a[@class="page-numbers next"]/@href').get()
    if next_page:
        response = requests.get(next_page, headers=header, cookies=cookies)
        page_link(response, header, cookies,url)
    else:
        print('no page')



def main():
    """Main function to initiate web scraping."""
    cookies = {
        '_ga': 'GA1.1.375934927.1730091885',
        '_scid': 'JM1z7b1gUfWSnoEsTySsgErSP2ebIcrv',
        '_ScCbts': '%5B%22572%3Bchrome.2%3A2%3A5%22%5D',
        '_sctr': '1%7C1730917800000',
        '_scid_r': 'TE1z7b1gUfWSnoEsTySsgErSP2ebIcrvChy53Q',
        '_ga_FKS2PPX2R2': 'GS1.1.1730956075.4.1.1730959868.0.0.0',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        # 'cookie': '_ga=GA1.1.375934927.1730091885; _scid=JM1z7b1gUfWSnoEsTySsgErSP2ebIcrv; _ScCbts=%5B%22572%3Bchrome.2%3A2%3A5%22%5D; _sctr=1%7C1730917800000; _scid_r=TE1z7b1gUfWSnoEsTySsgErSP2ebIcrvChy53Q; _ga_FKS2PPX2R2=GS1.1.1730956075.4.1.1730959868.0.0.0',
        'priority': 'u=0, i',
        'referer': 'https://alert-ab.ca/news-centre/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }

    url='https://alert-ab.ca/news-centre/'
    response = requests.get(url, cookies=cookies, headers=headers)
    page_link(response,headers,cookies,url)
    # After scraping, save the data to an Excel file
    save_to_excel()
if __name__ == "__main__":
    main()
