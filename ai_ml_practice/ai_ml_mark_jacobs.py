
from urllib.parse import urljoin

import pymysql
import requests
from parsel import Selector

def connect_db():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='actowiz',
        database='burger_king',
    )
    return connection

def create_table():
    """
    Function to create the table if it does not exist.
    """
    connection = connect_db()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS mark_jacobs_details (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        name_xpath VARCHAR(255),
        name_html TEXT,
        street_address VARCHAR(255),
        street_address_xpath VARCHAR(255),
        street_address_html TEXT,
        state VARCHAR(255),
        state_xpath VARCHAR(255),
        state_html TEXT,
        country_code VARCHAR(255),
        country_code_xpath VARCHAR(255),
        country_code_html TEXT,
        postal_code VARCHAR(20),
        postal_code_xpath VARCHAR(255),
        postal_code_html TEXT,
        country VARCHAR(255),
        country_xpath VARCHAR(255),
        country_html TEXT,
        direction_url TEXT,
        direction_url_xpath VARCHAR(255),
        direction_url_html TEXT,
        phone_number VARCHAR(20),
        phone_number_xpath VARCHAR(255),
        phone_number_html TEXT,
        email VARCHAR(255),
        email_xpath VARCHAR(255),
        email_html TEXT,
        open_hour TEXT,
        open_hour_xpath VARCHAR(255),
        open_hour_html TEXT
    );
    """
    with connection.cursor() as cursor:
        cursor.execute(create_table_query)
        connection.commit()

def insert_data_into_db( data):
    """
    Function to insert data into the database.
    """
    connection = connect_db()
    insert_query = """
    INSERT INTO mark_jacobs_details (
        name, name_xpath, name_html,
        street_address, street_address_xpath, street_address_html,
        state, state_xpath, state_html,
        country_code, country_code_xpath, country_code_html,
        postal_code, postal_code_xpath, postal_code_html,
        country, country_xpath, country_html,
        direction_url, direction_url_xpath, direction_url_html,
        phone_number, phone_number_xpath, phone_number_html,
        email, email_xpath, email_html,
        open_hour, open_hour_xpath, open_hour_html
    ) VALUES (
        %(name)s, %(name_xpath)s, %(name_html)s,
        %(street_address)s, %(street_address_xpath)s, %(street_address_html)s,
        %(state)s, %(state_xpath)s, %(state_html)s,
        %(country_code)s, %(country_code_xpath)s, %(country_code_html)s,
        %(postal_code)s, %(postal_code_xpath)s, %(postal_code_html)s,
        %(country)s, %(country_xpath)s, %(country_html)s,
        %(direction_url)s, %(direction_url_xpath)s, %(direction_url_html)s,
        %(phone_number)s, %(phone_number_xpath)s, %(phone_number_html)s,
        %(email)s, %(email_xpath)s, %(email_html)s,
        %(open_hour)s, %(open_hour_xpath)s, %(open_hour_html)s
    );
    """
    with connection.cursor() as cursor:
        cursor.execute(insert_query, data)
        connection.commit()

def pagedata(fullhref, headers, cookies):
    """
    Fetch and parse data, then insert it into the database.
    """

    response = requests.get(fullhref, headers=headers, cookies=cookies)
    parsed_data = Selector(response.text)
    details = parsed_data.xpath('//address[@class="detail-address"]')
    create_table()
    for detail in details:
        # Extract fields as in your original function
        name = detail.xpath('./h2/text()').get()
        name_xpath = './h2/text()'
        name_html = detail.xpath('./h2').get()
        street_address = detail.xpath('./span[@itemprop="streetAddress"]/text()').get()
        street_address_xpath = './span[@itemprop="streetAddress"]/text()'
        street_address_html = detail.xpath('./span[@itemprop="streetAddress"]').get()
        state = detail.xpath('./span[@itemprop="addressLocality"]/text()').get()
        state_xpath = './span[@itemprop="addressLocality"]/text()'
        state_html = detail.xpath('./span[@itemprop="addressLocality"]').get()
        country_code = detail.xpath('./span[@itemprop="addressRegion"]/text()').get()
        country_code_xpath = './span[@itemprop="addressRegion"]/text()'
        country_code_html = detail.xpath('./span[@itemprop="addressRegion"]').get()
        postal_code = detail.xpath('./span[@itemprop="postalCode"]/text()').get()
        postal_code_xpath = './span[@itemprop="postalCode"]/text()'
        postal_code_html = detail.xpath('./span[@itemprop="postalCode"]').get()
        country = detail.xpath('./span[@itemprop="addressCountry"]/text()').get()
        country_xpath = './span[@itemprop="addressCountry"]/text()'
        country_html = detail.xpath('./span[@itemprop="addressCountry"]').get()
        direction_url = detail.xpath('./a[@class="btn btn-secondary"]/@href').get()
        direction_url_xpath = './a[@class="btn btn-secondary"]'
        direction_url_html = detail.xpath('./a[@class="btn btn-secondary"]').get()
        phone_number = detail.xpath('./a[@itemprop="telephone"]/text()').get()
        phone_number_xpath = './a[@itemprop="telephone"]/text()'
        phone_number_html = detail.xpath('./a[@itemprop="telephone"]').get()
        email = detail.xpath('./a[@itemprop="email"]/text()').get()
        email_xpath = './a[@itemprop="email"]/text()'
        email_html = detail.xpath('./a[@itemprop="email"]').get()
        open_hour = detail.xpath('//div[@class="detail-hours"]//p/text()').getall()
        open_hour_xpath = '//div[@class="detail-hours"]//p/text()'
        open_hour_html = detail.xpath('//div[@class="detail-hours"]//p').getall()
        final_open_hour_html = "".join(open_hour_html)
        final_open_hour = " | ".join([item.replace('\n', '').strip() for item in open_hour])

        data = {
            "name": name if name else "N/A",
            "name_xpath": name_xpath,
            "name_html": name_html,
            "street_address": street_address if street_address else "N/A",
            "street_address_xpath": street_address_xpath,
            "street_address_html": street_address_html,
            "state": state if state else "N/A",
            "state_xpath": state_xpath,
            "state_html": state_html,
            "country_code": country_code if country_code else "N/A",
            "country_code_xpath": country_code_xpath,
            "country_code_html": country_code_html,
            "postal_code": postal_code if postal_code else "N/A",
            "postal_code_xpath": postal_code_xpath,
            "postal_code_html": postal_code_html,
            "country": country if country else "N/A",
            "country_xpath": country_xpath,
            "country_html": country_html,
            "direction_url": direction_url if direction_url else "N/A",
            "direction_url_xpath": direction_url_xpath,
            "direction_url_html": direction_url_html,
            "phone_number": phone_number if phone_number else "N/A",
            "phone_number_xpath": phone_number_xpath,
            "phone_number_html": phone_number_html,
            "email": email.strip() if email else "N/A",
            "email_xpath": email_xpath,
            "email_html": email_html,
            "open_hour": final_open_hour if final_open_hour else "N/A",
            "open_hour_xpath": open_hour_xpath,
            "open_hour_html": final_open_hour_html
        }
        print(name)
        # Insert data into the database
        insert_data_into_db(data)

def pagelink(response,headers,cookies):
    parsed_data=Selector(response.text)
    box=parsed_data.xpath('//section[@class="storelist__content storelist__content-na js-tabs__content storelist__content--active"]//div[@class="store-card g-col-12 g-col-md-4"]//div[@class="store-details"]')
    # print(box)
    for link in box:
        href=link.xpath('.//a[contains(@class, "storeDetails-btn")]/@href').get()
        fullhref=urljoin('https://www.marcjacobs.com/',href)
        pagedata(fullhref,headers,cookies)

def main():
    start = 0
    increment=6
    cookies = {
        'sid': 'SA8zNUDUPU3gl4g546Bnh5uZKscWHNMvpRw',
        'cqcid': 'bd3LmllmSaKEjRTJGgbHHvdouA',
        'cquid': '||',
        'dwsid': 'dDxkewnBc925079G_zN7N6eqfYlfCZ2__FhmrzyXiNNA1cTmiuViU5AutCdw7zyb6XAHUBjmuXa9nnxvwJZbXA==',
        'dw_dnt': '0',
        '__cq_dnt': '0',
        'GlobalE_Data': '%7B%22countryISO%22%3A%22MT%22%2C%22cultureCode%22%3A%22en-GB%22%2C%22currencyCode%22%3A%22EUR%22%2C%22apiVersion%22%3A%222.1.4%22%7D',
        'edgio_experiment': 'control',
        'x-edg-experiments': '14',
        'dwac_1b8b4169444398a5bd71b5531a': 'SA8zNUDUPU3gl4g546Bnh5uZKscWHNMvpRw%3D|dw-only|||USD|false|US%2FEastern|true',
        'dwanonymous_925c5c911dedc4dc1a345433a8c82587': 'bd3LmllmSaKEjRTJGgbHHvdouA',
        'AKA_A2': 'A',
        'c_uuid': '250100646453736130000537365720128024',
        'GlobalE_Welcome_Data': '%7B%22showWelcome%22%3Afalse%7D',
        '2c.cId': '673c26db8f60133c735b1ca8',
        '__cq_uuid': 'bd3LmllmSaKEjRTJGgbHHvdouA',
        '__cq_seg': '0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00',
        'liveagent_oref': 'https://www.google.com/',
        'GlobalE_Full_Redirect': 'false',
        'liveagent_sid': 'bf0d2f57-030e-4901-8d00-035f5a8e6ff1',
        'liveagent_vc': '2',
        'liveagent_ptid': 'bf0d2f57-030e-4901-8d00-035f5a8e6ff1',
        'marcjacobs_clarip_consent': '0,1,2,3',
        'explicit_cookie_consent_provided': 'Y',
        'xgen_user_id': 'vzkbyk7fonsm3o1byjg',
        'xgen_session_id': 'a9022a09-3e83-4141-a037-d58d1e67d87c',
        '_ga': 'GA1.1.1041170279.1731995383',
        '_gcl_au': '1.1.140555475.1731995383',
        '_scid': '-l5-_N_-XFIRFqxRZjoMJhxjOncuJNgE',
        '_fbp': 'fb.1.1731995384466.463628601199527607',
        '_ScCbts': '%5B%5D',
        'sa-r-source': 'www.google.com',
        'sa-user-id': 's%253A0-5324fb6d-d92a-5aa5-7850-7af775920b92.TQKXmkJFX7PhQmInCQ6S9k%252FtkMUmTqA%252B3vElRUKZRq4',
        'sa-user-id-v2': 's%253AUyT7bdkqWqV4UHr3dZILkrnm--g.MGjQGVb%252FG%252FM99vM1H%252FQf3YHSurxpG%252BUXuWH6E9eb9R8',
        'sa-user-id-v3': 's%253AAQAKIEFuuQXet_BAaWR8sm-2hHIIllCSQhmimQS6rdseSwL5EAEYAyCszbG2BjABOgT9KkGsQgT5Ie-_.KgXeenc5lejl9E%252FlgoU%252BI2KD%252FOPN0Zub7rK2EI3AvsM',
        '__qca': 'P0-853475356-1731995384835',
        'xgen_ab_info': '{"testing_group_name":"Inactive"}',
        'xgen_meta_data': '{"user_type":"new_user","access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21lcl9pZCI6IjA2MjMyNzc5MzhiNmViM2FlZTdkYTJjZmQ0YzZhNmJiIiwiZXhwIjoxNzMyMDM4NTgzLCJ1c2VyX2lkIjoidnprYnlrN2ZvbnNtM28xYnlqZyJ9.q40CtZQnWs1nptQSTRlmwdTp-A8rtscS0uaoKSnHD-M","expiration_date":"2024-11-19T17:49:43"}',
        'bm_mi': 'BED9A5B5C026B9723B525C14A7669DE8~YAAQiLEXAlsAKzGTAQAAVyv5Qhl/Da3DkDCy/ZKIRzc9fVS0R+0lyCF6iUncjdH9x68KaIXJd0HYUW593aJtTdpJXhK9C8xMu7QqjqRENK/uIlB1XqPUrQZcBtrPLjZh00DEQdGW5tbS9409pUcZ3j826ayy4jgDusHtPeVk4MwhPdqahtkSDGRiI75hV+A3ZuwEDr/pfwoAVz6PM81tVNtUOKwwA3U7GUqKCTXc5HqBz14X8qySVqkDO4MqoGcMlpNe8SLFBR7Je3uSl4wBW7rdVD42EDWocbrKTPurMRRuIroC9r3fSIf+RiLW6chpdtJBV1YTdQBW4XQstHCMepJFUA==~1',
        'bm_sv': 'F9F317E1FC51277D5B45CDBF42E646BF~YAAQiLEXAqoCKzGTAQAAaVv5QhlpVaf7U1U7FpBU6+s2hiNFPp/rEqZ1TNqO4szdZMWm4l4R4bGKzyqZyIv1y1rUKT/5fBcEG13pNNBzqs0EYnfFmNUqs+L2dFAomOpNJ8LV3+yjobI8wVRKDJVEXYbcsNYC8tvWRbuzVpLLyzHiwJjEoQ6hURoqrEUBUH1scDtQeSVEi2hODRIHZORoYlqJWVuJA4P1Mf/CNNysO54UMfXaw5HH6d2kXu/Iy61hoAlOVA4=~1',
        'ak_bmsc': '243E20DCEAED5EFC472DF37D0DC939A8~000000000000000000000000000000~YAAQhbEXAhmSfyuTAQAA9rEEQxlb9bw+r02rEPkWyYC5hzRjgKJXWoNvHZNb5E72vZNg3OL1qz1mS36fowbOQdHWyFXmv9P8PGFApoUzPg6fWVtnyF51GFZ3FOc09LpCJVvzjJcLcxLQOh1BV7pM75NuMKpyEGKYz5gUU5F6y2pdYo1gQa+y4LaoX+f9apHvEx5l6n07uQE8jkDdtGh/wKxCHvoOS2r1SB4yNqkcxZfcJ/yuc4Z4MCcIJXqB5nQdYLKmZF7kV7EOGznarlK14WO4QxCTJdPA5pWtEZVJpIKPqA6TAsLb29ohkg1IOsOJdk6+rLKPNHDgLQIJXpKqGjiZRzjHHASwo2gnaRFsaXWdxPx5O5AIVGyPms937j82whHSgb4wI75weXdwa0OfplaA/waoQghoh3B9U4VROGdTL7pPGrmWv9jmqLBqT5zA43GQXAOJCPydVGsYFP2xhCRk59h6C/YUCS1c/U4FAoYo8eygylvM7RGv2bvTKEgufFLQ4IB8d1rVgJn2c0EFa/AL',
        'GlobalE_CT_Data': '%7B%22CUID%22%3A%7B%22id%22%3A%22314581766.765739895.494%22%2C%22expirationDate%22%3A%22Tue%2C%2019%20Nov%202024%2006%3A49%3A38%20GMT%22%7D%2C%22CHKCUID%22%3Anull%2C%22GA4SID%22%3A519252761%2C%22GA4TS%22%3A1731997178646%2C%22Domain%22%3A%22www.marcjacobs.com%22%7D',
        'GlobalE_Ref': 'https%3A//www.google.com/',
        'RT': '"z=1&dm=www.marcjacobs.com&si=09099f10-0af9-454b-98e4-c65b45a838e3&ss=m3o1zcp0&sl=6&tt=asp&obo=4&rl=1"',
        'bm_sz': '1AC0D3DE790DDD6AFA2BB5B057231AC7~YAAQiLEXAgzsLDGTAQAA6LEaQxnSrwQALaAoXXb6kxBu9LJ9Y/cVEKWXdYld7OSVa1Rjsz5cmWiaLjEz8Fg7CKf8+BpuO+xIpG5DIciSyluwJj/JSfIaw3dh11xf0U/7N7y71lcHurEvk4srshYQRGvHCfX8o+BT1E2iy5JyeZZdel4IWhWeAND2Nkrohg4HcOBZ3DoQkDL3EZCKwdoY02nljRVqP0Q/2jloPH0lzuB5Ap3t0Pd3nh0c04fIV5HSvm5oqyH9Tz/dHarN4IjemLjw2D+6TatidIYinW7FdbR0BqnT4AVMtik/mFOO6pOTgi9s5Tqym9qaD1E72492IzGzoy39bW4OwWr6HbpVlLBDJv9zN6cpbzUfS/zZ4easAYDhVQ1fYEeyUWD9nqqNdYduWJpyGigMWAlTDmrHWsNbqnJvK/OKvm4fc8I2DEKnlv2aFdhN6lZEinvAoWWp23/5az5m4zZwMw6d6orXS5ffbjfDCFQ9Kxd+nvBhAVV2RSyiPLNnF34W6NXL29cSYLuTIuudobuIVC49owGO1Yqp9bMsxfsTgym7y3I7YHCptQ==~3687233~3616821',
        '_scid_r': 'DN5-_N_-XFIRFqxRZjoMJhxjOncuJNgEISIZbg',
        '_uetsid': '13df5380a63a11efbcf8fd766dc4c205',
        '_uetvid': '13dfa2f0a63a11ef90ec51f0edbf3fc9',
        'sa-r-date': '2024-11-19T06:27:27.877Z',
        'shq': '638675944476125689%5E019342f7-d9ab-4574-b13b-4356b66e5344%5E019342f7-d9ab-4970-9d84-e267464d47c9%5E0%5E31.171.130.18',
        '_ga_QLHB95L78F': 'GS1.1.1731995383.1.1.1731997705.0.0.776309321',
        '_abck': 'B534A3B3EA66BEBEEB575D5A7966A7FB~-1~YAAQiLEXArMRLTGTAQAAfBUdQwxTjnEZB95+KcDZjbE2oe7IHGOmP6cCUtDZVBt/T0WJ81xMByO+1kwcn+cjLZINFbrgunkEoMqRIe/Jrqe7xHrS38woqqdgXQJWrcaF2KiDskurFIU+gx07a1Lgf6C76/pBcXVRu3STZefbWVdvQHybySQ+jdG0iQ4YNtdmWRoXdLUeWGtB9jREOiQhdA9jG+8svXdfqbpT7Oxf2arF0CRh907n1fhrxnphGVfftfavzsz4Ll/a4kgFeEIBt16YF/PeBmlvAGQSVskNPJtF2RTDtV0XPj7Ln7XKr5467rtSoninRclYjGuudy9z7As4+Et752FlyByYtHAPUp60QCuykrbEdiGO0zx+YDrUBizw02fi7ytkW2ZPKocijJkYibC8rlMVjsbSkvft+zr8SqTptRl/9+Rbl3PjpGtL/6gGQhbh+IEaBPcq/UtMMGt5R6X2esE4kUNRiDXxbCZ4ZfblSm43xUVT5NUj38HdsbhaPxUWZ67k7SnIKFerWAcW/ToJj+l57V5b8dC6XZlbCII4ZzAkV71wwpurdKXKtiilxWnuAaYoVopSSf3buuVedoIDOGnMCfvn9eJH0zFi+tciXzz+TZMcLGndi+qWjbshn+8SZQWLrgksJD8UudL/fh+/+mohyIlaWf62XcOvM3anS/0bWRiR0+SG+krdexiVqlC8ZBkDFRA0lolKoPOxRoOGJHHCRNlcDqTRyv0qRKDrAVk=~-1~-1~1731999047',
    }
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        # 'cookie': 'sid=SA8zNUDUPU3gl4g546Bnh5uZKscWHNMvpRw; cqcid=bd3LmllmSaKEjRTJGgbHHvdouA; cquid=||; dwsid=dDxkewnBc925079G_zN7N6eqfYlfCZ2__FhmrzyXiNNA1cTmiuViU5AutCdw7zyb6XAHUBjmuXa9nnxvwJZbXA==; dw_dnt=0; __cq_dnt=0; GlobalE_Data=%7B%22countryISO%22%3A%22MT%22%2C%22cultureCode%22%3A%22en-GB%22%2C%22currencyCode%22%3A%22EUR%22%2C%22apiVersion%22%3A%222.1.4%22%7D; edgio_experiment=control; x-edg-experiments=14; dwac_1b8b4169444398a5bd71b5531a=SA8zNUDUPU3gl4g546Bnh5uZKscWHNMvpRw%3D|dw-only|||USD|false|US%2FEastern|true; dwanonymous_925c5c911dedc4dc1a345433a8c82587=bd3LmllmSaKEjRTJGgbHHvdouA; AKA_A2=A; c_uuid=250100646453736130000537365720128024; GlobalE_Welcome_Data=%7B%22showWelcome%22%3Afalse%7D; 2c.cId=673c26db8f60133c735b1ca8; __cq_uuid=bd3LmllmSaKEjRTJGgbHHvdouA; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; liveagent_oref=https://www.google.com/; GlobalE_Full_Redirect=false; liveagent_sid=bf0d2f57-030e-4901-8d00-035f5a8e6ff1; liveagent_vc=2; liveagent_ptid=bf0d2f57-030e-4901-8d00-035f5a8e6ff1; marcjacobs_clarip_consent=0,1,2,3; explicit_cookie_consent_provided=Y; xgen_user_id=vzkbyk7fonsm3o1byjg; xgen_session_id=a9022a09-3e83-4141-a037-d58d1e67d87c; _ga=GA1.1.1041170279.1731995383; _gcl_au=1.1.140555475.1731995383; _scid=-l5-_N_-XFIRFqxRZjoMJhxjOncuJNgE; _fbp=fb.1.1731995384466.463628601199527607; _ScCbts=%5B%5D; sa-r-source=www.google.com; sa-user-id=s%253A0-5324fb6d-d92a-5aa5-7850-7af775920b92.TQKXmkJFX7PhQmInCQ6S9k%252FtkMUmTqA%252B3vElRUKZRq4; sa-user-id-v2=s%253AUyT7bdkqWqV4UHr3dZILkrnm--g.MGjQGVb%252FG%252FM99vM1H%252FQf3YHSurxpG%252BUXuWH6E9eb9R8; sa-user-id-v3=s%253AAQAKIEFuuQXet_BAaWR8sm-2hHIIllCSQhmimQS6rdseSwL5EAEYAyCszbG2BjABOgT9KkGsQgT5Ie-_.KgXeenc5lejl9E%252FlgoU%252BI2KD%252FOPN0Zub7rK2EI3AvsM; __qca=P0-853475356-1731995384835; xgen_ab_info={"testing_group_name":"Inactive"}; xgen_meta_data={"user_type":"new_user","access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21lcl9pZCI6IjA2MjMyNzc5MzhiNmViM2FlZTdkYTJjZmQ0YzZhNmJiIiwiZXhwIjoxNzMyMDM4NTgzLCJ1c2VyX2lkIjoidnprYnlrN2ZvbnNtM28xYnlqZyJ9.q40CtZQnWs1nptQSTRlmwdTp-A8rtscS0uaoKSnHD-M","expiration_date":"2024-11-19T17:49:43"}; bm_mi=BED9A5B5C026B9723B525C14A7669DE8~YAAQiLEXAlsAKzGTAQAAVyv5Qhl/Da3DkDCy/ZKIRzc9fVS0R+0lyCF6iUncjdH9x68KaIXJd0HYUW593aJtTdpJXhK9C8xMu7QqjqRENK/uIlB1XqPUrQZcBtrPLjZh00DEQdGW5tbS9409pUcZ3j826ayy4jgDusHtPeVk4MwhPdqahtkSDGRiI75hV+A3ZuwEDr/pfwoAVz6PM81tVNtUOKwwA3U7GUqKCTXc5HqBz14X8qySVqkDO4MqoGcMlpNe8SLFBR7Je3uSl4wBW7rdVD42EDWocbrKTPurMRRuIroC9r3fSIf+RiLW6chpdtJBV1YTdQBW4XQstHCMepJFUA==~1; bm_sv=F9F317E1FC51277D5B45CDBF42E646BF~YAAQiLEXAqoCKzGTAQAAaVv5QhlpVaf7U1U7FpBU6+s2hiNFPp/rEqZ1TNqO4szdZMWm4l4R4bGKzyqZyIv1y1rUKT/5fBcEG13pNNBzqs0EYnfFmNUqs+L2dFAomOpNJ8LV3+yjobI8wVRKDJVEXYbcsNYC8tvWRbuzVpLLyzHiwJjEoQ6hURoqrEUBUH1scDtQeSVEi2hODRIHZORoYlqJWVuJA4P1Mf/CNNysO54UMfXaw5HH6d2kXu/Iy61hoAlOVA4=~1; ak_bmsc=243E20DCEAED5EFC472DF37D0DC939A8~000000000000000000000000000000~YAAQhbEXAhmSfyuTAQAA9rEEQxlb9bw+r02rEPkWyYC5hzRjgKJXWoNvHZNb5E72vZNg3OL1qz1mS36fowbOQdHWyFXmv9P8PGFApoUzPg6fWVtnyF51GFZ3FOc09LpCJVvzjJcLcxLQOh1BV7pM75NuMKpyEGKYz5gUU5F6y2pdYo1gQa+y4LaoX+f9apHvEx5l6n07uQE8jkDdtGh/wKxCHvoOS2r1SB4yNqkcxZfcJ/yuc4Z4MCcIJXqB5nQdYLKmZF7kV7EOGznarlK14WO4QxCTJdPA5pWtEZVJpIKPqA6TAsLb29ohkg1IOsOJdk6+rLKPNHDgLQIJXpKqGjiZRzjHHASwo2gnaRFsaXWdxPx5O5AIVGyPms937j82whHSgb4wI75weXdwa0OfplaA/waoQghoh3B9U4VROGdTL7pPGrmWv9jmqLBqT5zA43GQXAOJCPydVGsYFP2xhCRk59h6C/YUCS1c/U4FAoYo8eygylvM7RGv2bvTKEgufFLQ4IB8d1rVgJn2c0EFa/AL; GlobalE_CT_Data=%7B%22CUID%22%3A%7B%22id%22%3A%22314581766.765739895.494%22%2C%22expirationDate%22%3A%22Tue%2C%2019%20Nov%202024%2006%3A49%3A38%20GMT%22%7D%2C%22CHKCUID%22%3Anull%2C%22GA4SID%22%3A519252761%2C%22GA4TS%22%3A1731997178646%2C%22Domain%22%3A%22www.marcjacobs.com%22%7D; GlobalE_Ref=https%3A//www.google.com/; RT="z=1&dm=www.marcjacobs.com&si=09099f10-0af9-454b-98e4-c65b45a838e3&ss=m3o1zcp0&sl=6&tt=asp&obo=4&rl=1"; bm_sz=1AC0D3DE790DDD6AFA2BB5B057231AC7~YAAQiLEXAgzsLDGTAQAA6LEaQxnSrwQALaAoXXb6kxBu9LJ9Y/cVEKWXdYld7OSVa1Rjsz5cmWiaLjEz8Fg7CKf8+BpuO+xIpG5DIciSyluwJj/JSfIaw3dh11xf0U/7N7y71lcHurEvk4srshYQRGvHCfX8o+BT1E2iy5JyeZZdel4IWhWeAND2Nkrohg4HcOBZ3DoQkDL3EZCKwdoY02nljRVqP0Q/2jloPH0lzuB5Ap3t0Pd3nh0c04fIV5HSvm5oqyH9Tz/dHarN4IjemLjw2D+6TatidIYinW7FdbR0BqnT4AVMtik/mFOO6pOTgi9s5Tqym9qaD1E72492IzGzoy39bW4OwWr6HbpVlLBDJv9zN6cpbzUfS/zZ4easAYDhVQ1fYEeyUWD9nqqNdYduWJpyGigMWAlTDmrHWsNbqnJvK/OKvm4fc8I2DEKnlv2aFdhN6lZEinvAoWWp23/5az5m4zZwMw6d6orXS5ffbjfDCFQ9Kxd+nvBhAVV2RSyiPLNnF34W6NXL29cSYLuTIuudobuIVC49owGO1Yqp9bMsxfsTgym7y3I7YHCptQ==~3687233~3616821; _scid_r=DN5-_N_-XFIRFqxRZjoMJhxjOncuJNgEISIZbg; _uetsid=13df5380a63a11efbcf8fd766dc4c205; _uetvid=13dfa2f0a63a11ef90ec51f0edbf3fc9; sa-r-date=2024-11-19T06:27:27.877Z; shq=638675944476125689%5E019342f7-d9ab-4574-b13b-4356b66e5344%5E019342f7-d9ab-4970-9d84-e267464d47c9%5E0%5E31.171.130.18; _ga_QLHB95L78F=GS1.1.1731995383.1.1.1731997705.0.0.776309321; _abck=B534A3B3EA66BEBEEB575D5A7966A7FB~-1~YAAQiLEXArMRLTGTAQAAfBUdQwxTjnEZB95+KcDZjbE2oe7IHGOmP6cCUtDZVBt/T0WJ81xMByO+1kwcn+cjLZINFbrgunkEoMqRIe/Jrqe7xHrS38woqqdgXQJWrcaF2KiDskurFIU+gx07a1Lgf6C76/pBcXVRu3STZefbWVdvQHybySQ+jdG0iQ4YNtdmWRoXdLUeWGtB9jREOiQhdA9jG+8svXdfqbpT7Oxf2arF0CRh907n1fhrxnphGVfftfavzsz4Ll/a4kgFeEIBt16YF/PeBmlvAGQSVskNPJtF2RTDtV0XPj7Ln7XKr5467rtSoninRclYjGuudy9z7As4+Et752FlyByYtHAPUp60QCuykrbEdiGO0zx+YDrUBizw02fi7ytkW2ZPKocijJkYibC8rlMVjsbSkvft+zr8SqTptRl/9+Rbl3PjpGtL/6gGQhbh+IEaBPcq/UtMMGt5R6X2esE4kUNRiDXxbCZ4ZfblSm43xUVT5NUj38HdsbhaPxUWZ67k7SnIKFerWAcW/ToJj+l57V5b8dC6XZlbCII4ZzAkV71wwpurdKXKtiilxWnuAaYoVopSSf3buuVedoIDOGnMCfvn9eJH0zFi+tciXzz+TZMcLGndi+qWjbshn+8SZQWLrgksJD8UudL/fh+/+mohyIlaWf62XcOvM3anS/0bWRiR0+SG+krdexiVqlC8ZBkDFRA0lolKoPOxRoOGJHHCRNlcDqTRyv0qRKDrAVk=~-1~-1~1731999047',
        'priority': 'u=1, i',
        'referer': 'https://www.marcjacobs.com/mt-en/stores?srsltid=AfmBOoprc4cBpQClpscWs9Dxiz7O7S640wdLTrWyj48FhnUZFmhV0oQ8',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    while True:
        params = {
            'showMap': 'false',
            'region': 'NA',
            'countryCode': 'US',
            'startIndex': start,
        }
        response = requests.get('https://www.marcjacobs.com/mt-en/stores', params=params, cookies=cookies, headers=headers)
        if response.status_code==200:
            pagelink(response,headers,cookies)
        else:
            print('response not available')

        start+=increment
        # Stop if no more data is returned
        parsed_data = Selector(response.text)
        if not parsed_data.xpath(
                '//section[@class="storelist__content storelist__content-na js-tabs__content storelist__content--active"]//div[@class="store-card g-col-12 g-col-md-4"]'):
            break

if __name__=="__main__":
    main()