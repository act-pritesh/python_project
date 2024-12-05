import os
import re
from datetime import datetime

import requests
from parsel import Selector
from jsonpath_ng import jsonpath, parse
import pandas as pd


headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.9',
    'apikey': 'z9duUaFUiEUYSHs97CU38fcZO7ipOPvm',
    'content-type': 'application/json; charset=utf-8',
    'origin': 'https://www.worldbank.org',
    'priority': 'u=1, i',
    'referer': 'https://www.worldbank.org/',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
}
cookies = {
    'check': 'true',
    'AMCVS_1E7B833554B8360D0A4C98A5%40AdobeOrg': '1',
    's_cc': 'true',
    'ai_user': 'lMthN|2024-10-21T09:53:42.824Z',
    '_fbp': 'fb.1.1729504424769.937085153340509453',
    '_gcl_au': '1.1.555870654.1729504427',
    'at_check': 'true',
    'QSI_SI_0fyBfcKBwUPvE4m_intercept': 'true',
    's_sq': '%5B%5BB%5D%5D',
    'AMCV_1E7B833554B8360D0A4C98A5%40AdobeOrg': '179643557%7CMCIDTS%7C20018%7CMCMID%7C63179255810145781740083176260034820066%7CMCAAMLH-1730181859%7C12%7CMCAAMB-1730181859%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1729584259s%7CNONE%7CMCAID%7CNONE%7CMCCIDH%7C0%7CvVersion%7C5.5.0',
    'mbox': 'PC#73ff0c242cb34007a0e650dba7f21708.41_0#1792821860|session#3e529405beb04b4990c0f40c903a5891#1729579806',
    's_plt': '29.29%2Cen%3Awb%3Amain%3A%2Fen%2Fprojects-operations%2Fprocurement%2Fdebarred-firms',
    'AWSALB': 'd6qA2d38mz0TJOv5xPM9TV2ddbfnuTbeJzhHLgZ053d1pZXPTvzD6K3+KvJWwqLXVqXkr6Sfh902OTNFZpuazTHKb+7aL/lfKZza5qj20Moq4lWT3GWEm4hzOuUh',
    'AWSALBCORS': 'd6qA2d38mz0TJOv5xPM9TV2ddbfnuTbeJzhHLgZ053d1pZXPTvzD6K3+KvJWwqLXVqXkr6Sfh902OTNFZpuazTHKb+7aL/lfKZza5qj20Moq4lWT3GWEm4hzOuUh',
    's_ips': '609',
    's_tp': '148051',
    's_vnc365': '1761115942310%26vn%3D6',
    's_ivc': 'true',
    's_inv': '1996',
    's_ppn': 'en%3Awb%3Amain%3A%2Fen%2Fprojects-operations%2Fprocurement%2Fdebarred-firms',
    '__cf_bm': '0qFbOCiQi0usZ6clUmn5Vrysx3wmhJLIC2vkoTLbCNQ-1729580945-1.0.1.1-HLUvWc7ZK45enG8mxP17HubJprPxGyIJsJSDS82GgN70xQ8cvD.4nWr7djJPMOiPXkEgY5HD14.26SDhSDUm1g',
    'ai_session': 'RsNdE|1729569678676|1729581245613.5',
    's_nr730': '1729581277490-Repeat',
    's_tslv': '1729581277493',
    's_ppv': 'en%253Awb%253Amain%253A%252Fen%252Fprojects-operations%252Fprocurement%252Fdebarred-firms%2C0%2C100%2C98%2C148050%2C249%2C249',
}

# Function to fetch page content and return Selector object
def fetch_page_content(url, headers,cookies):
    response = requests.get(url, headers=headers,cookies=cookies)
    if response.status_code == 200:
        try:
            return response.text if 'html' in response.headers.get('Content-Type', '') else response.json()
        except ValueError:
            print("Response is not in JSON format")
            return None
    return None

