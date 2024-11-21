
from urllib.parse import urljoin

import pymysql
import requests
from parsel import Selector


def manage_database(data_list):
    """
    Connect to the database, create the table if not exists, and insert data.

    :param data_list: List of dictionaries containing store data.
    """
    # Ensure the input is a list of dictionaries
    if isinstance(data_list, dict):
        data_list = [data_list]

    # Database connection parameters
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='actowiz',
        database='burger_king',
        charset='utf8mb4'
    )

    # SQL for table creation
    create_table_query = """
    CREATE TABLE IF NOT EXISTS boot_barn_details (
        name VARCHAR(255),
        name_xpath TEXT,
        name_html TEXT,
        address TEXT,
        address_xpath TEXT,
        address_html TEXT,
        city VARCHAR(100),
        city_xpath TEXT,
        city_html TEXT,
        state VARCHAR(100),
        state_xpath TEXT,
        state_html TEXT,
        zip_code VARCHAR(20),
        zip_code_xpath TEXT,
        zip_code_html TEXT,
        opening_hours TEXT,
        opening_hour_xpath TEXT,
        opening_hour_html TEXT
    )
    """

    # SQL for data insertion
    insert_data_query = """
    INSERT INTO boot_barn_details (
        name, name_xpath, name_html, 
        address, address_xpath, address_html, 
        city, city_xpath, city_html, 
        state, state_xpath, state_html, 
        zip_code, zip_code_xpath, zip_code_html, 
        opening_hours, opening_hour_xpath, opening_hour_html
    ) VALUES (
        %(name)s, %(name_xpath)s, %(name_html)s, 
        %(address)s, %(address_xpath)s, %(address_html)s, 
        %(city)s, %(city_xpath)s, %(city_html)s, 
        %(state)s, %(state_xpath)s, %(state_html)s, 
        %(zip_code)s, %(zip_code_xpath)s, %(zip_code_html)s, 
        %(opening_hours)s, %(opening_hour_xpath)s, %(opening_hour_html)s
    )
    """

    # Execute queries
    with connection.cursor() as cursor:
        # Create table if not exists
        cursor.execute(create_table_query)

        # Insert each data dictionary into the database
        for data in data_list:
            cursor.execute(insert_data_query, data)

    # Commit the changes and close the connection
    connection.commit()
    connection.close()
