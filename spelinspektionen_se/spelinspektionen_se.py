import os
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import requests
from parsel import Selector




def page_data(unique_link, headers,cookies,date,url,data_list):
    response=requests.get(unique_link,headers=headers, cookies=cookies)
    parsed_data = Selector(text=response.text)
    title = parsed_data.xpath('//div[@class="page-header"]/h1/text()').get()
    translated_title = GoogleTranslator(source='auto', target='en').translate(title) if title else "N/A"
    final_date=date
    description=parsed_data.xpath('//div[@class="main-body"]//*/text()').getall()
    full_des="".join( des.strip() for des in description)
    translated_full_des = GoogleTranslator(source='auto', target='en').translate(full_des) if full_des else "N/A"
    data_list.append({
        'url':url,
        'news_url':unique_link,
        'title':translated_title,
        'date':final_date,
        'description':translated_full_des
    })


def page_link(response, headers, cookies,url,data_list):
    parsed_data = Selector(response.text)

    # Extract all the links from the current page
    all_links = parsed_data.xpath('//div[@class="row"]//a[@class="header"]')


    def process(data):
        href = data.xpath('./@href').get()
        date=data.xpath('//small[@class="date"]/text()').get()
        page_data(href, headers, cookies,date,url,data_list)

    # Use ThreadPoolExecutor to process the links concurrently

    with ThreadPoolExecutor() as executor:
        executor.map(process, all_links)

    # Extract the link for the next page from the pagination section
    next_page = parsed_data.xpath('//li[last()]//a[@class="page-link"]/@href').get()

    if next_page:
        # If there is a next page, construct the full URL and request it
        next_page_url = 'https://www.spelinspektionen.se' + next_page
        print(f"Next page URL: {next_page_url}")

        # Request the next page and call the page_link function again
        next_response = requests.get(next_page_url, headers=headers, cookies=cookies)
        page_link(next_response, headers, cookies,url,data_list)



def create_output_folder(folder_name="output"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def main():
    """Main function to initiate web scraping."""
    cookies = {
        'cookie_policy_settings': 'true%2Ctrue%2Ctrue%2Ctrue',
        'ASP.NET_SessionId': 'ewnj0oqzs0guscwjhababypj',
        '_pk_id.1.1528': '21fd262164361068.1733380866.',
        '_pk_ses.1.1528': '1',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }

    url = 'https://www.spelinspektionen.se/press/nyhetsarkiv/page/2/'

    # Send the first request
    response = requests.get(url, cookies=cookies, headers=headers)

    data_list=[]
    # Start the scraping process
    page_link(response,headers,cookies,url,data_list)

    # Create the output folder if it doesn't exist
    output_folder = "output"
    create_output_folder(output_folder)

    # Save the data to Excel inside the created folder
    output_file = os.path.join(output_folder, "spelinspektionen_se_translate.xlsx")
    df = pd.DataFrame(data_list)
    df.to_excel(output_file, index=False)

    print(f"Data successfully written to {output_file}")

if __name__ == "__main__":
    main()