# Function to remove specific punctuation from text
def remove_specific_punctuation(text):
    punctuation_marks = [
        ".", ",", "?", "!", ":", ";", "—", "-", "'", '"', "[", "]", "{", "}", "…", "\\", "@", "&", "*",
        "_", "^", "~", "`", "/", "“", "”", "(", ")","  "
    ]
    for char in punctuation_marks:
        text = str(text).replace(char, '')
    return text

# Function to remove non-alphanumeric characters, except spaces
def remove_non(text):
    return re.sub(r'[^\w\s]', '', text)

# Function to check if text contains non-Latin characters
def contains_non_latin(text):
    return bool(re.search(r'[^\x00-\x7F]', text))

# Function to extract alias from the firm name
def extract_alias(firm_name):
    # Look for parentheses first
    aliases = re.findall(r'\([^()]*\)', firm_name)
    cleaned_aliases = []

    if aliases:
        for alias in aliases:
            if re.search(r'\d', alias):  # Skip aliases with numbers
                continue

            cleaned_alias = remove_specific_punctuation(alias.strip())
            cleaned_alias = remove_non(cleaned_alias)

            if cleaned_alias:
                cleaned_aliases.append(cleaned_alias)

        combined_alias = ' | '.join(cleaned_aliases)

        # Remove parentheses content and clean firm name
        cleaned_name = re.sub(r'\s*\(.*?\)', '', firm_name).strip()
        cleaned_name = remove_specific_punctuation(cleaned_name)
        cleaned_name = remove_non(cleaned_name)

        if combined_alias.lower() == "n/a" or combined_alias.strip() == "|":
            return combined_alias, cleaned_name

        return combined_alias, cleaned_name

    # If no alias in parentheses, check for non-Latin text as alias
    non_latin_alias = None
    if contains_non_latin(firm_name):
        # Extract the non-Latin part as the alias
        non_latin_alias = ''.join(re.findall(r'[^\x00-\x7F]+', firm_name))

        # Remove non-Latin characters from the firm name
        cleaned_name = re.sub(r'[^\x00-\x7F]', '', firm_name).strip()
    else:
        cleaned_name = firm_name.strip()

    # Clean both firm name and non-Latin alias
    cleaned_name = remove_specific_punctuation(cleaned_name)
    cleaned_name = remove_non(cleaned_name)

    if non_latin_alias:
        non_latin_alias = remove_specific_punctuation(non_latin_alias)
        non_latin_alias = remove_non(non_latin_alias)

    return non_latin_alias, cleaned_name


def correct_spelling_errors(date_str):
    # Dictionary of common spelling mistakes
    corrections = {
        "Feberuary": "February",
        # Add more corrections if needed
    }
    # Correct spelling
    for wrong, correct in corrections.items():
        date_str = date_str.replace(wrong, correct)
    return date_str
# Function to format a date in 'yyyy-mm-dd' format
def format_date(date_str):
    try:
        # Correct spelling errors
        date_str = correct_spelling_errors(date_str)

        # Check if the date is already in YYYY-MM-DD format
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str

        # Parse date in 'Month DD, YYYY' format
        date_obj = datetime.strptime(date_str, '%B %d, %Y')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return None


def parse_html_data(html_content, url2):
    parsed_data = Selector(html_content)
    table = parsed_data.xpath('//div[@class="c14v1-body c14v1-body-covid c14v1-body-text flipboard-keep "]/table')
    html_results = []

    for row in table.xpath('.//tr')[1:]:  # Skip the header row
        # Extract data from each column
        firm_name = [' '.join(row.xpath('./td[1]').getall())]
        date_imposition = [row.xpath('./td[2]').getall()]
        sanction_imposed = [row.xpath('./td[3]').getall()]
        grounds = [row.xpath('./td[4]').getall()]

        html_results += extract_company_and_dates(firm_name, date_imposition, sanction_imposed, grounds, url2)

    return pd.DataFrame(html_results)


