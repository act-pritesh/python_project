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
def insert_store_data(store_data):
    connection = connect_db()
    cursor = connection.cursor()

    # SQL query to insert store data
    sql_query = """
    INSERT INTO burger_king_details (name,name_xpath,html_name, address, address_xpath,html_address, number,number_xpath,html_number, time, time_xpath,
                           html_time)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql_query, (
        store_data["name"],
        store_data["name_xpath"],
        store_data["html_name"],
        store_data["address"],
        store_data["address_xpath"],
        store_data["html_address"],
        store_data["number"],
        store_data["number_xpath"],
        store_data["html_number"],
        store_data["time"],
        store_data["time_xpath"],
        store_data["html_time"]
    ))

    connection.commit()  # Commit the transaction
    print(f"Inserted store: {store_data['name']}")  # Log the insertion
    cursor.close()
    connection.close()


def querys():
    cookies = {
        '_ga': 'GA1.1.1142280484.1725011867',
        '_ga_KQE6QVSPD1': 'GS1.1.1731926884.11.1.1731927336.0.0.0',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        # 'cookie': '_ga=GA1.1.1142280484.1725011867; _ga_KQE6QVSPD1=GS1.1.1731926884.11.1.1731927336.0.0.0',
        'priority': 'u=0, i',
        'referer': 'https://www.google.com/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36',
    }


    i = 1

    while True:
        response = requests.get(f"https://stores.burgerking.in/?page={i}", cookies=cookies, headers=headers)
        parsed_data = Selector(response.text)

        stores=parsed_data.xpath("//div[@class='store-info-box']")

        if not stores:
            break
        for store in stores:
            name=store.xpath('.//li[@class="outlet-name"]//div[@class="info-text"]/a/text()').get()
            name_xpath='.//li[@class="outlet-name"]//div[@class="info-text"]/a/text()'
            html_name=store.xpath('.//li[@class="outlet-name"]//div[@class="info-text"]/a').get()
            address=store.xpath('.//li[@class="outlet-address"]//div[@class="info-text"]//span/text()').getall()
            address_xpath='.//li[@class="outlet-address"]//div[@class="info-text"]//span/text()'
            full_address=" ".join(address)
            html_address=store.xpath('.//li[@class="outlet-address"]//div[@class="info-text"]/span').getall()
            full_html_address=" ".join(html_address)
            number=store.xpath('.//li[@class="outlet-phone"]//div[@class="info-text"]/a/text()').get()
            number_xpath='.//li[@class="outlet-phone"]//div[@class="info-text"]/a/text()'
            html_number=store.xpath('.//li[@class="outlet-phone"]//div[@class="info-text"]/a').get()
            time=store.xpath('.//li[@class="outlet-timings"]//div[@class="info-text"]/span/text()').get()
            time_xpath='.//li[@class="outlet-timings"]//div[@class="info-text"]/span/text()'
            html_time = store.xpath('//li[@class="outlet-timings"]//div[@class="info-text"]/span').get()
            store_data = {
                "name":name,
                "name_xpath":name_xpath,
                "html_name":html_name,
                "address": full_address,
                "address_xpath":address_xpath,
                "html_address":full_html_address,
                "number":number,
                "number_xpath":number_xpath,
                "html_number":html_number,
                "time":time,
                "time_xpath":time_xpath,
                "html_time":html_time
            }
            print(store_data)
            insert_store_data(store_data)
        print(i)
        i += 1
querys()








































