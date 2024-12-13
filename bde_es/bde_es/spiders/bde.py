import os
import re
from datetime import datetime

import pandas as pd
import scrapy
from deep_translator import GoogleTranslator
from scrapy.crawler import CrawlerProcess
from langdetect import detect

class BdeSpider(scrapy.Spider):
    name = "bde"
    # allowed_domains = ["bde.es.com"]
    # start_urls = ["https://bde.es.com"]

    def start_requests(self):
        cookies = {
            'PD_STATEFUL_33b41c04-cc9e-11e0-a40a-e41f131e2270': 'www.bde.es',
            'wbe_cookies': '{"tecnica":true,"GoogleAnalytics":true,"id":"V2.8oOfteqkrO5o"}',
            '_ga': 'GA1.1.972047639.1734067538',
            'stg_traffic_source_priority': '1',
            '_pk_ses.c7026fcf-ef47-44a8-aa74-346d541f014f.c9b9': '*',
            'TS014fad2f': '013f5b1f43da40960a85535007201ee468ffb85ae77d939ff90573f69ed5d555c3d12cea119a1b661591218c7b8482758715abbd7d',
            'JSESSIONID': '0000c7QEaL3TEIlRNF7kNgG34nn:1edrf25nt',
            '_ga_GJB7F10M0K': 'GS1.1.1734067537.1.1.1734068571.0.0.0',
            '_pk_id.c7026fcf-ef47-44a8-aa74-346d541f014f.c9b9': 'f8f96fe8e9b0f8d7.1734067538.1.1734068573.1734067538.',
            'stg_last_interaction': 'Fri%2C%2013%20Dec%202024%2005:43:53%20GMT',
            'stg_returning_visitor': 'Fri%2C%2013%20Dec%202024%2005:43:53%20GMT',
        }

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            # 'Cookie': 'PD_STATEFUL_33b41c04-cc9e-11e0-a40a-e41f131e2270=www.bde.es; wbe_cookies={"tecnica":true,"GoogleAnalytics":true,"id":"V2.8oOfteqkrO5o"}; _ga=GA1.1.972047639.1734067538; stg_traffic_source_priority=1; _pk_ses.c7026fcf-ef47-44a8-aa74-346d541f014f.c9b9=*; TS014fad2f=013f5b1f43da40960a85535007201ee468ffb85ae77d939ff90573f69ed5d555c3d12cea119a1b661591218c7b8482758715abbd7d; JSESSIONID=0000c7QEaL3TEIlRNF7kNgG34nn:1edrf25nt; _ga_GJB7F10M0K=GS1.1.1734067537.1.1.1734068571.0.0.0; _pk_id.c7026fcf-ef47-44a8-aa74-346d541f014f.c9b9=f8f96fe8e9b0f8d7.1734067538.1.1734068573.1734067538.; stg_last_interaction=Fri%2C%2013%20Dec%202024%2005:43:53%20GMT; stg_returning_visitor=Fri%2C%2013%20Dec%202024%2005:43:53%20GMT',
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
        url = 'https://www.bde.es/wbe/en/entidades-profesionales/supervisadas/sanciones-impuestas-banco-espana/'
        yield scrapy.Request(url=url, method='GET', headers=headers, cookies=cookies, callback=self.parse)

    def convert_date(self,date_str):
        # Parse the input string into a datetime object
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        # Convert the datetime object to the desired format
        return date_obj.strftime('%Y-%m-%d')

    def parse(self, response):
        dataset=response.xpath('//div[@class="block-entry-content__fine__results"]/div[@class="block-entry-content__fine__result"]')
        results = []
        for data in dataset:
            published_date=data.xpath('./p[@class="block-entry-content__fine__result__date-publication"]/span/text()').get('N/A')
            final_published_date=self.convert_date(published_date)
            description=data.xpath('./p[not(@class) and not(.//strong[normalize-space(.) = "Applicable legislation:"])]//text()').getall()
            final_des=''.join(description)
            # Check if translation is necessary
            if final_des:
                try:
                    lang = detect(final_des)
                    if lang == 'en':
                        translated_des = final_des
                    else:
                        translated_des = GoogleTranslator(source='auto', target='en').translate(final_des)
                except Exception:
                    translated_des = "Translation Error"
            else:
                translated_des = "N/A"
            pattern1=r'Fine.*(€\s*[\d,.]+)'
            pattern2='Multa.*?(\d\s*[\d,. €]+)+'
            match1 = re.search(pattern1, translated_des)
            match2 = re.search(pattern2, translated_des)
            if match1:
                panelty = match1.group(1)
            elif match2:
                panelty = match2.group(1)
            else:
                panelty = None  # No match found

            applicable_legislation=data.xpath('.//p[contains(., "Applicable legislation")]/text() | .//p[contains(.,"Normas aplicables")]/text()').get()
            resolution_date=data.xpath('//p[@class="block-entry-content__fine__result__date-resolution"]/span/text()').get()
            final_resolution_date=self.convert_date(resolution_date)
            decision=data.xpath('.//p[@class="block-entry-content__fine__result__signature"]/span/text()').get()
            results.append({
                'url':response.url,
                'published_date': final_published_date if final_published_date else "N/A",
                'description': translated_des if translated_des else "N/A",
                'penalty': panelty if panelty else "N/A",
                'applicable_legislation': applicable_legislation if applicable_legislation else "N/A",
                'resolution_date': final_resolution_date if final_resolution_date else "N/A",
                'decision':decision
            })

            # Ensure the 'output' folder exists
        output_folder = "output"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Export to Excel using pandas
        output_path = os.path.join(output_folder, "bde_es_translate.xlsx")
        df = pd.DataFrame(results)
        df.to_excel(output_path, index=False)
        self.log(f"Data exported to {output_path}")

if __name__=="__main__":
    process = CrawlerProcess()
    process.crawl(BdeSpider)
    process.start()