def json_data(json_response, url2):
    jsonpath_expr1 = parse('$..SUPP_NAME')
    jsonpath_expr8 = parse('$..ADD_SUPP_INFO')
    jsonpath_expr2 = parse('$..SUPP_ADDR')
    jsonpath_expr3 = parse('$..SUPP_CITY')
    jsonpath_expr4 = parse('$..COUNTRY_NAME')
    jsonpath_expr5 = parse('$..DEBAR_FROM_DATE')
    jsonpath_expr6 = parse('$..DEBAR_TO_DATE')
    jsonpath_expr7 = parse('$..DEBAR_REASON')
    jsonpath_expr9 = parse('$..INELIGIBLY_STATUS')
    jsonpath_expr10=parse('$..SUPP_STATE_CODE')

    # Find all matches in the JSON
    firm_names = [match.value for match in jsonpath_expr1.find(json_response)]
    add_firm_name = [match.value for match in jsonpath_expr8.find(json_response)]
    full_firm_names = [
        f"{name or ''} {add or ''}".strip()
        for name, add in zip(firm_names, add_firm_name)
    ]
    supp_address = [match.value for match in jsonpath_expr2.find(json_response)]
    supp_city = [match.value for match in jsonpath_expr3.find(json_response)]
    country = [match.value for match in jsonpath_expr4.find(json_response)]
    ineligibility_period_from_date = [match.value for match in jsonpath_expr5.find(json_response)]
    ineligibility_period_to_date = [match.value for match in jsonpath_expr6.find(json_response)]
    grounds = [match.value for match in jsonpath_expr7.find(json_response)]
    ineligibility_status = [match.value for match in jsonpath_expr9.find(json_response)]
    state_code=[match.value for match in jsonpath_expr10.find(json_response)]

    result = []
    for i in range(len(full_firm_names)):
        alias, cleaned_firm_name = extract_alias(full_firm_names[i])
        cleaned_firm_name = remove_specific_punctuation(cleaned_firm_name)

        # Format the JSON dates to 'yyyy-mm-dd'
        start_date = ineligibility_period_from_date[i] if i < len(ineligibility_period_from_date) else None
        end_date = ineligibility_period_to_date[i] if i < len(ineligibility_period_to_date) else None

        entry = {
            'Url': url2,
            'Firm_Name': cleaned_firm_name,
            'Alias': alias if alias else None,
            'Address': (
                re.sub(r'\s+', ' ',
                       f"{supp_address[i] if supp_address[i] else ''} {supp_city[i] if supp_city[i] else ''} {state_code[i] if state_code[i] else ''}").strip()
                if i < len(supp_address) and (
                            supp_address[i] or supp_city[i] or (i < len(state_code) and state_code[i]))
                else "N/A"
            ),
            'Country': country[i] if i < len(country) else None,
            'Ineligibility_Period_From_date': start_date,
            'Ineligibility_Period_To_date': end_date,
            'Grounds': re.sub(r'\s+', ' ',grounds[i] if i < len(grounds) else None),
            'start_date_of_inspection_section': "N/A",  # Add the date field from JSON data
            'end_date_of_inspection_section': "N/A"
        }
        result.append(entry)

    return pd.DataFrame(result)


