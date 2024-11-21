
from urllib.parse import urljoin, quote
import pymysql
import requests
from parsel import Selector


# Function to establish database connection and perform operations
def db_operations(store_details):
    # Define database connection parameters
    host = 'localhost'
    user = 'root'
    password = 'actowiz'
    database = 'burger_king'

    # SQL Queries
    create_table_query = """
    CREATE TABLE IF NOT EXISTS home_goods_details (
        name VARCHAR(255),
        name_xpath TEXT,
        name_html TEXT,
        full_address TEXT,
        full_address_xpath TEXT,
        full_address_html TEXT,
        phone_number VARCHAR(50),
        phone_number_xpath TEXT,
        phone_number_html TEXT,
        direction_url TEXT,
        direction_url_xpath TEXT,
        direction_url_html TEXT
    );
    """
    insert_query = """
    INSERT INTO home_goods_details (
        name, name_xpath, name_html, 
        full_address, full_address_xpath, full_address_html,
        phone_number, phone_number_xpath, phone_number_html,
        direction_url, direction_url_xpath, direction_url_html
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    # Connect to the database
    connection = pymysql.connect(host=host, user=user, password=password, database=database)
    cursor = connection.cursor()

    # Create table if it doesn't exist
    cursor.execute(create_table_query)

    # Insert data into the table
    cursor.execute(insert_query, (
        store_details["name"], store_details["name_xpath"], store_details["name_html"],
        store_details["full_address"], store_details["full_address_xpath"], store_details["full_address_html"],
        store_details["phone_number"], store_details["phone_number_xpath"], store_details["phone_number_html"],
        store_details["direction_url"], store_details["direction_url_xpath"], store_details["direction_url_html"]
    ))

    # Commit the transaction and close the connection
    connection.commit()
    connection.close()
    print("Data inserted successfully!")


def page_data(full_href, headers, cookies):
    response = requests.get(full_href, headers=headers, cookies=cookies)
    parsed_data = Selector(response.text)
    details = parsed_data.xpath('//div[@class="store-info"]')
    for detail in details:
        name = detail.xpath('./h1/text()').get()
        name_xpath = './h1/text()'
        name_html = detail.xpath('./h1').get()
        address = detail.xpath('./h2/text()').getall()
        address_xpath = './h2/text()'
        address_html = detail.xpath('./h2').getall()
        full_address_html="".join(address_html)
        address = [t.strip() for t in address if t.strip()]
        full_address = " ".join(address).replace('\r','').replace('\n','')  # Joining address parts into a single string
        phone_number = detail.xpath('./p/a[@data-link="Phone Number:Call"]/text()').get()
        phone_number_xpath = './p/a[@data-link="Phone Number:Call"]/text()'
        phone_number_html = detail.xpath('./p/a[@data-link="Phone Number:Call"]').get()
        direction_url = detail.xpath('./p/a[@class="link directions"]/@href').get()
        direction_url_xpath = './p/a[@class="link directions"]/@href'
        direction_url_html = detail.xpath('./p/a[@class="link directions"]').get()
        encoded_url = quote(direction_url)
        # Create a dictionary for the current store
        store_details = {
            "name": name if name else "N/A",
            "name_xpath":name_xpath,
            "name_html":name_html,
            "full_address": full_address,
            "full_address_xpath":address_xpath,
            "full_address_html":full_address_html,
            "phone_number": phone_number,
            "phone_number_xpath":phone_number_xpath,
            "phone_number_html":phone_number_html,
            "direction_url": encoded_url,
            "direction_url_xpath":direction_url_xpath,
            "direction_url_html":direction_url_html
        }
        # print(store_details)
        db_operations(store_details)

def pagelink(response,headers,cookies):
    parsed_data=Selector(response.text)
    links=parsed_data.xpath('//ul[@class="states-list"]/li//a[@class="arrow-link"]')
    for link in links:
        href=link.xpath('./@href').get()
        full_href=urljoin('https://www.homegoods.com/',href)
        # print(full_href)
        page_data(full_href,headers,cookies)
def main():
    cookies = {
        'AKA_A2': 'A',
        'akaalb_www_homegoods_com_alb': '~op=:~rv=56~m=~os=698f3717b47f60b3161d8805543209a1~id=7c72635ab729a560572b541b22eefbcd',
        'x-tjx-CBTC': '5b35d3526805858aa5475ea0d435c2f3',
        '_abck': '4643B9AF594AE7C641F1013300A3BA81~-1~YAAQDNJ6XBP8ui+TAQAAUPdtTQzH/2goafRUcugsPPU0MwFwj2YgR+pfa77A0YKhrFwklZmrFjhOh52P/12wEshvRBf7x2gGYOD1/WPkah4zzmAYdnZ4zZUoevIRa2p3n3WIayTEhR69JWpZi5AMTvmkQe9M5qK05DrzYUdUyfSuqUC8m5pWipPrUPZOzbihcW57D/efHwOZy04pvaBKMsCQVMUi8TlN3x0t7vWWclx1Ke6HoWE0ER3dtQgyjIhabgu+lLZulJretw+s4D5ic5SQqyfkcP2excWByRVqEPdHRDXwolv/pc87y0TYAkKqr8cSZD7DQEjDp5+QgGgpoUdgg94W9Mnz2laEksYskq6TZGTVC47wrYGPPMUcyGuL6EWwFQ2dsDW89X8TeyGmb0ZxxveyHl56my7c2cNlN/yL~-1~-1~-1',
        'ak_bmsc': 'A57AAB0CB3CB604F038636545B5AD144~000000000000000000000000000000~YAAQDNJ6XBT8ui+TAQAAUPdtTRmujZxL3ePp8okxF4LNhUCbzXE6l7nEjM3PFFYuQfOxeYYOkBWBKsctAYsosC/atGp8Ll9M+wAgbNOT8WQNutV2mb97zWjwyI3ZhChv32oi/Y9/81Zz2bB+Ito1XjS9pZ8o9v7rtGqowMtIOaK1JEVWDv7VBaQtJmekUB8AJwO++drrtQgDJzzQ3XJC2eqRQI+3ATVqFHj3EaS5W5EWDi40CYmTW4x8LJHqlYJVgDEC0xb71sNXvOGw3y6VE/y2VjddT11niEaMemYA8GbrBMrTixMB2i5C/R+1zRZDKwlxD+9+eJ7LSjtIIsnO6fwGozk3FyvYRF/uSbpuQd5vkbAd1kSZuyG/t0xwAevRqQf6S9eMg+YmAH+5UA==',
        'bm_sz': '03FCCA2A38236453E4C5E283B97326EC~YAAQDNJ6XBb8ui+TAQAAUPdtTRkYvYC18/AahiFTX18TjdPWE/cyuVPOMCZLB/JC7zVmACRzBw0jHPOgoIh2M8CjjljXHTBXq9JqCvmlLzdxjUth+38jEu1tAW5rAIIFg/B/WZDQ93nS4k5A+m1m4Ny/1zChoveFoGE1U4kcKJVGoMZCoaIE4xIHA3FTrSkDgiA7pm/+MUYxX+SFDCebdPdyedpFtgiSxPPQhblPf0xrmWs+5Rsf3DVYzjLNjTct9QEga58VGZNAxmNpi5NYztfPLoNBBcqPjSRNfpLsGXv+sVdlFh/EEzyuyIY5rloWkPuveNWSdRnVMdD3FjoDWETSN8pUValj1DWpJhlQupciKPySlAKtMV7daZsSZbFQy4KQUy3qfSNKiN50soFdWaY=~3748917~3229237',
        's_fid': '095DF99429A1E65B-1D80B10B3905AA11',
        's_cc': 'true',
        '_ga': 'GA1.1.111592534.1732170878',
        's_nr30': '1732170883549-New',
        'akavpau_www_homegoods_vp': '1732171189~id=1c2cf52f872f3f828fa90ce26956a63c',
        'bm_mi': '3FE48FF0644FBA6F591EE03FD1435328~YAAQDNJ6XCv8ui+TAQAAwDtuTRkMv5FU1WhSaM28ahU8yhfmQ4ucO/1EsiP8dwkratC6KKDLVm2xLmVfTQwietn+ACGNXnowPGOjUpLxgj+TdxBnEhgST69LWOL22qNp22yqiX39ouTX4hRg/9p4id6/w6zYxGf9skcKCJxiSy0eUpVo9HA/x/9YsRmKTOGhnz4wjiFFLA9zcBwCg+B2rKOx/9dFO+tYwggnRNyIp/ChEc8zLfawMhYn0qy0QCpIGHCpMYlEKGEGpLxoul6cIuK7dmRiZRVbsT5lIOZSbidISZJCinFgZ5av91K92koZetuSt5mPSXNimF929Cq42YCa~1',
        'bm_sv': '5238C250C705F7C824E5CC4D9B4121A1~YAAQDNJ6XCz8ui+TAQAAwDtuTRmfwGt9SH58Yi/YgS2HK+oSVrp+zfAPLnXfAKnEcj24KdCIadFrcpjkUDzs7y9kfUU9cvbRCZbF+Fr+9Wt6lrBWi4DdRqkp9CZbqEstq9Muq8ag4CUSt0LpfaXGpDNi7IlQZvA8Yk97+XqTAly8ZCxRUwrFcejTAsPmZUKIpUkpaexpE1m6RD2xCI67R8h1fyUbJ2PXiIz3lzDyHMYfhrkzuFGSB0VIsfWiR/OUIZ77~1',
        '_ga_E4PCS1FX8R': 'GS1.1.1732170877.1.0.1732170897.40.0.0',
        'OptanonConsent': 'isGpcEnabled=0&datestamp=Thu+Nov+21+2024+12%3A04%3A57+GMT%2B0530+(India+Standard+Time)&version=202410.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=a688176c-448c-4b04-9677-2084e46bc5c6&interactionCount=1&isAnonUser=1&landingPath=https%3A%2F%2Fwww.homegoods.com%2Fall-stores&groups=2%3A1%2CC0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        # 'cookie': 'AKA_A2=A; akaalb_www_homegoods_com_alb=~op=:~rv=56~m=~os=698f3717b47f60b3161d8805543209a1~id=7c72635ab729a560572b541b22eefbcd; x-tjx-CBTC=5b35d3526805858aa5475ea0d435c2f3; _abck=4643B9AF594AE7C641F1013300A3BA81~-1~YAAQDNJ6XBP8ui+TAQAAUPdtTQzH/2goafRUcugsPPU0MwFwj2YgR+pfa77A0YKhrFwklZmrFjhOh52P/12wEshvRBf7x2gGYOD1/WPkah4zzmAYdnZ4zZUoevIRa2p3n3WIayTEhR69JWpZi5AMTvmkQe9M5qK05DrzYUdUyfSuqUC8m5pWipPrUPZOzbihcW57D/efHwOZy04pvaBKMsCQVMUi8TlN3x0t7vWWclx1Ke6HoWE0ER3dtQgyjIhabgu+lLZulJretw+s4D5ic5SQqyfkcP2excWByRVqEPdHRDXwolv/pc87y0TYAkKqr8cSZD7DQEjDp5+QgGgpoUdgg94W9Mnz2laEksYskq6TZGTVC47wrYGPPMUcyGuL6EWwFQ2dsDW89X8TeyGmb0ZxxveyHl56my7c2cNlN/yL~-1~-1~-1; ak_bmsc=A57AAB0CB3CB604F038636545B5AD144~000000000000000000000000000000~YAAQDNJ6XBT8ui+TAQAAUPdtTRmujZxL3ePp8okxF4LNhUCbzXE6l7nEjM3PFFYuQfOxeYYOkBWBKsctAYsosC/atGp8Ll9M+wAgbNOT8WQNutV2mb97zWjwyI3ZhChv32oi/Y9/81Zz2bB+Ito1XjS9pZ8o9v7rtGqowMtIOaK1JEVWDv7VBaQtJmekUB8AJwO++drrtQgDJzzQ3XJC2eqRQI+3ATVqFHj3EaS5W5EWDi40CYmTW4x8LJHqlYJVgDEC0xb71sNXvOGw3y6VE/y2VjddT11niEaMemYA8GbrBMrTixMB2i5C/R+1zRZDKwlxD+9+eJ7LSjtIIsnO6fwGozk3FyvYRF/uSbpuQd5vkbAd1kSZuyG/t0xwAevRqQf6S9eMg+YmAH+5UA==; bm_sz=03FCCA2A38236453E4C5E283B97326EC~YAAQDNJ6XBb8ui+TAQAAUPdtTRkYvYC18/AahiFTX18TjdPWE/cyuVPOMCZLB/JC7zVmACRzBw0jHPOgoIh2M8CjjljXHTBXq9JqCvmlLzdxjUth+38jEu1tAW5rAIIFg/B/WZDQ93nS4k5A+m1m4Ny/1zChoveFoGE1U4kcKJVGoMZCoaIE4xIHA3FTrSkDgiA7pm/+MUYxX+SFDCebdPdyedpFtgiSxPPQhblPf0xrmWs+5Rsf3DVYzjLNjTct9QEga58VGZNAxmNpi5NYztfPLoNBBcqPjSRNfpLsGXv+sVdlFh/EEzyuyIY5rloWkPuveNWSdRnVMdD3FjoDWETSN8pUValj1DWpJhlQupciKPySlAKtMV7daZsSZbFQy4KQUy3qfSNKiN50soFdWaY=~3748917~3229237; s_fid=095DF99429A1E65B-1D80B10B3905AA11; s_cc=true; _ga=GA1.1.111592534.1732170878; s_nr30=1732170883549-New; akavpau_www_homegoods_vp=1732171189~id=1c2cf52f872f3f828fa90ce26956a63c; bm_mi=3FE48FF0644FBA6F591EE03FD1435328~YAAQDNJ6XCv8ui+TAQAAwDtuTRkMv5FU1WhSaM28ahU8yhfmQ4ucO/1EsiP8dwkratC6KKDLVm2xLmVfTQwietn+ACGNXnowPGOjUpLxgj+TdxBnEhgST69LWOL22qNp22yqiX39ouTX4hRg/9p4id6/w6zYxGf9skcKCJxiSy0eUpVo9HA/x/9YsRmKTOGhnz4wjiFFLA9zcBwCg+B2rKOx/9dFO+tYwggnRNyIp/ChEc8zLfawMhYn0qy0QCpIGHCpMYlEKGEGpLxoul6cIuK7dmRiZRVbsT5lIOZSbidISZJCinFgZ5av91K92koZetuSt5mPSXNimF929Cq42YCa~1; bm_sv=5238C250C705F7C824E5CC4D9B4121A1~YAAQDNJ6XCz8ui+TAQAAwDtuTRmfwGt9SH58Yi/YgS2HK+oSVrp+zfAPLnXfAKnEcj24KdCIadFrcpjkUDzs7y9kfUU9cvbRCZbF+Fr+9Wt6lrBWi4DdRqkp9CZbqEstq9Muq8ag4CUSt0LpfaXGpDNi7IlQZvA8Yk97+XqTAly8ZCxRUwrFcejTAsPmZUKIpUkpaexpE1m6RD2xCI67R8h1fyUbJ2PXiIz3lzDyHMYfhrkzuFGSB0VIsfWiR/OUIZ77~1; _ga_E4PCS1FX8R=GS1.1.1732170877.1.0.1732170897.40.0.0; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Nov+21+2024+12%3A04%3A57+GMT%2B0530+(India+Standard+Time)&version=202410.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=a688176c-448c-4b04-9677-2084e46bc5c6&interactionCount=1&isAnonUser=1&landingPath=https%3A%2F%2Fwww.homegoods.com%2Fall-stores&groups=2%3A1%2CC0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    }

    response = requests.get('https://www.homegoods.com/all-stores', cookies=cookies, headers=headers)
    # if response.status_code==200:
    pagelink(response,headers,cookies)
    # else:
    #     print("hy")
    print(response.status_code)

if __name__=="__main__":
    main()