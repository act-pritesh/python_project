import os
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

import pandas as pd
import requests
from parsel import Selector


def page_data(unique_link, headers,cookies,url,date,data_list):
    response=requests.get(unique_link,headers=headers, cookies=cookies)
    parsed_data = Selector(text=response.text)
    title = parsed_data.xpath('//div[@class="subtitle-wrap"]//h2/text()').get()
    final_date=date
    description=parsed_data.xpath('//dl[@class="full"]/dd/p[not(a[last()])]/text() | //dl[@class="full"]/dd//div[@class="htmlEdit"]//text()').getall()
    full_des="".join( des.strip() for des in description)
    print(full_des)
    data_list.append({
        'url':url,
        'press_link':unique_link,
        'title':title,
        'date':final_date,
        'description':full_des if full_des else "N/A"
    })




def page_link(response, headers, cookies,url,data_list):
    parsed_data = Selector(response.text)

    # Extract all the links from the current page
    all_links = parsed_data.xpath('//td[@scope="row"]')

    for data in all_links:
        href = data.xpath('./a/@href').get()
        full_href=urljoin('https://wm.moa.gov.tw/preview_fa_en/',href)
        date=data.xpath('//td[@data-th="Update"]//text()').get()
        print(full_href,date)
        page_data(full_href,headers, cookies,url,date,data_list)

def create_output_folder(folder_name="output"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def main():
    """Main function to initiate web scraping."""
    cookies = {
        '_gid': 'GA1.3.1286801868.1733393688',
        'PHPSESSID': '6ulqmgpvodsig07p0d8fhbckol',
        '_ga': 'GA1.3.610887878.1733393686',
        '_gat_gtag_UA_297400212_2': '1',
        '_ga_45K55J9SW7': 'GS1.1.1733482545.1.1.1733482563.0.0.0',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        # 'Cookie': '_gid=GA1.3.1286801868.1733393688; PHPSESSID=6ulqmgpvodsig07p0d8fhbckol; _ga=GA1.3.610887878.1733393686; _gat_gtag_UA_297400212_2=1; _ga_45K55J9SW7=GS1.1.1733482545.1.1.1733482563.0.0.0',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    url= 'https://wm.moa.gov.tw/preview_fa_en/list.php?theme=Press_Release&subtheme=&page=1&'
    # Send the first request
    response = requests.get(url, cookies=cookies, headers=headers)
    data_list=[]
    # Start the scraping process
    page_link(response,headers,cookies,url,data_list)
    # Create the output folder if it doesn't exist
    output_folder = "output"
    create_output_folder(output_folder)

    # Save the data to Excel inside the created folder
    output_file = os.path.join(output_folder, "wm_moa_gov_tw.xlsx")
    df = pd.DataFrame(data_list)
    df.to_excel(output_file, index=False)

    print(f"Data successfully written to {output_file}")

if __name__ == "__main__":
    main()
