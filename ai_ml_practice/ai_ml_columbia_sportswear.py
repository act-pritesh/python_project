from urllib.parse import urljoin

import pymysql
import requests
from parsel import Selector


def handle_db_operations(data_dict):
    """
    Creates the database connection, creates the table if not exists,
    and inserts the data into the database.
    """
    # Establish connection to the MySQL database
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='actowiz',
        database='burger_king',
        charset='utf8mb4'  # utf8mb4 for supporting special characters
    )

    try:
        # Create table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS columbia_sportswear_details (
            name VARCHAR(255) NOT NULL,
            name_xpath TEXT,
            name_html TEXT,
            full_address TEXT,
            full_address_xpath TEXT,
            full_address_html TEXT,
            city VARCHAR(255),
            city_xpath TEXT,
            city_html TEXT,
            state_code VARCHAR(10),
            state_code_xpath TEXT,
            state_code_html TEXT,
            state VARCHAR(100),
            state_xpath TEXT,
            state_html TEXT,
            zip_code VARCHAR(10),
            zip_code_xpath TEXT,
            zip_code_html TEXT,
            direction_url VARCHAR(255),
            direction_url_xpath TEXT,
            direction_url_html TEXT,
            phone_number VARCHAR(50),
            phone_number_xpath TEXT,
            phone_number_html TEXT,
            opening_hours TEXT,
            opening_hours_xpath TEXT,
            opening_hours_html TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """

        with conn.cursor() as cursor:
            cursor.execute(create_table_query)
            conn.commit()
            print("Table created or already exists.")

        # Prepare the insertion query
        insert_query = """
        INSERT INTO columbia_sportswear_details (
            name, name_xpath, name_html, 
            full_address, full_address_xpath, full_address_html, 
            city, city_xpath, city_html, 
            state_code, state_code_xpath, state_code_html, 
            state, state_xpath, state_html, 
            zip_code, zip_code_xpath, zip_code_html, 
            direction_url, direction_url_xpath, direction_url_html, 
            phone_number, phone_number_xpath, phone_number_html, 
            opening_hours, opening_hours_xpath, opening_hours_html
        ) VALUES (
            %(name)s, %(name_xpath)s, %(name_html)s, 
            %(full_address)s, %(full_address_xpath)s, %(full_address_html)s, 
            %(city)s, %(city_xpath)s, %(city_html)s, 
            %(state_code)s, %(state_code_xpath)s, %(state_code_html)s, 
            %(state)s, %(state_xpath)s, %(state_html)s, 
            %(zip_code)s, %(zip_code_xpath)s, %(zip_code_html)s, 
            %(direction_url)s, %(direction_url_xpath)s, %(direction_url_html)s, 
            %(phone_number)s, %(phone_number_xpath)s, %(phone_number_html)s, 
            %(opening_hours)s, %(opening_hours_xpath)s, %(opening_hours_html)s
        )
        """

        # Insert the data into the database
        with conn.cursor() as cursor:
            cursor.execute(insert_query, data_dict)
            conn.commit()
            print("Data inserted successfully.")

    finally:
        # Ensure the connection is closed after operations
        conn.close()
def fourth_link(headers, cookies, full_href):
    response = requests.get(full_href, headers=headers, cookies=cookies)
    parsed_data = Selector(response.text)

    # Extract the name
    name = parsed_data.xpath('//h1[@class="item min-h-[25px] text-2xl font-bold uppercase leading-[25px] text-white"]/text()').get()
    name_xpath ='//h1[@class="item min-h-[25px] text-2xl font-bold uppercase leading-[25px] text-white"]/text()'
    name_html = parsed_data.xpath('//h1[@class="item min-h-[25px] text-2xl font-bold uppercase leading-[25px] text-white"]').get()

    # Extract address-related information
    address = parsed_data.xpath('.//div[@class="mb-8 w-full pr-2 md:mb-0 md:pr-8"]//div[@class="address-line"][1]/span/text()').getall()
    address_xpath ='.//div[@class="mb-8 w-full pr-2 md:mb-0 md:pr-8"]//div[@class="address-line"][1]/span/text()'
    address_html = parsed_data.xpath('.//div[@class="mb-8 w-full pr-2 md:mb-0 md:pr-8"]//div[@class="address-line"]').getall()
    full_address = "".join(address)
    full_address_html=" ".join(address_html)
    city = parsed_data.xpath('.//div[@class="mb-8 w-full pr-2 md:mb-0 md:pr-8"]//div[@class="address-line"][2]/span[1]/text()').get()
    city_xpath ='.//div[@class="mb-8 w-full pr-2 md:mb-0 md:pr-8"]//div[@class="address-line"][2]/span[1]/text()'
    city_html = parsed_data.xpath('.//div[@class="mb-8 w-full pr-2 md:mb-0 md:pr-8"]//div[@class="address-line"]').get()
    state_code = parsed_data.xpath('.//div[@class="mb-8 w-full pr-2 md:mb-0 md:pr-8"]//div[@class="address-line"][2]/abbr/text()').get()
    state_code_xpath ='.//div[@class="mb-8 w-full pr-2 md:mb-0 md:pr-8"]//div[@class="address-line"][2]/abbr/text()'
    state_code_html = parsed_data.xpath('.//div[@class="mb-8 w-full pr-2 md:mb-0 md:pr-8"]//div[@class="address-line"]').get()
    state = parsed_data.xpath('.//div[@class="mb-8 w-full pr-2 md:mb-0 md:pr-8"]//div[@class="address-line"][2]/abbr/@title').get()
    state_xpath ='.//div[@class="mb-8 w-full pr-2 md:mb-0 md:pr-8"]//div[@class="address-line"][2]/abbr/@title'
    state_html = parsed_data.xpath('.//div[@class="mb-8 w-full pr-2 md:mb-0 md:pr-8"]//div[@class="address-line"]').get()
    zip_code = parsed_data.xpath('.//div[@class="mb-8 w-full pr-2 md:mb-0 md:pr-8"]//div[@class="address-line"][2]/span[last()]/text()').get()
    zip_code_xpath ='.//div[@class="mb-8 w-full pr-2 md:mb-0 md:pr-8"]//div[@class="address-line"][2]/span[last()]/text()'
    zip_code_html = parsed_data.xpath('.//div[@class="mb-8 w-full pr-2 md:mb-0 md:pr-8"]//div[@class="address-line"]').get()
    direction_url = parsed_data.xpath('.//div[@class="mb-4 flex items-center space-x-1"]/a/@href').get()
    direction_url_xpath ='.//div[@class="mb-4 flex items-center space-x-1"]/a/@href'
    direction_url_html = parsed_data.xpath('.//div[@class="mb-4 flex items-center space-x-1"]/a').get()
    phone_number = parsed_data.xpath('.//div[@class="mb-4 flex items-center"]/a/text()').get()
    phone_number_xpath ='.//div[@class="mb-4 flex items-center"]/a/text()'
    phone_number_html = parsed_data.xpath('.//div[@class="mb-4 flex items-center"]/a').get()


    # Extract opening hours
    open_hour_datas = parsed_data.xpath('.//div[@class="mb-8 w-full px-2 md:mb-0 md:px-8"]//table//tr')
    open_hour_datas_xpath = './/div[@class="mb-8 w-full px-2 md:mb-0 md:px-8"]//table//tr'
    open_hour_datas_html = parsed_data.xpath('.//div[@class="mb-8 w-full px-2 md:mb-0 md:px-8"]//table//tr').getall()
    full_open_hour_html=" ".join(open_hour_datas_html)
    results = []  # To store formatted day and time strings

    for day_date in open_hour_datas:
        day = day_date.xpath('./td[1]//span/text()').get()
        time = day_date.xpath('./td[2]//span/text()').getall()
        time = [t.strip() for t in time if t.strip()]
        full_time = " ".join(time).strip()
        if not day or not full_time:
            continue
        results.append(f"{day.strip()} - {full_time}")

    opening_hours = " | ".join(results)

    # Create dictionary for the extracted data
    data_dict = {
        "name": name,
        "name_xpath":name_xpath,
        "name_html":name_html,
        "full_address": full_address,
        "full_address_xpath":address_xpath,
        "full_address_html":full_address_html,
        "city": city,
        "city_xpath":city_xpath,
        "city_html":city_html,
        "state_code": state_code,
        "state_code_xpath":state_code_xpath,
        "state_code_html":state_code_html,
        "state": state,
        "state_xpath":state_xpath,
        "state_html":state_html,
        "zip_code": zip_code,
        "zip_code_xpath":zip_code_xpath,
        "zip_code_html":zip_code_html,
        "direction_url": direction_url,
        "direction_url_xpath":direction_url_xpath,
        "direction_url_html":direction_url_html,
        "phone_number": phone_number,
        "phone_number_xpath":phone_number_xpath,
        "phone_number_html":phone_number_html,
        "opening_hours": opening_hours,
        "opening_hours_xpath":open_hour_datas_xpath,
        "opening_hours_html":full_open_hour_html
    }

    print(data_dict)
    handle_db_operations(data_dict)

def third_page_link(headers,cookies,full_href):
    response = requests.get(full_href, headers=headers, cookies=cookies)
    parsed_data = Selector(response.text)
    links=parsed_data.xpath('//a[contains(text(), "View Store Page")]')
    for link in links:
        href=link.xpath('./@href').get()
        full_href = urljoin('https://stores.columbia.com/', href)
        fourth_link(headers,cookies,full_href)


def second_page_link(headers,cookies,full_href):
    response=requests.get(full_href,headers=headers, cookies=cookies)
    parsed_data=Selector(response.text)
    links=parsed_data.xpath('//ul[@class="mx-auto grid max-w-screen-lg grid-cols-1 gap-1 px-4 py-8 sm:grid-cols-2 lg:grid-cols-3 lg:pb-24 lg:pt-12 xl:grid-cols-4"]//li')
    for link in links:
        href=link.xpath('./a/@href').get()
        full_href = urljoin('https://stores.columbia.com/', href)
        third_page_link(headers,cookies,full_href)


def first_page_link(response,headers,cookies):
    parsed_data=Selector(response.text)
    links=parsed_data.xpath('//ul//li[@class="group"]')
    for link in links:
        href=link.xpath('./a/@href').get()
        full_href=urljoin('https://stores.columbia.com/',href)
        name=link.xpath('.//span/text()').get()
        second_page_link(headers,cookies,full_href)

def main():
    cookies = {
        'prev_pt': 'store%20locator',
        'gpv_pn': 'store%20locator%20|%20columbia',
        'kndctr_BA9115F354F6053E0A4C98A4_AdobeOrg_identity': 'CiY2MzAwMjQ3ODcwNTA2NDY1NzE0MDEzNjQ0MjI3NzkwNDM5OTc5MFIQCKzV-8O0MhgBKgNWQTYwAfABrNX7w7Qy',
        'kndctr_BA9115F354F6053E0A4C98A4_AdobeOrg_cluster': 'va6',
        'AMCV_BA9115F354F6053E0A4C98A4%40AdobeOrg': 'MCMID|63002478705064657140136442277904399790',
        'QuantumMetricSessionID': '8bd2107b02c2b61297d77c594b1643c9',
        'QuantumMetricUserID': '09efb8f0d4701d157838dd6259ceabcb',
        'bc_invalidateUrlCache_targeting': '1732088108805',
        'bluecoreNV': 'true',
        '_scid': 'FXZ3baMsJaqOiMaCzuZc9PeLM-j42bHQ',
        '_ScCbts': '%5B%5D',
        '__attentive_id': 'f6b8cfefb6d04af3974dd228f339df27',
        '__attentive_cco': '1732088122712',
        'crl8.fpcuid': '4f40dc41-9987-4d30-aca0-011adf7ca477',
        '__attentive_ss_referrer': 'https://stores.columbia.com/al',
        'tfpsi': '4c4353c3-f60e-41c9-8f70-d7145b59e87e',
        '__attentive_dv': '1',
        '_sctr': '1%7C1732041000000',
        'mt.v': '2.595874080.1732088456121',
        'pxcts': 'c6cd28bc-a712-11ef-bf79-3331fbef9f0c',
        '_pxvid': 'c53b5696-a712-11ef-af41-baabfbabf0ca',
        '__cf_bm': 'GMG66B5twrmlGvKuoIqn4O1kZU9PpdoJPL._hJn5Lg8-1732088456-1.0.1.1-Dzr5yHZPXaSKLj.7LSG0lZ6P.SXqoBKcAfSmeFKzFISTPxyzkb8otsBCMMcjMZHRkz9kkOVdpL1PGfdMPkCbfA',
        '_px3': '6797813f8c6447c953b10333b80656262aaf0cca1e334e832b7e6e80b781d6b9:ERmEliyfDbGL9s8Giw6h2vHVh3uANcfrXS9ZLBjK+y+FJEdJiTiE9MeSJf/V8W32TNEIat0/owiEN8RuYIcw/A==:1000:goC6FUQlYdKKvmff8rP9GbgTov0NawD1D12lpLX2TCyC7d5Pl5KxXiB1JQ/DJihaKmgMmpISk4It09QU6CrTt+LNSht6zPfgN9Do99AG4yiiPQoFvx5NANcTalXHfGn8awvdlm7LZXZSK/1SJFMjh8HLU68ObNKMH2vTWYdfrDG3GvAj+XwsIw5F6pgrGz0B3+eHHHTAtdSspziu2bje2m46UAejrcnPLjiEnXJ1rgE=',
        '__pxvid': 'c75d38ee-a712-11ef-9b30-0242ac120002',
        '__cq_uuid': 'bd3LmllmSaKEjRTJGgbHHvdouA',
        '__cq_seg': '0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00',
        '_gcl_au': '1.1.2105323778.1732088461',
        '_pin_unauth': 'dWlkPVpHSTVaV1EzTlRrdE4yWmlaQzAwTW1abUxUZ3lOV010TVdabFlUbGtNalV3WkdWaQ',
        '_tt_enable_cookie': '1',
        '_ttp': '7LSfxz5Ih95VmBrdnnTO9ozX3ae.tt.1',
        'mp_columbia_us_mixpanel': '%7B%22distinct_id%22%3A%20%2219348848c7927e-03a029b7f7056a-26011851-e1000-19348848c7a4c6%22%2C%22bc_persist_updated%22%3A%201732088466605%2C%22language%22%3A%20%22en_us%22%7D',
        'scarab.visitor': '%22796B773AA1C4641B%22',
        '_pxde': 'e6b278f69bd67118e51e4d4d0d8235ee811f6d1731499b9a00cf462b3bb41b16:eyJ0aW1lc3RhbXAiOjE3MzIwODg0NjY2ODh9',
        '_uetsid': 'ce31bdf0a71211ef886cd32bbcbd06f7',
        '_uetvid': 'ce31ea10a71211ef8ba2076e0886c2ba',
        'mt.sac_25': 't',
        'sn.vi': 'a4b9af51-484f-4e46-a6aa-adc73482e9e2',
        'sn.tpc': '1',
        's_nr30': '1732088507058-New',
        'OptanonConsent': 'isGpcEnabled=0&datestamp=Wed+Nov+20+2024+13%3A11%3A48+GMT%2B0530+(India+Standard+Time)&version=202307.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&genVendors=&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1&AwaitingReconsent=false',
        'mp_dev_mixpanel': '%7B%22distinct_id%22%3A%20%22193487f16ab598-050b6ed714d825-26011851-e1000-193487f16ac291%22%2C%22bc_persist_updated%22%3A%201732088508648%2C%22language%22%3A%20%22en_us%22%7D',
        '_scid_r': 'IvZ3baMsJaqOiMaCzuZc9PeLM-j42bHQid5pNw',
        '__attentive_pv': '4',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        # 'cookie': 'prev_pt=store%20locator; gpv_pn=store%20locator%20|%20columbia; kndctr_BA9115F354F6053E0A4C98A4_AdobeOrg_identity=CiY2MzAwMjQ3ODcwNTA2NDY1NzE0MDEzNjQ0MjI3NzkwNDM5OTc5MFIQCKzV-8O0MhgBKgNWQTYwAfABrNX7w7Qy; kndctr_BA9115F354F6053E0A4C98A4_AdobeOrg_cluster=va6; AMCV_BA9115F354F6053E0A4C98A4%40AdobeOrg=MCMID|63002478705064657140136442277904399790; QuantumMetricSessionID=8bd2107b02c2b61297d77c594b1643c9; QuantumMetricUserID=09efb8f0d4701d157838dd6259ceabcb; bc_invalidateUrlCache_targeting=1732088108805; bluecoreNV=true; _scid=FXZ3baMsJaqOiMaCzuZc9PeLM-j42bHQ; _ScCbts=%5B%5D; __attentive_id=f6b8cfefb6d04af3974dd228f339df27; __attentive_cco=1732088122712; crl8.fpcuid=4f40dc41-9987-4d30-aca0-011adf7ca477; __attentive_ss_referrer=https://stores.columbia.com/al; tfpsi=4c4353c3-f60e-41c9-8f70-d7145b59e87e; __attentive_dv=1; _sctr=1%7C1732041000000; mt.v=2.595874080.1732088456121; pxcts=c6cd28bc-a712-11ef-bf79-3331fbef9f0c; _pxvid=c53b5696-a712-11ef-af41-baabfbabf0ca; __cf_bm=GMG66B5twrmlGvKuoIqn4O1kZU9PpdoJPL._hJn5Lg8-1732088456-1.0.1.1-Dzr5yHZPXaSKLj.7LSG0lZ6P.SXqoBKcAfSmeFKzFISTPxyzkb8otsBCMMcjMZHRkz9kkOVdpL1PGfdMPkCbfA; _px3=6797813f8c6447c953b10333b80656262aaf0cca1e334e832b7e6e80b781d6b9:ERmEliyfDbGL9s8Giw6h2vHVh3uANcfrXS9ZLBjK+y+FJEdJiTiE9MeSJf/V8W32TNEIat0/owiEN8RuYIcw/A==:1000:goC6FUQlYdKKvmff8rP9GbgTov0NawD1D12lpLX2TCyC7d5Pl5KxXiB1JQ/DJihaKmgMmpISk4It09QU6CrTt+LNSht6zPfgN9Do99AG4yiiPQoFvx5NANcTalXHfGn8awvdlm7LZXZSK/1SJFMjh8HLU68ObNKMH2vTWYdfrDG3GvAj+XwsIw5F6pgrGz0B3+eHHHTAtdSspziu2bje2m46UAejrcnPLjiEnXJ1rgE=; __pxvid=c75d38ee-a712-11ef-9b30-0242ac120002; __cq_uuid=bd3LmllmSaKEjRTJGgbHHvdouA; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; _gcl_au=1.1.2105323778.1732088461; _pin_unauth=dWlkPVpHSTVaV1EzTlRrdE4yWmlaQzAwTW1abUxUZ3lOV010TVdabFlUbGtNalV3WkdWaQ; _tt_enable_cookie=1; _ttp=7LSfxz5Ih95VmBrdnnTO9ozX3ae.tt.1; mp_columbia_us_mixpanel=%7B%22distinct_id%22%3A%20%2219348848c7927e-03a029b7f7056a-26011851-e1000-19348848c7a4c6%22%2C%22bc_persist_updated%22%3A%201732088466605%2C%22language%22%3A%20%22en_us%22%7D; scarab.visitor=%22796B773AA1C4641B%22; _pxde=e6b278f69bd67118e51e4d4d0d8235ee811f6d1731499b9a00cf462b3bb41b16:eyJ0aW1lc3RhbXAiOjE3MzIwODg0NjY2ODh9; _uetsid=ce31bdf0a71211ef886cd32bbcbd06f7; _uetvid=ce31ea10a71211ef8ba2076e0886c2ba; mt.sac_25=t; sn.vi=a4b9af51-484f-4e46-a6aa-adc73482e9e2; sn.tpc=1; s_nr30=1732088507058-New; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Nov+20+2024+13%3A11%3A48+GMT%2B0530+(India+Standard+Time)&version=202307.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&genVendors=&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1&AwaitingReconsent=false; mp_dev_mixpanel=%7B%22distinct_id%22%3A%20%22193487f16ab598-050b6ed714d825-26011851-e1000-193487f16ac291%22%2C%22bc_persist_updated%22%3A%201732088508648%2C%22language%22%3A%20%22en_us%22%7D; _scid_r=IvZ3baMsJaqOiMaCzuZc9PeLM-j42bHQid5pNw; __attentive_pv=4',
        # 'if-modified-since': 'Mon, 18 Nov 2024 15:19:13 GMT',
        # 'if-none-match': 'W/"To8lsYvM80Js3iwn8J2WUuoTQUHrNd5l8kKE2Gr8jT5IWf0WyMz1bW7wQATmP8Hb2kHFCBpAiEzx4j2JK4qyiQ=="',
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
    response = requests.get('https://stores.columbia.com/', cookies=cookies, headers=headers)
    first_page_link(response,headers,cookies)

if __name__=="__main__":
    main()