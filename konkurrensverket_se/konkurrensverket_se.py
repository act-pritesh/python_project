import asyncio
import os
import re
from datetime import datetime

import pandas as pd
from lxml import html
from urllib.parse import urljoin
from curl_cffi import requests
import html as html_module

def convert_to_yy_mm_dd(publisheddate):
    # Parse the input date and convert it to 'yy-mm-dd' format
    try:
        date_obj = datetime.strptime(publisheddate, "%d %B %Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return "Invalid date format. "

def extract_name(text):
    # Regex pattern to extract name and title (name, title)
    pattern = r'([A-Za-z\s]+(?:[A-Za-z\s]+)*)\s*,\s*([A-Za-z\s]+)'
    return re.findall(pattern, text)

def extract_phone_numbers(text):
    # Regex pattern for matching phone numbers
    pattern = r'(\d[\d\s\-]+)'
    return re.findall(pattern, text)

def extract_emails(text):
    # Regex pattern for matching email addresses
    pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    return re.findall(pattern, text)
def remove_html_tags(html_content):
    tree = html.fromstring(html_content)

    # Extract text from the parsed HTML tree
    text_without_html = tree.text_content()
    text_without_entities = html_module.unescape(text_without_html)
    text_without_entities = text_without_entities.replace("\xa0", " ")
    return text_without_entities


async def page_data(unique_link,client,url,data_list):
    response=await client.get(unique_link)
    json_data=response.json()
    all_content=json_data.get('content',{})

    title=all_content.get('heading')
    preamble=all_content.get('preamble')

    fragments = all_content.get('text', {}).get('fragments', [])
    date= all_content.get('publishedDate')
    final_date=convert_to_yy_mm_dd(date)
    print(final_date)
    # If there are at least 5 dictionaries in the fragments list
    if len(fragments) >= 5:

        raw_description = fragments[0]
        des = raw_description.get('raw', '')
        clean_des = remove_html_tags(des)

        # Extract the contact information from index 2
        raw_contact = fragments[2]
        con = raw_contact.get('raw', '')
        clean_con = remove_html_tags(con)
        final = f"{preamble},{clean_des},{clean_con}"
        data_list.append({
            'url': url,
            'news_url': unique_link,
            'press_release_date': final_date if final_date else "N/A",
            'title': title if title else "N/A",
            'description': final if final else "N/A"
        })
    # If there are fewer than 5 dictionaries in the fragments list
    else:
        # Extract the description from index 0
        raw_description = fragments[0]
        des = raw_description.get('raw', '')
        clean_des = remove_html_tags(des)

        final = f"{preamble},{clean_des}"
        data_list.append({
            'url': url,
            'news_url': unique_link,
            'press_release_date': final_date if final_date else "N/A",
            'title': title if title else "N/A",
            'description': final if final else "N/A"
        })
async def page_link(url, client,data_list):
    response = await client.get(url)
    json_data=response.json()
    items=json_data.get('items',[])
    for item in items:
        links_dict=item.get('link',{})
        link=links_dict.get('link')
        full_link=urljoin("https://www.konkurrensverket.se/",link)
        await page_data(full_link,client,url,data_list)


def create_output_folder(folder_name="output"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


async def main():
    """Main function to initiate web scraping."""
    cookies = {
        'ai_user': 'L76ZX|2024-12-09T09:22:00.127Z',
        'CookieInformationConsent': '%7B%22website_uuid%22%3A%22cdda5372-26ab-4177-815b-1c9cf9929296%22%2C%22timestamp%22%3A%222024-12-09T09%3A22%3A04.100Z%22%2C%22consent_url%22%3A%22https%3A%2F%2Fwww.konkurrensverket.se%2Fen%2Fnews%2F%3Fsorting%3Drelevance%26page%3D1%22%2C%22consent_website%22%3A%22prod.konkurrensverket.se%22%2C%22consent_domain%22%3A%22www.konkurrensverket.se%22%2C%22user_uid%22%3A%2257f7e850-0dfb-400d-b55a-09a267a75202%22%2C%22consents_approved%22%3A%5B%22cookie_cat_necessary%22%2C%22cookie_cat_functional%22%2C%22cookie_cat_statistic%22%2C%22cookie_cat_marketing%22%2C%22cookie_cat_unclassified%22%5D%2C%22consents_denied%22%3A%5B%5D%2C%22user_agent%22%3A%22Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F131.0.0.0%20Safari%2F537.36%22%7D',
        '_ga': 'GA1.1.22331489.1733736121',
        'ASP.NET_SessionId': '0ix4jdpiix01mlxn4i4zcwju',
        '__RequestVerificationToken': 'qA3zAeihAEMRcbxcC7P6hE36Vf1MsJqi6lgR5hgRqUFGP-DIa2aLmfbtd_wBvr5T7diZiBAxbjlzmEPQcutGI0Vo4ZpsV6JqWNLRvw8RNnI1',
        'ARRAffinity': '7fe3a0fbc349e9d066c9000519d2a34df99f06fe857948e09df781f27b0bfdca',
        'ARRAffinitySameSite': '7fe3a0fbc349e9d066c9000519d2a34df99f06fe857948e09df781f27b0bfdca',
        'ai_session': 'Wgt4c|1733803901828|1733803946391.9',
        '_ga_47D7JXLW30': 'GS1.1.1733803901.4.1.1733803975.0.0.0',
    }

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        # 'cookie': 'ai_user=L76ZX|2024-12-09T09:22:00.127Z; CookieInformationConsent=%7B%22website_uuid%22%3A%22cdda5372-26ab-4177-815b-1c9cf9929296%22%2C%22timestamp%22%3A%222024-12-09T09%3A22%3A04.100Z%22%2C%22consent_url%22%3A%22https%3A%2F%2Fwww.konkurrensverket.se%2Fen%2Fnews%2F%3Fsorting%3Drelevance%26page%3D1%22%2C%22consent_website%22%3A%22prod.konkurrensverket.se%22%2C%22consent_domain%22%3A%22www.konkurrensverket.se%22%2C%22user_uid%22%3A%2257f7e850-0dfb-400d-b55a-09a267a75202%22%2C%22consents_approved%22%3A%5B%22cookie_cat_necessary%22%2C%22cookie_cat_functional%22%2C%22cookie_cat_statistic%22%2C%22cookie_cat_marketing%22%2C%22cookie_cat_unclassified%22%5D%2C%22consents_denied%22%3A%5B%5D%2C%22user_agent%22%3A%22Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F131.0.0.0%20Safari%2F537.36%22%7D; _ga=GA1.1.22331489.1733736121; ASP.NET_SessionId=0ix4jdpiix01mlxn4i4zcwju; __RequestVerificationToken=qA3zAeihAEMRcbxcC7P6hE36Vf1MsJqi6lgR5hgRqUFGP-DIa2aLmfbtd_wBvr5T7diZiBAxbjlzmEPQcutGI0Vo4ZpsV6JqWNLRvw8RNnI1; ARRAffinity=7fe3a0fbc349e9d066c9000519d2a34df99f06fe857948e09df781f27b0bfdca; ARRAffinitySameSite=7fe3a0fbc349e9d066c9000519d2a34df99f06fe857948e09df781f27b0bfdca; ai_session=Wgt4c|1733803901828|1733803946391.9; _ga_47D7JXLW30=GS1.1.1733803901.4.1.1733803975.0.0.0',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://www.konkurrensverket.se/en/news?sorting=relevance&page=8',
        'request-context': 'appId=cid-v1:b8d12d9b-8803-4900-aed3-39efe9b3aee7',
        'request-id': '|x46uT.5VgOE',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    page = 1
    data_list = []
    while True:
        params = {
            'sorting': 'relevance',
            'page': page,
        }

        url = 'https://www.konkurrensverket.se/en/news/'


        # Use an async session for efficient network requests
        async with requests.AsyncSession(cookies=cookies, headers=headers, params=params) as client:
            previous_count = len(data_list)
            await page_link(url, client, data_list)

            # Check if no data was fetched on the first page or subsequent pages
            if len(data_list) == previous_count:
                print(f"No data found on page {page}. Stopping pagination.")
                break
        # Increment page number to move to the next page
        page += 1

    output_folder = "output"
    create_output_folder(output_folder)

    # Save the data to Excel inside the created folder
    output_file = os.path.join(output_folder, "konkurrensverket_se.xlsx")
    df = pd.DataFrame(data_list)
    df.to_excel(output_file, index=False)

    print(f"Data successfully written to {output_file}")

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
