import json
import os
import re
from datetime import datetime
from urllib.parse import urljoin
import scrapy
from parsel import Selector
from scrapy.crawler import CrawlerProcess
import pandas as pd  # Import pandas for Excel handling


class NbsSpider(scrapy.Spider):
    name = "nbs"

    def __init__(self, *args, **kwargs):
        super(NbsSpider, self).__init__(*args, **kwargs)
        # Create an 'output' folder if it doesn't exist
        self.output_folder = 'output'
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # Initialize a list to store the data
        self.data = []

    def start_requests(self):
        cookies = {
            'pll_language': 'en',
            'cookie-consent-7319579eda0a': 'security_storage%2Canalytics_storage%2Cpersonalization_storage%2Cad_storage',
            '_hjSession_3211032': 'eyJpZCI6IjQ0ZDU5MDlhLTkyOGQtNDkxZi1hMmIyLWQ0NmRjYjZlZTBkZCIsImMiOjE3MzM5ODA3MTI2NjgsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MX0=',
            '_gid': 'GA1.2.333372529.1733980715',
            '_hjSessionUser_3211032': 'eyJpZCI6ImM0NjM2MDZjLWZlNjAtNWUyZS1hOWI0LTNkZGQ1OWRlMWE4ZCIsImNyZWF0ZWQiOjE3MzM5ODA3MTI2NjYsImV4aXN0aW5nIjp0cnVlfQ==',
            '_ga': 'GA1.2.1139027750.1733980456',
            '_ga_M9SPDPXFS5': 'GS1.1.1733980716.1.1.1733980818.0.0.0',
            '_ga_R8X0JM00WN': 'GS1.1.1733980455.1.1.1733980818.0.0.0',
        }

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        url = 'https://nbs.sk/en/financial-market-supervision-practical-info/warnings/warning-list-of-non-authorized-business-activities-of-entities/'
        yield scrapy.Request(url=url, method='GET', headers=headers, cookies=cookies, callback=self.parse)

    def remove_extra_space(self, text):
        if text is None:
            return ""
        text = re.sub(r'x000D', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    def get_column_names(self, response):
        headers = response.xpath("//table/thead/tr/td/text()").getall()
        return [
            h.replace("\r", "").replace("\t", "").replace("\n", "").replace(" ", "_").lower().strip()
            for h in headers
        ]

    def fetch_additional_content(self, response, raw_data):
        description = response.xpath('//div[@class="nbs-post__block"]//p//text() | //div[@class="nbs-content"]//p/text()').getall()
        full_des = ''.join([self.remove_extra_space(text) for text in description]).strip()
        raw_data['description'] = full_des
        yield from self.post_request(raw_data)

    def parse(self, response):
        header = self.get_column_names(response)
        rows = response.xpath('//table/tbody//tr')

        for row in rows:
            raw_data = {'url': response.url}
            for i, cell in enumerate(row.xpath("td")):
                cell_text = self.remove_extra_space(cell.xpath("string()").get())

                # Convert date if applicable
                try:
                    cell_text = datetime.strptime(cell_text, '%d. %m. %Y').strftime('%Y-%m-%d')
                except ValueError:
                    pass

                # Add cell content to raw_data
                raw_data[header[i]] = cell_text

                # Handle links in the cell
                link = cell.xpath(".//a/@href").get()
                if link:
                    full_link = urljoin(response.url, link)
                    raw_data[f"{header[i]}_url"] = full_link

                    # Check if the current header is 'subject' to trigger additional content fetching
                    if header[i] == 'subject':
                        yield scrapy.Request(
                            full_link,
                            callback=self.fetch_additional_content,
                            cb_kwargs={'raw_data': raw_data}
                        )

            # Append the raw_data after processing each row, so multiple data rows are added
            self.data.append(raw_data)

    def post_request(self, raw_data):
        cookies = {
            'pll_language': 'en',
            'cookie-consent-7319579eda0a': 'security_storage%2Canalytics_storage%2Cpersonalization_storage%2Cad_storage',
            '_gid': 'GA1.2.333372529.1733980715',
            '_hjSessionUser_3211032': 'eyJpZCI6ImM0NjM2MDZjLWZlNjAtNWUyZS1hOWI0LTNkZGQ1OWRlMWE4ZCIsImNyZWF0ZWQiOjE3MzM5ODA3MTI2NjYsImV4aXN0aW5nIjp0cnVlfQ==',
            '_ga': 'GA1.2.1139027750.1733980456',
            '_ga_R8X0JM00WN': 'GS1.1.1733988192.4.0.1733988192.0.0.0',
            '_ga_M9SPDPXFS5': 'GS1.1.1733988192.4.0.1733988192.0.0.0',
        }

        headers = {
            'Accept': 'application/json, */*;q=0.1',
            'Content-Type': 'application/json',
            'Origin': 'https://nbs.sk',
            'Referer': 'https://nbs.sk/en/financial-market-supervision-practical-info/warnings/warning-list-of-non-authorized-business-activities-of-entities/',
        }

        json_data = {
            'gbConfig': {
                'tags': [33218],
                'limit': 10,
                'template': 'links',
            },
            'lang': 'en',
            'limit': 10,
            'offset': 0,
        }

        url = 'https://nbs.sk/wp-json/nbs/v1/post/list'
        yield scrapy.Request(url=url,
                             method='POST',
                             headers=headers,
                             cookies=cookies,
                             body=json.dumps(json_data),
                             callback=self.parse_post_response,
                             cb_kwargs={'raw_data': raw_data})

    def post_fetch_additional_content(self,response,raw_data):
        description = response.xpath('//div[@class="nbs-post__block"]//p//text()').getall()
        full_des = ''.join([self.remove_extra_space(text) for text in description]).strip()
        raw_data['description'] = full_des
        self.data.append(raw_data)

    def parse_post_response(self, response, raw_data):
        # Parse the JSON response
        data = response.json()
        html_content = data.get('html')
        if html_content:
            # Convert the HTML string into a Selector object
            selector = Selector(text=html_content)

            # Find all div elements with the class 'archive-results'
            date_elements = selector.xpath('//div[@class="archive-results"]//a')

            for d in date_elements:
                # Create a copy of raw_data for each iteration
                row_data = raw_data.copy()

                # Extract date and format it
                date = d.xpath('.//div[@class="date"]/text()').get('N/A').strip()
                try:
                    date = datetime.strptime(date, '%d %b %Y').strftime('%Y-%m-%d')
                except ValueError:
                    pass
                row_data['date'] = date

                # Extract subject and link
                subject = d.xpath('.//h2[@class="h3"]/text()').get('N/A').strip()
                subject_link = d.xpath('./@href').get('N/A').strip()
                row_data['subject'] = subject
                row_data['subject_url'] = subject_link

                # If there's a link to follow, make a request for additional content
                if subject_link:
                    yield scrapy.Request(
                        subject_link,
                        callback=self.post_fetch_additional_content,
                        cb_kwargs={'raw_data': row_data}
                    )
                else:
                    # If no additional link, append the row data immediately
                    self.data.append(row_data)

            # Append the data for post content after it is fully processed

    def closed(self,reason):
        # Write the data to an Excel file when the spider is closed
        df = pd.DataFrame(self.data)
        output_file = os.path.join(self.output_folder, 'nbs_sk.xlsx')
        df.to_excel(output_file, index=False)
        self.log(f"Data saved to {output_file}")


if __name__=="__main__":
    process = CrawlerProcess()
    process.crawl(NbsSpider)
    process.start()