def pagedata(full_href, headers, cookies):
    response=requests.get(full_href,headers=headers, cookies=cookies)
    parsed_data = Selector(response.text)
    box=parsed_data.xpath('//div[@class="store-locator-detail-form"]')
    for b in box:
        name=b.xpath('.//h1[@class="section-title"]/text()').get()
        name_xpath = './/h1[@class="section-title"]/text()'
        name_html = b.xpath('.//h1[@class="section-title"]').get()
        address=b.xpath('.//div[@class="stores-details-display"]//address[@class="store-address"]//span[@class="store-address1" or @class="store-address2"]/text()').getall()
        address_xpath = './/div[@class="stores-details-display"]//address[@class="store-address"]//span[@class="store-address1" or @class="store-address2"]/text()'
        address_html = b.xpath('.//div[@class="stores-details-display"]//address[@class="store-address"]').getall()
        full_address="".join(address)
        full_address_html="".join(address_html)
        city=b.xpath('.//div[@class="stores-details-display"]//address[@class="store-address"]//span[@class="store-address-city"]/text()').get()
        city_xpath ='.//div[@class="stores-details-display"]//address[@class="store-address"]//span[@class="store-address-city"]/text()'
        city_html = b.xpath('.//div[@class="stores-details-display"]//address[@class="store-address"]//span[@class="store-address-city"]').get()
        state=b.xpath('.//div[@class="stores-details-display"]//address[@class="store-address"]//span[@class="store-address-state"]/text()').get()
        state_xpath ='.//div[@class="stores-details-display"]//address[@class="store-address"]//span[@class="store-address-state"]/text()'
        state_html = b.xpath('.//div[@class="stores-details-display"]//address[@class="store-address"]//span[@class="store-address-state"]').get()
        zip_code=b.xpath('.//div[@class="stores-details-display"]//address[@class="store-address"]//span[@class="store-address-postal-code"]/text()').get()
        zip_code_xpath ='.//div[@class="stores-details-display"]//address[@class="store-address"]//span[@class="store-address-postal-code"]/text()'
        zip_code_html = b.xpath('.//div[@class="stores-details-display"]//address[@class="store-address"]//span[@class="store-address-postal-code"]').get()
        open_hour=b.xpath('//div[@class="store-details-container"]//div[@class="store-hours-days"]')
        open_hour_xpath = '//div[@class="store-details-container"]//div[@class="store-hours-days"]'
        open_hour_html = b.xpath('//div[@class="store-details-container"]//div[@class="store-hours-days"]').getall()
        opening_hours_full_html=''.join(open_hour_html)
        results = []
        for day_time in open_hour:
            # Assuming open_hour contains the div with store hours
            days_elements = day_time.xpath('.//span[@class="stores-day"]')  # Extract all the days
            times_elements = day_time.xpath('.//span[not(@class="stores-day")]')  # Extract all corresponding times
            # Ensure that both days and times are the same length
            for day, time in zip(days_elements, times_elements):
                day_name = day.xpath('text()').get().strip()  # Get the day text
                time_range = time.xpath('text()').get().strip()  # Get the time range text
                results.append(f"{day_name}{time_range}")
            # Combine the results into one string
            opening_hours = " | ".join(results)
            # Create the dictionary for this store
            store_data = {
                'name': name,
                'name_xpath':name_xpath,
                'name_html':name_html,
                'address': full_address,
                'address_xpath':address_xpath,
                'address_html':full_address_html,
                'city': city.replace(',',''),
                'city_xpath':city_xpath,
                'city_html':city_html,
                'state': state,
                'state_xpath':state_xpath,
                'state_html':state_html,
                'zip_code': zip_code,
                'zip_code_xpath':zip_code_xpath,
                'zip_code_html':zip_code_html,
                'opening_hours': opening_hours,
                'opening_hour_xpath':open_hour_xpath,
                'opening_hour_html':opening_hours_full_html
            }
            print(store_data)
            manage_database(store_data)

def pagelink(response,headers,cookies):
    parsed_data=Selector(response.text)
    links=parsed_data.xpath('//div[@class="city"]/a')
    for link in links:
        href=link.xpath('./@href').get()
        full_href=urljoin('https://www.bootbarn.com/',href)
        pagedata(full_href,headers,cookies)

