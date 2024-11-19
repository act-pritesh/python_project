import pymysql
import requests
from parsel import Selector

import pymysql


def create_table_and_insert(details):
    # Database connection configuration
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='actowiz',
        database='burger_king',
    )
    # Establish connection to the MySQL database
    cursor = connection.cursor()

    # Create the table if it doesn't already exist
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS lk_bennett_details (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        name_xpath TEXT,
        name_html TEXT,
        address VARCHAR(255),
        address_xpath TEXT,
        address_html TEXT,
        number VARCHAR(20),
        number_xpath TEXT,
        number_html TEXT
    )
    '''
    cursor.execute(create_table_query)

    # Insert data into the table
    insert_query = '''
    INSERT INTO lk_bennett_details (name, name_xpath, name_html, address, address_xpath, address_html, number, number_xpath, number_html)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cursor.execute(insert_query, (
        details["name"],
        details["name_xpath"],
        details["name_html"],
        details["address"],
        details["address_xpath"],
        details["address_html"],
        details["number"],
        details["number_xpath"],
        details["number_html"]
    ))

    # Commit the transaction and close the connection
    connection.commit()
    cursor.close()
    connection.close()
    print("Data inserted successfully!")

def pagedata(response):
    parsed_data=Selector(response.text)
    details=parsed_data.xpath('//div[@class="home-page-copy-component container home-page-container"]//li')

    for detail in details:
        data=detail.xpath('text()').getall()
        # Safely extract elements with default fallback values
        name = data[0] if len(data) > 0 else "N/A"
        name_xpath='//div[@class="home-page-copy-component container home-page-container"]//li/text()'
        name_html=detail.xpath('//div[@class="home-page-copy-component container home-page-container"]//li').get()
        address = data[1] if len(data) > 1 else "N/A"
        address_xpath='//div[@class="home-page-copy-component container home-page-container"]//li/text()'
        address_html=detail.xpath('//div[@class="home-page-copy-component container home-page-container"]//li').get()
        number = data[2] if len(data) > 2 else "N/A"
        number_xpath = '//div[@class="home-page-copy-component container home-page-container"]//li/text()'
        number_html = detail.xpath('//div[@class="home-page-copy-component container home-page-container"]//li').get()
        details={
            "name":name,
            "name_xpath":name_xpath,
            "name_html":name_html,
            "address":address,
            "address_xpath":address_xpath,
            "address_html":address_html,
            "number":number,
            "number_xpath":number_xpath,
            "number_html":number_html
        }
        print(details)
        create_table_and_insert(details)