def extract_company_and_dates(lis, lis2, lis3, lis4, url2):
    results = []

    for index, item in enumerate(lis):
        # Extract the name and address from the company data
        td_pattern = r'<td.*?>(.*?)</td>'
        td_match = re.search(td_pattern, item, re.DOTALL)
        name, address, alias, cleaned_name = None, None, None, None

        if td_match:
            td_content = td_match.group(1).strip()
            name_pattern = r'(.*?)\*([0-9]{2})(.*)'
            name_match = re.search(name_pattern, td_content, re.DOTALL)
            if name_match:
                name = name_match.group(1).strip() + " *" + name_match.group(2).strip()
                address = name_match.group(3).strip()
                name = re.sub(r'<[^>]+>', '', name).strip()  # Remove HTML tags from name
                address = re.sub(r'<[^>]+>', '', address).strip()  # Remove HTML tags from address

                # Extract alias and clean the firm name
                alias, cleaned_name = extract_alias(name)

                # Remove specific punctuation from the cleaned firm name
                cleaned_name = remove_specific_punctuation(cleaned_name)

        # Extract the dates from the date data
        date_item = lis2[index][0]
        clean_content = re.sub(r'<[^>]+>', '', date_item).strip()  # Remove HTML tags from date data
        start_date_str, end_date_str = None, None

        if "Ongoing" in clean_content:
            start_date_str, end_date_str = "Ongoing", ""
        else:
            # Support different types of dashes (en-dash, em-dash, hyphen)
            date_range_pattern = r'([A-Za-z]+ \d{1,2}, \d{4})\s*(?:-|–|—)\s*([A-Za-z]+ \d{1,2}, \d{4})?'  # Add optional second date
            date_match = re.search(date_range_pattern, clean_content)
            if date_match:
                start_date_str = format_date(date_match.group(1).strip())  # Format start date
                end_date_str = format_date(date_match.group(2).strip()) if date_match.group(2) else None

        # Extract the sanction information
        sanction_item = lis3[index][0]
        sanction_clean_content = re.sub(r'<[^>]+>', '', sanction_item).strip()  # Remove HTML tags from sanction data

        # Extract the grounds information
        grounds_item = lis4[index][0]
        grounds_clean_content = re.sub(r'<[^>]+>', '', grounds_item).strip()  # Remove HTML tags from grounds data

        # Store the result in a dictionary if the name is valid
        if cleaned_name:
            results.append({
                'Url': url2,
                'Firm_Name': cleaned_name,  # Use the cleaned firm name without punctuation
                'alias': alias if alias==" " else 'N/A',  # Use the alias extracted from the firm name
                'Address': address,
                'Country': "N/A",  # HTML does not provide country information
                'Ineligibility_Period_From_date': "N/A",  # Corrected this field
                'Ineligibility_Period_To_date': "N/A",  # Corrected this field
                'Grounds': grounds_clean_content,
                'Sanction_Imposed': sanction_clean_content,
                'start_date_of_inspection_section': start_date_str,  # Also include original fields
                'end_date_of_inspection_section': end_date_str,
            })

    return results

# Main scraping function
def scrape_worldbank_data():
    url = 'https://apigwext.worldbank.org/dvsvc/v1.0/json/APPLICATION/ADOBE_EXPRNCE_MGR/FIRM/SANCTIONED_FIRM'
    url2 = 'https://www.worldbank.org/en/projects-operations/procurement/debarred-firms'

    # Fetch data
    json_response = fetch_page_content(url, headers, None)
    parsed_html = fetch_page_content(url2, headers, cookies)

    # Parse JSON and HTML data
    json_df = json_data(json_response, url2) if isinstance(json_response, dict) else None
    html_df = parse_html_data(parsed_html, url2) if isinstance(parsed_html, str) else None

    return json_df, html_df


# Save the scraped data to Excel
def save_data_to_excel(df):
    if isinstance(df, pd.DataFrame):
        df = df.replace('', 'N/A').replace('None', 'N/A')
        df.fillna('N/A', inplace=True)
        # df.to_excel(filename, index=False)
        output_folder = "output"
        create_output_folder(output_folder)

        # Save the data to Excel inside the created folder
        output_file = os.path.join(output_folder, "worldbank_org.xlsx")
        df.to_excel(output_file, index=False)

        print(f"Data successfully written to {output_file}")
    else:
        print("Error: The data passed is not a DataFrame.")


def create_output_folder(folder_name="output"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
# Run the scraper and save the data
def main():
    json_df, html_df = scrape_worldbank_data()

    if json_df is not None and html_df is not None:
        combined_df = pd.concat([json_df, html_df], ignore_index=True)

        # Replace any NaN values with 'N/A'
        combined_df.replace('  ', 'N/A', inplace=True)
        combined_df.fillna('N/A', inplace=True)

        # Save the combined DataFrame to Excel
        save_data_to_excel(combined_df)
    else:
        print("Failed to scrape both JSON and HTML data.")


if __name__ == "__main__":
    main()