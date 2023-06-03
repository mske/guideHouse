import requests
from bs4 import BeautifulSoup
import pandas as pd
import random

# Set the URLs of the website
sale_url = "https://www.zillow.com/homes/for_sale/"
rent_url = "https://www.zillow.com/homes/for_rent/"
sold_url = "https://www.zillow.com/homes/recently_sold/"


# user_agent_list = [
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
#     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
# ]

# Set the column names for the CSV file
column_names = ["Category", "House Features", "Address", "State", "Zip Code", "Price", "Open Time"]

# Function to scrape data from a single page
def scrape_page(url, type):
    print(f'scrapping url {url} for {type} category')
    # Pick a random user agent
    # user_agent = random.choice(user_agent_list)
    # Set the headers
    # headers = {'User-Agent': user_agent}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}
    # Send a GET request to the URL
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all the listings on the page
    listings = soup.find_all("article", class_="StyledPropertyCard-c11n-8-85-1__sc-jvwq6q-0 bJNeCb srp__sc-1o67r90-0 kgNiLC property-card list-card_not-saved")

    data = []
    for listing in listings:
        # category_text = listing.find("div", class_="StyledPropertyCardDataArea-c11n-8-85-1__sc-yipmu-0 gxlfal").get_text(strip=True)
        # category = category_text.split('-')[-1].strip()
        category = type
        house_features_list = listing.find("ul", class_="StyledPropertyCardHomeDetailsList-c11n-8-85-1__sc-1xvdaej-0 dmDolk")
        house_features = ''
        for li in house_features_list.find_all("li"):
            house_features += " " + li.get_text(strip=True)
        full_address_list = listing.find("address").get_text(strip=True).split(",")
        address = full_address_list[-3].strip()
        state = full_address_list[-2].strip()
        zip_code = full_address_list[-1].strip()
        price = listing.find("div", class_="srp__sc-16e8gqd-0 gKmVGs").get_text(strip=True)
        open_time_text = listing.find("div", class_="StyledPropertyCardBadgeArea-c11n-8-85-1__sc-wncxdw-0 gKSqTi").get_text(strip=True)
        if "Open:" in open_time_text:
            open_time = open_time_text.strip('Open:')
        else:
            open_time = ""
        data.append([category, house_features, address, state, zip_code, price, open_time])

    return data

# Function to scrape data from all pages
def scrape_all_pages():
    all_data = []

    # Scrape data from the first page
    all_data.extend(scrape_page(sale_url, 'Sale'))
    all_data.extend(scrape_page(rent_url, 'Rent'))
    all_data.extend(scrape_page(sold_url, 'Sold'))

    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}

    sale_response = requests.get(sale_url, headers=headers)
    sale_soup = BeautifulSoup(sale_response.content, "html.parser")
    # Find the total number of sale pages
    sale_total_pages = len(sale_soup.find_all("li", class_="PaginationNumberItem-c11n-8-85-1__sc-bnmlxt-0 eKbbwc"))
    # print(f'sale li {sale_soup.find_all("li")}')
    print(f'sale total pages {sale_total_pages}')

    # Scrape data from remaining sale pages
    for page in range(2, sale_total_pages + 1):
        page_url = sale_url + str(page) + "_p/"
        all_data.extend(scrape_page(page_url, 'Sale'))

    rent_response = requests.get(rent_url, headers=headers)
    rent_soup = BeautifulSoup(rent_response.content, "html.parser")

    # Find the total number of rent pages
    rent_total_pages = len(rent_soup.find_all("li", class_="PaginationNumberItem-c11n-8-84-0__sc-bnmlxt-0 hSDQEI"))
    # print(f'rent li {rent_soup.find_all("li")}')
    print(f'rent total pages {rent_total_pages}')

    # Scrape data from remaining rent pages
    for page in range(2, rent_total_pages + 1):
        page_url = rent_url + str(page) + "_p/"
        all_data.extend(scrape_page(page_url, 'Rent'))

    sold_response = requests.get(sold_url, headers=headers)
    sold_soup = BeautifulSoup(sold_response.content, "html.parser")
    # Find the total number of sold pages
    sold_total_pages = len(sold_soup.find_all("li", class_="PaginationNumberItem-c11n-8-84-0__sc-bnmlxt-0 hSDQEI"))
    # print(f'sold li {sold_soup.find_all("li")}')
    print(f'sold total pages {sold_total_pages}')

    # Scrape data from remaining sold pages
    for page in range(2, sold_total_pages + 1):
        page_url = sold_url + str(page) + "_p/"
        all_data.extend(scrape_page(page_url, 'Sold'))

    return all_data

if __name__ == '__main__':
    # Scrape data from all pages
    data = scrape_all_pages()

    # Create a pandas DataFrame from the scraped data
    df = pd.DataFrame(data, columns=column_names)

    # Save the DataFrame to a CSV file
    df.to_csv("zillow_data.csv", index=False)