def main():
    cookies = {
        'orderCode': '',
        'JSESSIONID': 'CFFA8C57E38438CEC3848149153D7FC7.accstorefront-7d44c4959c-c2dzd',
        'CSRFToken': 'b38906c9-1b6f-4cd5-94d2-27351f85312e',
        'ROUTE': '.accstorefront-7d44c4959c-c2dzd',
        'GlobalE_Full_Redirect': 'false',
        'OptanonAlertBoxClosed': '2024-11-19T10:10:28.693Z',
        '_gcl_au': '1.1.1889555351.1732011029',
        'eupubconsent-v2': 'CQIU0yQQIU0yQAcABBENBPFsAP_gAEPgAChQKjNX_G__bWlr8X73aftkeY1P9_h77sQxBhfJE-4FzLvW_JwXx2ExNA36tqIKmRIAu3TBIQNlGJDURVCgaogVryDMaEiUoTNKJ6BkiFMRM2dYCF5vm4tj-QCY5vr991dx2B-t7dr83dzyy41Hn3a5_2a0WJCdA5-tDfv9bROb-9IOd_x8v4v8_F_pE2_eT1l_tWvp7D9-cts7_XW89_fff_9Pn_-uB_-_3_vQVGAJMNCogDLIkJCDQMIIEAKgrCAigQBAAAkDRAQAmDAp2BgEusJEAIAUAAwQAgABBkACAAASABCIAIACgQAAQCBQABAAQDAQAMDAAGACwEAgABAdAxTAggECwASMyIhTAhCASCAlsqEEgCBBXCEIs8CiAREwUAAAJABWAAICwWBxJICViQQJcQbQAAEACAQQAFCKTswBBAGbLUXiwbRlaYFg-YLntMAyQIggAAAA.f_wACHwAAAAA',
        '_ga': 'GA1.1.1959907589.1732011026',
        '_fbp': 'fb.1.1732011029942.728585860311179594',
        'scarab.visitor': '%22796B773AA1C4641B%22',
        'lantern': 'ad422880-7473-4c1a-b085-611ad4fa519b',
        'usi_return_visitor': 'Tue%20Nov%2019%202024%2015%3A40%3A30%20GMT%2B0530%20(India%20Standard%20Time)',
        'usi_first_hit': '1732011030577',
        '_tt_enable_cookie': '1',
        '_ttp': 'OdsrQpY5TCkKLi-ohLcGg9Y-DIG.tt.1',
        '_clck': '1chen4d%7C2%7Cfr0%7C0%7C1784',
        '_hjSession_588835': 'eyJpZCI6ImZkMmE1NWJhLWMyMjEtNDQzYS04OTUyLWM2MDQxYTJiNzUxMSIsImMiOjE3MzIwMTEwMzE2NTcsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MX0=',
        '_hjSessionUser_588835': 'eyJpZCI6IjNjNjQ2ZmY2LTU5ZTgtNTgzNC1iZDlmLTkyODE4OGFlODk4ZCIsImNyZWF0ZWQiOjE3MzIwMTEwMzE2NTYsImV4aXN0aW5nIjp0cnVlfQ==',
        'GlobalE_Welcome_Data': '%7B%22showWelcome%22%3Afalse%7D',
        'GlobalE_Consent': '%7B%22required%22%3Atrue%2C%22groups%22%3A%7B%221%22%3A1%2C%222%22%3A1%2C%223%22%3A1%7D%7D',
        '_hjSession_3316506': 'eyJpZCI6IjczMGMwZGJmLTQzOTItNDBmZC1hZWUyLWNlNzQ5Mzk2MWM5NyIsImMiOjE3MzIwMTExMTIxOTIsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=',
        '_hjSessionUser_3316506': 'eyJpZCI6ImNkYTNiZjZkLWNlMzItNTEwYS1hNTM0LWRiOTlmNTcyNmU0ZCIsImNyZWF0ZWQiOjE3MzIwMTExMTIxOTEsImV4aXN0aW5nIjp0cnVlfQ==',
        'dtm_token_sc': 'AQAG468Ew6xr-gEAu7oDAQA_QwABAQCSQuipGQEBAJJC6KkZ',
        'dtm_token': 'AQAG468Ew6xr-gEAu7oDAQA_QwABAQCSQuipGQEBAJJC6KkZ',
        'GlobalE_Data': '%7B%22countryISO%22%3A%22US%22%2C%22currencyCode%22%3A%22USD%22%2C%22cultureCode%22%3A%22en-US%22%7D',
        'OptanonConsent': 'isGpcEnabled=0&datestamp=Tue+Nov+19+2024+15%3A44%3A30+GMT%2B0530+(India+Standard+Time)&version=202408.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=ae075b76-145c-4850-812b-07d6317da6d3&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1%2CV2STACK42%3A1&intType=1&geolocation=GB%3BENG&AwaitingReconsent=false',
        '_ga_7PD22P3ZD7': 'GS1.1.1732011025.1.1.1732011270.20.0.0',
        'GlobalE_CT_Data': '%7B%22CUID%22%3A%7B%22id%22%3A%22279089385.747568372.1344%22%2C%22expirationDate%22%3A%22Tue%2C%2019%20Nov%202024%2010%3A44%3A31%20GMT%22%7D%2C%22CHKCUID%22%3Anull%2C%22GA4SID%22%3A315673070%2C%22GA4TS%22%3A1732011271662%2C%22Domain%22%3A%22.lkbennett.com%22%7D',
        '_uetsid': '81413660a65e11ef96559d68364a140b',
        '_uetvid': '81415800a65e11efba6827bc801020e9',
        '_clsk': 'dbn0xe%7C1732012104515%7C13%7C1%7Ct.clarity.ms%2Fcollect',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        # 'cookie': 'orderCode=; JSESSIONID=CFFA8C57E38438CEC3848149153D7FC7.accstorefront-7d44c4959c-c2dzd; CSRFToken=b38906c9-1b6f-4cd5-94d2-27351f85312e; ROUTE=.accstorefront-7d44c4959c-c2dzd; GlobalE_Full_Redirect=false; OptanonAlertBoxClosed=2024-11-19T10:10:28.693Z; _gcl_au=1.1.1889555351.1732011029; eupubconsent-v2=CQIU0yQQIU0yQAcABBENBPFsAP_gAEPgAChQKjNX_G__bWlr8X73aftkeY1P9_h77sQxBhfJE-4FzLvW_JwXx2ExNA36tqIKmRIAu3TBIQNlGJDURVCgaogVryDMaEiUoTNKJ6BkiFMRM2dYCF5vm4tj-QCY5vr991dx2B-t7dr83dzyy41Hn3a5_2a0WJCdA5-tDfv9bROb-9IOd_x8v4v8_F_pE2_eT1l_tWvp7D9-cts7_XW89_fff_9Pn_-uB_-_3_vQVGAJMNCogDLIkJCDQMIIEAKgrCAigQBAAAkDRAQAmDAp2BgEusJEAIAUAAwQAgABBkACAAASABCIAIACgQAAQCBQABAAQDAQAMDAAGACwEAgABAdAxTAggECwASMyIhTAhCASCAlsqEEgCBBXCEIs8CiAREwUAAAJABWAAICwWBxJICViQQJcQbQAAEACAQQAFCKTswBBAGbLUXiwbRlaYFg-YLntMAyQIggAAAA.f_wACHwAAAAA; _ga=GA1.1.1959907589.1732011026; _fbp=fb.1.1732011029942.728585860311179594; scarab.visitor=%22796B773AA1C4641B%22; lantern=ad422880-7473-4c1a-b085-611ad4fa519b; usi_return_visitor=Tue%20Nov%2019%202024%2015%3A40%3A30%20GMT%2B0530%20(India%20Standard%20Time); usi_first_hit=1732011030577; _tt_enable_cookie=1; _ttp=OdsrQpY5TCkKLi-ohLcGg9Y-DIG.tt.1; _clck=1chen4d%7C2%7Cfr0%7C0%7C1784; _hjSession_588835=eyJpZCI6ImZkMmE1NWJhLWMyMjEtNDQzYS04OTUyLWM2MDQxYTJiNzUxMSIsImMiOjE3MzIwMTEwMzE2NTcsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MX0=; _hjSessionUser_588835=eyJpZCI6IjNjNjQ2ZmY2LTU5ZTgtNTgzNC1iZDlmLTkyODE4OGFlODk4ZCIsImNyZWF0ZWQiOjE3MzIwMTEwMzE2NTYsImV4aXN0aW5nIjp0cnVlfQ==; GlobalE_Welcome_Data=%7B%22showWelcome%22%3Afalse%7D; GlobalE_Consent=%7B%22required%22%3Atrue%2C%22groups%22%3A%7B%221%22%3A1%2C%222%22%3A1%2C%223%22%3A1%7D%7D; _hjSession_3316506=eyJpZCI6IjczMGMwZGJmLTQzOTItNDBmZC1hZWUyLWNlNzQ5Mzk2MWM5NyIsImMiOjE3MzIwMTExMTIxOTIsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=; _hjSessionUser_3316506=eyJpZCI6ImNkYTNiZjZkLWNlMzItNTEwYS1hNTM0LWRiOTlmNTcyNmU0ZCIsImNyZWF0ZWQiOjE3MzIwMTExMTIxOTEsImV4aXN0aW5nIjp0cnVlfQ==; dtm_token_sc=AQAG468Ew6xr-gEAu7oDAQA_QwABAQCSQuipGQEBAJJC6KkZ; dtm_token=AQAG468Ew6xr-gEAu7oDAQA_QwABAQCSQuipGQEBAJJC6KkZ; GlobalE_Data=%7B%22countryISO%22%3A%22US%22%2C%22currencyCode%22%3A%22USD%22%2C%22cultureCode%22%3A%22en-US%22%7D; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Nov+19+2024+15%3A44%3A30+GMT%2B0530+(India+Standard+Time)&version=202408.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=ae075b76-145c-4850-812b-07d6317da6d3&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1%2CV2STACK42%3A1&intType=1&geolocation=GB%3BENG&AwaitingReconsent=false; _ga_7PD22P3ZD7=GS1.1.1732011025.1.1.1732011270.20.0.0; GlobalE_CT_Data=%7B%22CUID%22%3A%7B%22id%22%3A%22279089385.747568372.1344%22%2C%22expirationDate%22%3A%22Tue%2C%2019%20Nov%202024%2010%3A44%3A31%20GMT%22%7D%2C%22CHKCUID%22%3Anull%2C%22GA4SID%22%3A315673070%2C%22GA4TS%22%3A1732011271662%2C%22Domain%22%3A%22.lkbennett.com%22%7D; _uetsid=81413660a65e11ef96559d68364a140b; _uetvid=81415800a65e11efba6827bc801020e9; _clsk=dbn0xe%7C1732012104515%7C13%7C1%7Ct.clarity.ms%2Fcollect',
        'priority': 'u=0, i',
        'referer': 'https://www.lkbennett.com/navigation/store-locator-help',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36',
    }

    response = requests.get('https://www.lkbennett.com/navigation/store-locator-help', cookies=cookies, headers=headers)
    pagedata(response)

if __name__=="__main__":
    main()