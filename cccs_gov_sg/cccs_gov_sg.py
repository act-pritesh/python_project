import os
import string
from datetime import datetime
from urllib.parse import urljoin
import re
import pandas as pd
import requests
from parsel import Selector

# Function to get the response from the URL
def fetch_webpage(url, cookies, headers):
    response = requests.get(url, cookies=cookies, headers=headers)
    response.raise_for_status()
    return Selector(response.text.replace('<br>', '').replace('<br />', ''))

# Function to clean and extract table headers
def get_column_names(selector):
    headers = selector.xpath("//table[@class='listing-table__table']//th//text()").getall()
    return [
        h.replace("\r", "").replace("\t", "").replace("\n", "").replace(" ", "_").lower().strip()
        for h in headers
    ]

# Function to remove extra spaces and unwanted characters from text
def remove_extra_space(text):
    text = re.sub(r'x000D', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

# Function to process table data (header and data lists)
# Function to fetch additional content (description and media release link or table data)
def process_table_data(header, data):
    """
    Process the table header and data, merging multiple <p> tags in any cell of the second column.
    """
    processed_data = []

    for i in range(len(data)):
        # If the data entry is a list (i.e., multiple <p> tags), join all elements into a single string
        if isinstance(data[i], list):
            merged_text = ' '.join([remove_extra_space(text) for text in data[i]]).strip()
        else:
            merged_text = remove_extra_space(data[i])

        processed_data.append(merged_text)

    return dict(zip(header, processed_data))


def fetch_additional_content(url, cookies, headers):
    """
    Fetch additional content from the provided URL and handle tables with multiple <p> tags dynamically.
    """
    response = requests.get(url, cookies=cookies, headers=headers)
    response.raise_for_status()
    parsed_data = Selector(response.text)

    # Try to fetch the description
    description = parsed_data.xpath('//div[@class="rte"]/p//text()').getall()
    if description:
        full_des = ''.join([remove_extra_space(text) for text in description]).strip()
        additional_link = parsed_data.xpath('//div[@class="rte"]/p/a[contains(text(), "Read")]/@href').get()
        full_link = urljoin('https://www.cccs.gov.sg/', additional_link) if additional_link else "N/A"
        return full_des, full_link

    # Try to fetch table data
    table = parsed_data.xpath('//table')
    if table:
        header = table.xpath('.//tr/td[1]/p/text()').getall()
        header = [
            ''.join(char for char in h if char not in string.punctuation)
            .replace("\r", "")
            .replace("\t", "")
            .replace("\n", "")
            .replace(" ", "_")
            .lower()
            .strip()
            for h in header
        ]

        data_rows = table.xpath('.//tr/td[2]')

        data = []
        for i, row in enumerate(data_rows):
            # Collect all text inside <p> tags within the current cell
            cell_data = row.xpath('.//p//text()').getall()
            if cell_data:
                # Merge all <p> texts into a single string
                merged_cell_data = ' '.join([remove_extra_space(text) for text in cell_data]).strip()

                # If the header is 'decision_date', convert the date format to 'yy-mm-dd'
                if i < len(header) and header[i] == 'decision_date':
                    try:
                        date_obj = datetime.strptime(merged_cell_data, "%d %B %Y")
                        merged_cell_data = date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        pass  # If date conversion fails, keep the original text

                data.append(merged_cell_data)
            else:
                data.append("N/A")

        if header and data:
            return process_table_data(header, data), "N/A"

        return "N/A", "N/A"

# Function to parse table rows
def get_table_data(selector, column_names, base_url, cookies, headers):
    rows = selector.xpath("//tr[@class='listing-table__table--item']")
    data = []
    for row in rows:
        row_data = {'url': base_url}
        for i, cell in enumerate(row.xpath("td")):
            cell_text = remove_extra_space(cell.xpath("string()").get().strip())

            # Handle date parsing
            try:
                cell_text = datetime.strptime(cell_text, '%d %b %Y').strftime('%Y-%m-%d')
            except ValueError:
                pass

            row_data[column_names[i]] = cell_text

            # Handle links in the cell
            link = cell.xpath(".//a/@href").get()
            if link:
                full_link = urljoin(base_url, link)
                row_data[f"{column_names[i]}_url"] = full_link

                if column_names[i] == 'title':
                    description, media_release_url = fetch_additional_content(full_link, cookies, headers)

                    if isinstance(description, dict):
                        # If description is a table dictionary, update the row with table data
                        row_data.update(description)
                    else:
                        row_data['description'] = description
                        row_data['media_release_url'] = media_release_url

        data.append(row_data)
    return data

# Function to create the output folder
def create_output_folder(folder_name="output"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# Function to save data to an Excel file
def save_to_excel(data, output_folder, file_name="cccs_gov_sg.xlsx"):
    create_output_folder(output_folder)
    output_file = os.path.join(output_folder, file_name)
    df = pd.DataFrame(data)
    df = df.replace('', 'N/A').replace('None', 'N/A')
    df.fillna('N/A', inplace=True)
    df.to_excel(output_file, index=False)
    print(f"Data successfully written to {output_file}")

# Main function to orchestrate the scraping process
def main():
    url = 'https://www.cccs.gov.sg/cases-and-commitments/public-register/abuse-of-dominance'
    cookies = {
        'ASP.NET_SessionId': 'vs1czyo0k1fgftp4no0rrcy2',
        '_ga': 'GA1.1.1062615100.1733892194',
        '_sp_ses.6dfc': '*',
        'rp_www.cccs.gov.sg': '84065d61c040d4c6e0fa3eee7a80f6ce',
        '_sp_id.6dfc': 'bb6c52cc-b02c-4271-b479-4fa4394f11a0.1733892194.2.1733896397.1733893811.e3f01434-802c-4297-92ba-7973aaa2395e.84baf2f6-7e47-4ac9-95c0-ea61a596a1c6.f5af7693-fafb-4889-919c-aea18ae626dd.1733895612467.45',
        'AWSALB': 'Ccqq4vXdPW5PDIUUqPBwGFSR5RZ/8VLZN3534L2eGveoUAPNziBYYAuoT4uQYk6A6+TNqf92u+BrmxDxe+HCb+pebWFzlDUCi7dvYn58kc4c6q4eYO+fMbpmqeDI',
        '_ga_QPKZTNCQR1': 'GS1.1.1733895612.2.1.1733896901.60.0.1444853902',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }

    selector = fetch_webpage(url, cookies, headers)
    column_names = get_column_names(selector)
    data = get_table_data(selector, column_names, url, cookies, headers)
    save_to_excel(data, "output")

if __name__ == "__main__":
    main()