def main():
    cookies = {
        'GlobalE_Data': '%7B%22countryISO%22%3A%22GB%22%2C%22cultureCode%22%3A%22en-GB%22%2C%22currencyCode%22%3A%22GBP%22%2C%22apiVersion%22%3A%222.1.4%22%7D',
        'dwanonymous_3aa735181a13aa73b9e06b7d6162b1d5': 'abkJLcQKQoW0Wkzg1xIlXDjWyo',
        '_vwo_uuid_v2': 'D9670B4BFD0A60BC042394920190C2BBD|ba3e12fda1527893febb08d87f432e98',
        '_vwo_uuid': 'D9670B4BFD0A60BC042394920190C2BBD',
        '_vwo_ds': '3%241732010494%3A38.15682631%3A%3A',
        '_gcl_au': '1.1.413652769.1732010501',
        '_vis_opt_exp_28_combi': '2',
        '_ga': 'GA1.1.1734040335.1732010502',
        '__cq_uuid': 'bd3LmllmSaKEjRTJGgbHHvdouA',
        '__cq_seg': '0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00',
        'GlobalE_Welcome_Data': '%7B%22showWelcome%22%3Afalse%7D',
        '_pin_unauth': 'dWlkPVpHSTVaV1EzTlRrdE4yWmlaQzAwTW1abUxUZ3lOV010TVdabFlUbGtNalV3WkdWaQ',
        '_lc2_fpi': '9aa8f41704f2--01jd1xxxq8tw233k3qctdkj28t',
        'dwac_30d03f8f7e0d83428425462287': 'Rv_o3NEz9YRcyIq3tjqVAP53kI5Fc2EEa_c%3D|dw-only|||USD|false|US%2FPacific|true',
        'cqcid': 'abkJLcQKQoW0Wkzg1xIlXDjWyo',
        'cquid': '||',
        'sid': 'Rv_o3NEz9YRcyIq3tjqVAP53kI5Fc2EEa_c',
        'cc-at_bootbarn_us': 'eyJ2ZXIiOiIxLjAiLCJqa3UiOiJzbGFzL3Byb2QvYmNjZl9wcmQiLCJraWQiOiI4YzMyZTExNy1jNjFjLTQzMGItYWFlMS00ODc1NWMzYmIyN2IiLCJ0eXAiOiJqd3QiLCJjbHYiOiJKMi4zLjQiLCJhbGciOiJFUzI1NiJ9.eyJhdXQiOiJHVUlEIiwic2NwIjoic2ZjYy5zaG9wcGVyLW15YWNjb3VudC5iYXNrZXRzIHNmY2Muc2hvcHBlci1kaXNjb3Zlcnktc2VhcmNoIHNmY2Muc2hvcHBlci1teWFjY291bnQucGF5bWVudGluc3RydW1lbnRzIHNmY2Muc2hvcHBlci1jdXN0b21lcnMubG9naW4gc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5vcmRlcnMgc2ZjYy5zaG9wcGVyLXByb2R1Y3RsaXN0cyBzZmNjLnNob3BwZXItcHJvbW90aW9ucyBzZmNjLnNlc3Npb25fYnJpZGdlIGNfcGFzc3dvcmRsZXNzTG9naW5fciBzZmNjLnNob3BwZXItbXlhY2NvdW50LnBheW1lbnRpbnN0cnVtZW50cy5ydyBzZmNjLnNob3BwZXItbXlhY2NvdW50LnByb2R1Y3RsaXN0cyBzZmNjLnNob3BwZXItY2F0ZWdvcmllcyBzZmNjLnNob3BwZXItbXlhY2NvdW50IHNmY2Muc2hvcHBlci1teWFjY291bnQuYWRkcmVzc2VzIHNmY2Muc2hvcHBlci1wcm9kdWN0cyBzZmNjLnNob3BwZXItbXlhY2NvdW50LnJ3IHNmY2Muc2hvcHBlci1zdG9yZXMgc2ZjYy5wd2RsZXNzX2xvZ2luIHNmY2Muc2hvcHBlci1iYXNrZXRzLW9yZGVycyBzZmNjLnNob3BwZXItY3VzdG9tZXJzLnJlZ2lzdGVyIHNmY2Muc2hvcHBlci1teWFjY291bnQuYWRkcmVzc2VzLnJ3IHNmY2Muc2hvcHBlci1teWFjY291bnQucHJvZHVjdGxpc3RzLnJ3IHNmY2Muc2hvcHBlci1iYXNrZXRzLW9yZGVycy5ydyBzZmNjLnNob3BwZXItZ2lmdC1jZXJ0aWZpY2F0ZXMgc2ZjYy5zaG9wcGVyLXByb2R1Y3Qtc2VhcmNoIiwic3ViIjoiY2Mtc2xhczo6YmNjZl9wcm',
        'cc-sg_bootbarn_us': '1',
        'usid_bootbarn_us': 'b3eaddca-630b-46ac-b366-5e6dc9c1d064',
        'cc-at_bootbarn_us_2': 'Q6OnNjaWQ6ZGQxMzVlNmItNGZmNC00Y2Q0LWFhZWYtN2ZjNGExMjkzODY4Ojp1c2lkOmIzZWFkZGNhLTYzMGItNDZhYy1iMzY2LTVlNmRjOWMxZDA2NCIsImN0eCI6InNsYXMiLCJpc3MiOiJzbGFzL3Byb2QvYmNjZl9wcmQiLCJpc3QiOjEsImRudCI6IjAiLCJhdWQiOiJjb21tZXJjZWNsb3VkL3Byb2QvYmNjZl9wcmQiLCJuYmYiOjE3MzIxNzM1NjMsInN0eSI6IlVzZXIiLCJpc2IiOiJ1aWRvOnNsYXM6OnVwbjpHdWVzdDo6dWlkbjpHdWVzdCBVc2VyOjpnY2lkOmFia0pMY1FLUW9XMFdremcxeElsWERqV3lvOjpzZXNiOnNlc3Npb25fYnJpZGdlOjpjaGlkOmJvb3RiYXJuX3VzIiwiZXhwIjoxNzMyMTc1MzkzLCJpYXQiOjE3MzIxNzM1OTMsImp0aSI6IkMyQy0yMDU0MjQ0MDM3MC0xMzU1NzU4MzAxMDg0ODI5MTE5NTE4NzQzNCJ9.BL5FPsmLWPGIyUnnxfvq-1TIjbyDZWfaOYpTKPucpcxQSoEaQ86aMzc7PttVyRgMN7T6GmrXFWMvp7v1DIvkeA',
        'cc-nx-g_bootbarn_us': 'jeIqmFqxoxigJRKGRzJmxiYiGSBVTmp2FR0UiQPlDfQ',
        '__cq_dnt': '0',
        'dw_dnt': '0',
        'dwsid': 'Ri4vv0aGxBSr3M67VLrm8_6mV-3SxlCUnOOgeIVKT8Vo0IaWu1Tq8KMtptAyJNvhp6b2gzEJ_0PNH0EPmZiI9A==',
        'dw': '1',
        'dw_cookies_accepted': '1',
        '_vis_opt_s': '2%7C',
        '_vis_opt_test_cookie': '1',
        'GlobalE_Full_Redirect': 'false',
        'GlobalE_CT_Data': '%7B%22CUID%22%3A%7B%22id%22%3A%22720346058.267987225.703%22%2C%22expirationDate%22%3A%22Thu%2C%2021%20Nov%202024%2007%3A50%3A24%20GMT%22%7D%2C%22CHKCUID%22%3Anull%2C%22GA4SID%22%3A822709451%2C%22GA4TS%22%3A1732173624430%2C%22Domain%22%3A%22www.bootbarn.com%22%7D',
        'GlobalE_Ref': 'https%3A//www.google.com/',
        '_svsid': 'fc408d0e1e2b35c02fcd536e9b8ef4c9',
        '_li_dcdm_c': '.bootbarn.com',
        '_svsidss': 'fc408d0e1e2b35c02fcd536e9b8ef4c9',
        '_gcl_gs': '2.1.k1$i1732174351$u7876001',
        '_vwo_sn': '163103%3A10%3A%3A%3A1',
        '_gcl_aw': 'GCL.1732174463.CjwKCAiArva5BhBiEiwA-oTnXQ3zzxRS_Ftz9NwJpGZ7L9_x80_zv6kkyMu8vMu-xNgxGisiPHolshoCvvEQAvD_BwE',
        '_ga_5S2DVSN1BJ': 'GS1.1.1732173611.2.1.1732174465.55.0.0',
        '_uetsid': '13036ee0a7d911efb17cad26f9b1a2ef',
        '_uetvid': '4806c3f0a65d11efa5a6c544a3c695a2',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        # 'cookie': 'GlobalE_Data=%7B%22countryISO%22%3A%22GB%22%2C%22cultureCode%22%3A%22en-GB%22%2C%22currencyCode%22%3A%22GBP%22%2C%22apiVersion%22%3A%222.1.4%22%7D; dwanonymous_3aa735181a13aa73b9e06b7d6162b1d5=abkJLcQKQoW0Wkzg1xIlXDjWyo; _vwo_uuid_v2=D9670B4BFD0A60BC042394920190C2BBD|ba3e12fda1527893febb08d87f432e98; _vwo_uuid=D9670B4BFD0A60BC042394920190C2BBD; _vwo_ds=3%241732010494%3A38.15682631%3A%3A; _gcl_au=1.1.413652769.1732010501; _vis_opt_exp_28_combi=2; _ga=GA1.1.1734040335.1732010502; __cq_uuid=bd3LmllmSaKEjRTJGgbHHvdouA; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; GlobalE_Welcome_Data=%7B%22showWelcome%22%3Afalse%7D; _pin_unauth=dWlkPVpHSTVaV1EzTlRrdE4yWmlaQzAwTW1abUxUZ3lOV010TVdabFlUbGtNalV3WkdWaQ; _lc2_fpi=9aa8f41704f2--01jd1xxxq8tw233k3qctdkj28t; dwac_30d03f8f7e0d83428425462287=Rv_o3NEz9YRcyIq3tjqVAP53kI5Fc2EEa_c%3D|dw-only|||USD|false|US%2FPacific|true; cqcid=abkJLcQKQoW0Wkzg1xIlXDjWyo; cquid=||; sid=Rv_o3NEz9YRcyIq3tjqVAP53kI5Fc2EEa_c; cc-at_bootbarn_us=eyJ2ZXIiOiIxLjAiLCJqa3UiOiJzbGFzL3Byb2QvYmNjZl9wcmQiLCJraWQiOiI4YzMyZTExNy1jNjFjLTQzMGItYWFlMS00ODc1NWMzYmIyN2IiLCJ0eXAiOiJqd3QiLCJjbHYiOiJKMi4zLjQiLCJhbGciOiJFUzI1NiJ9.eyJhdXQiOiJHVUlEIiwic2NwIjoic2ZjYy5zaG9wcGVyLW15YWNjb3VudC5iYXNrZXRzIHNmY2Muc2hvcHBlci1kaXNjb3Zlcnktc2VhcmNoIHNmY2Muc2hvcHBlci1teWFjY291bnQucGF5bWVudGluc3RydW1lbnRzIHNmY2Muc2hvcHBlci1jdXN0b21lcnMubG9naW4gc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5vcmRlcnMgc2ZjYy5zaG9wcGVyLXByb2R1Y3RsaXN0cyBzZmNjLnNob3BwZXItcHJvbW90aW9ucyBzZmNjLnNlc3Npb25fYnJpZGdlIGNfcGFzc3dvcmRsZXNzTG9naW5fciBzZmNjLnNob3BwZXItbXlhY2NvdW50LnBheW1lbnRpbnN0cnVtZW50cy5ydyBzZmNjLnNob3BwZXItbXlhY2NvdW50LnByb2R1Y3RsaXN0cyBzZmNjLnNob3BwZXItY2F0ZWdvcmllcyBzZmNjLnNob3BwZXItbXlhY2NvdW50IHNmY2Muc2hvcHBlci1teWFjY291bnQuYWRkcmVzc2VzIHNmY2Muc2hvcHBlci1wcm9kdWN0cyBzZmNjLnNob3BwZXItbXlhY2NvdW50LnJ3IHNmY2Muc2hvcHBlci1zdG9yZXMgc2ZjYy5wd2RsZXNzX2xvZ2luIHNmY2Muc2hvcHBlci1iYXNrZXRzLW9yZGVycyBzZmNjLnNob3BwZXItY3VzdG9tZXJzLnJlZ2lzdGVyIHNmY2Muc2hvcHBlci1teWFjY291bnQuYWRkcmVzc2VzLnJ3IHNmY2Muc2hvcHBlci1teWFjY291bnQucHJvZHVjdGxpc3RzLnJ3IHNmY2Muc2hvcHBlci1iYXNrZXRzLW9yZGVycy5ydyBzZmNjLnNob3BwZXItZ2lmdC1jZXJ0aWZpY2F0ZXMgc2ZjYy5zaG9wcGVyLXByb2R1Y3Qtc2VhcmNoIiwic3ViIjoiY2Mtc2xhczo6YmNjZl9wcm; cc-sg_bootbarn_us=1; usid_bootbarn_us=b3eaddca-630b-46ac-b366-5e6dc9c1d064; cc-at_bootbarn_us_2=Q6OnNjaWQ6ZGQxMzVlNmItNGZmNC00Y2Q0LWFhZWYtN2ZjNGExMjkzODY4Ojp1c2lkOmIzZWFkZGNhLTYzMGItNDZhYy1iMzY2LTVlNmRjOWMxZDA2NCIsImN0eCI6InNsYXMiLCJpc3MiOiJzbGFzL3Byb2QvYmNjZl9wcmQiLCJpc3QiOjEsImRudCI6IjAiLCJhdWQiOiJjb21tZXJjZWNsb3VkL3Byb2QvYmNjZl9wcmQiLCJuYmYiOjE3MzIxNzM1NjMsInN0eSI6IlVzZXIiLCJpc2IiOiJ1aWRvOnNsYXM6OnVwbjpHdWVzdDo6dWlkbjpHdWVzdCBVc2VyOjpnY2lkOmFia0pMY1FLUW9XMFdremcxeElsWERqV3lvOjpzZXNiOnNlc3Npb25fYnJpZGdlOjpjaGlkOmJvb3RiYXJuX3VzIiwiZXhwIjoxNzMyMTc1MzkzLCJpYXQiOjE3MzIxNzM1OTMsImp0aSI6IkMyQy0yMDU0MjQ0MDM3MC0xMzU1NzU4MzAxMDg0ODI5MTE5NTE4NzQzNCJ9.BL5FPsmLWPGIyUnnxfvq-1TIjbyDZWfaOYpTKPucpcxQSoEaQ86aMzc7PttVyRgMN7T6GmrXFWMvp7v1DIvkeA; cc-nx-g_bootbarn_us=jeIqmFqxoxigJRKGRzJmxiYiGSBVTmp2FR0UiQPlDfQ; __cq_dnt=0; dw_dnt=0; dwsid=Ri4vv0aGxBSr3M67VLrm8_6mV-3SxlCUnOOgeIVKT8Vo0IaWu1Tq8KMtptAyJNvhp6b2gzEJ_0PNH0EPmZiI9A==; dw=1; dw_cookies_accepted=1; _vis_opt_s=2%7C; _vis_opt_test_cookie=1; GlobalE_Full_Redirect=false; GlobalE_CT_Data=%7B%22CUID%22%3A%7B%22id%22%3A%22720346058.267987225.703%22%2C%22expirationDate%22%3A%22Thu%2C%2021%20Nov%202024%2007%3A50%3A24%20GMT%22%7D%2C%22CHKCUID%22%3Anull%2C%22GA4SID%22%3A822709451%2C%22GA4TS%22%3A1732173624430%2C%22Domain%22%3A%22www.bootbarn.com%22%7D; GlobalE_Ref=https%3A//www.google.com/; _svsid=fc408d0e1e2b35c02fcd536e9b8ef4c9; _li_dcdm_c=.bootbarn.com; _svsidss=fc408d0e1e2b35c02fcd536e9b8ef4c9; _gcl_gs=2.1.k1$i1732174351$u7876001; _vwo_sn=163103%3A10%3A%3A%3A1; _gcl_aw=GCL.1732174463.CjwKCAiArva5BhBiEiwA-oTnXQ3zzxRS_Ftz9NwJpGZ7L9_x80_zv6kkyMu8vMu-xNgxGisiPHolshoCvvEQAvD_BwE; _ga_5S2DVSN1BJ=GS1.1.1732173611.2.1.1732174465.55.0.0; _uetsid=13036ee0a7d911efb17cad26f9b1a2ef; _uetvid=4806c3f0a65d11efa5a6c544a3c695a2',
        'priority': 'u=0, i',
        'referer': 'https://www.google.com/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
    }

    params = {
        'gad_source': '1',
        'gclid': 'CjwKCAiArva5BhBiEiwA-oTnXQ3zzxRS_Ftz9NwJpGZ7L9_x80_zv6kkyMu8vMu-xNgxGisiPHolshoCvvEQAvD_BwE',
    }

    response = requests.get('https://www.bootbarn.com/stores-all', params=params, cookies=cookies, headers=headers)
    pagelink(response,headers,cookies)

if __name__=="__main__":
    main()