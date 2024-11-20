import pymysql
import requests

from parsel import Selector

def connect_to_database():
    """
    Establishes a connection to the database.
    """
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='actowiz',
        database='burger_king',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

def create_table():
    """
    Creates the store_locator table if it doesn't exist.
    """
    connection = connect_to_database()
    with connection.cursor() as cursor:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS patagonia_details (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            name_xpath TEXT,
            name_html TEXT,
            street_address TEXT,
            street_address_xpath TEXT,
            street_address_html TEXT,
            state VARCHAR(255),
            state_xpath TEXT,
            state_html TEXT,
            city VARCHAR(255),
            city_xpath TEXT,
            city_html TEXT,
            city_code VARCHAR(50),
            city_code_xpath TEXT,
            city_code_html TEXT,
            zip_code VARCHAR(50),
            zip_code_xpath TEXT,
            zip_code_html TEXT,
            phone_number VARCHAR(50),
            phone_number_xpath TEXT,
            phone_number_html TEXT,
            direction_url TEXT,
            direction_url_xpath TEXT,
            direction_url_html TEXT
        );
        """
        cursor.execute(create_table_query)
        connection.commit()

def insert_store(store_data):
    """
    Inserts a single store record into the database.
    """
    connection = connect_to_database()
    with connection.cursor() as cursor:
        insert_query = """
        INSERT INTO patagonia_details (
            name, name_xpath, name_html,
            street_address, street_address_xpath, street_address_html,
            state, state_xpath, state_html,
            city, city_xpath, city_html,
            city_code, city_code_xpath, city_code_html,
            zip_code, zip_code_xpath, zip_code_html,
            phone_number, phone_number_xpath, phone_number_html,
            direction_url, direction_url_xpath, direction_url_html
        ) VALUES (
            %(name)s, %(name_xpath)s, %(name_html)s,
            %(street_address)s, %(street_address_xpath)s, %(street_address_html)s,
            %(state)s, %(state_xpath)s, %(state_html)s,
            %(city)s, %(city_xpath)s, %(city_html)s,
            %(city_code)s, %(city_code_xpath)s, %(city_code_html)s,
            %(zip_code)s, %(zip_code_xpath)s, %(zip_code_html)s,
            %(phone_number)s, %(phone_number_xpath)s, %(phone_number_html)s,
            %(direction_url)s, %(direction_url_xpath)s, %(direction_url_html)s
        );
        """
        cursor.execute(insert_query, store_data)
        connection.commit()


def pagedata(response):
    parsed_data = Selector(response.text)
    boxes = parsed_data.xpath('//div[@class="col"]//div[@class="store-locator__state-container"]')
    create_table()
    for box in boxes:
        # Get the state heading for the current state container
        state = box.xpath('.//h2[@class="store-locator__state-heading"]/text()').get()
        state_xpath = './/h2[@class="store-locator__state-heading"]/text()'
        state_html = box.xpath('.//h2[@class="store-locator__state-heading"]').get()
        stores_data = box.xpath('.//div[@class="store-locator__store-tile"]')
        for store in stores_data:
            name = store.xpath('.//a[@class="store-locator__store-name"]/text()').get()
            name_xpath = './/a[@class="store-locator__store-name"]/text()'
            name_html = store.xpath('.//a[@class="store-locator__store-name"]').get()
            street_address = store.xpath('.//div[@class="store-locator__store-info"]/div[1]/text()').get()
            street_address_xpath = './/div[@class="store-locator__store-info"]/div[1]/text()'
            street_address_html = store.xpath('.//div[@class="store-locator__store-info"]').get()
            city = store.xpath('.//div[@class="store-locator__store-info"]/div/span[1]/text()').get()
            city_xpath = './/div[@class="store-locator__store-info"]/div/span[1]/text()'
            city_html = store.xpath('.//div[@class="store-locator__store-info"]').get()
            city_code = store.xpath('.//div[@class="store-locator__store-info"]/div/span[2]/text()').get()
            city_code_xpath = './/div[@class="store-locator__store-info"]/div/span[2]/text()'
            city_code_html = store.xpath('.//div[@class="store-locator__store-info"]').get()
            zip_code = store.xpath('.//div[@class="store-locator__store-info"]/div/span[3]/text()').get()
            zip_code_xpath = './/div[@class="store-locator__store-info"]/div/span[3]/text()'
            zip_code_html = store.xpath('.//div[@class="store-locator__store-info"]').get()
            phone_number = store.xpath('.//div[@class="store-locator__store-info"]/div[last()]/text()').get()
            phone_number_xpath ='.//div[@class="store-locator__store-info"]/div[last()]/text()'
            phone_number_html = store.xpath('.//div[@class="store-locator__store-info"]').get()
            direction_url = store.xpath('.//div[@class="store-locator__store-links"]/a[@target]/@href').get()
            direction_url_xpath = './/div[@class="store-locator__store-links"]/a[@target]/@href'
            direction_url_html = store.xpath('.//div[@class="store-locator__store-links"]/a[@target]').get()

            stores = {
                "name": name,
                "name_xpath":name_xpath,
                "name_html":name_html,
                "street_address": street_address,
                "street_address_xpath":street_address_xpath,
                "street_address_html":street_address_html,
                "state": state,
                "state_xpath":state_xpath,
                "state_html":state_html,
                "city": city,
                "city_xpath":city_xpath,
                "city_html":city_html,
                "city_code": city_code,
                "city_code_xpath":city_code_xpath,
                "city_code_html":city_code_html,
                "zip_code": zip_code,
                "zip_code_xpath":zip_code_xpath,
                "zip_code_html":zip_code_html,
                "phone_number": phone_number,
                "phone_number_xpath":phone_number_xpath,
                "phone_number_html":phone_number_html,
                "direction_url": direction_url,
                "direction_url_xpath":direction_url_xpath,
                "direction_url_html":direction_url_html

            }
            print(stores)
            insert_store(stores)


def main():
    headers = {
        'Referer': 'https://www.google.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
    }

    response = requests.get('https://www.patagonia.com/store-locator/', headers=headers)
    pagedata(response)

if __name__=="__main__":
    main()