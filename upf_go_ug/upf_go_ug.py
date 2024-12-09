import asyncio
import os
import re
from datetime import datetime
import httpx
import pandas as pd
from parsel import Selector



def convert_date_to_yy_mm_dd(date_str):
    # Parse the input string to a datetime object
    date_obj = datetime.strptime(date_str, "%B %d, %Y")
    # Format the datetime object to 'yy-mmdd'
    return date_obj.strftime("%Y-%m-%d")


async def page_data(url,unique_link,client,data_list):
    response=await client.get(unique_link)
    parsed_data = Selector(response.text)
    title = parsed_data.xpath('//h1[@class="entry-title"]//text()').get('N/A')
    title = re.sub(r'\s+', ' ', title).strip()
    date= parsed_data.xpath('//span[@class="posted-on"]//time//text()').get('N/A')
    final_date= convert_date_to_yy_mm_dd(date)
    description= ' '.join(parsed_data.xpath('//div[@class="entry-content"]/*//text()').getall()).replace(' ','')
    description = re.sub(r'\s+', ' ', description).strip()
    data_list.append({
        'url':url,
        'news_url':unique_link,
        'date':final_date,
        'title':title,
        'description':description if description else "N/A"
    })


async def page_link(url, client,data_list):
    response = await client.get(url)
    parsed_data = Selector(response.text)

    # Extract all the links from the current page
    all_links = parsed_data.xpath('//header[@class="entry-header"]/h2/a')

    for data in all_links:
        href = data.xpath('./@href').get()
        print(href)
        await page_data(url,href,client,data_list)

    # Check for pagination and recursively process it
    pagination = parsed_data.xpath('//div[@class="nav-links"]/div[@class="nav-previous"]/a/@href').get()
    if pagination:
        await page_link(pagination, client,data_list)
    else:
        print('no pagination')


async def create_output_folder(folder_name="output"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


async def main():
    """Main function to initiate web scraping."""
    cookies = {
        '__wpdm_client': '1e439586eb510b190ae1b8d04dd52048',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
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

    params = {
        's': 'Wanted',
    }

    url = 'https://upf.go.ug/page/1/'

    data_list=[]
    # Use an async client for efficient network requests
    async with httpx.AsyncClient(cookies=cookies, headers=headers, params=params) as client:
        await page_link(url,client,data_list)

    output_folder = "output"
    await create_output_folder(output_folder)

    # Save the data to Excel inside the created folder
    output_file = os.path.join(output_folder, "upf_go_ug.xlsx")
    df = pd.DataFrame(data_list)
    df.to_excel(output_file, index=False)

    print(f"Data successfully written to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
