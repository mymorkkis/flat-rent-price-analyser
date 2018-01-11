import re, requests
from bs4 import BeautifulSoup
from logger import logger

# http://www.rightmove.co.uk/property-to-rent/find.html/?searchType=RENT&locationIdentifier=REGION%5E66954&insId=1&radius=0.0&minBedrooms=2&maxBedrooms=2&maxDaysSinceAdded=1&houseFlatShare=false


def scrape():
    rightmove_url = ('http://www.rightmove.co.uk/property-to-rent/find.html/'
                     '?searchType=RENT'
                     '&locationIdentifier=REGION%5E66954&insId=1&radius=0.0'
                     '&minBedrooms=2&maxBedrooms=2'
                     '&maxDaysSinceAdded='  # 1
                     '&houseFlatShare=false')

    r = requests.get(rightmove_url)
    if r.status_code < 400:
        if r.status_code != 200:
            logger.warning(f'Status code = {r.status_code}')
        try:
            soup = BeautifulSoup(r.text, 'html.parser')
            divs = soup.find_all('div', class_='is-list')  # replaced 'l-searchResult'
            wanted_divs = []
            for div in divs:
                if 'is-hidden' not in div.attrs['class']:
                    wanted_divs.append(div)
            listings = []
            for div in wanted_divs:
                try:
                    description = get_description(div)
                    postcode_area = get_postcode_area(description)
                    price = get_price(div)
                    if not price > 0:
                        logger.warning(f'{price} not a valid price. Skipping div')
                        continue
                    listings.append((description, postcode_area, price, 'rightmove'))
                except Exception as e:
                    logger.error(f'Error: {e}')
                    continue
            return listings
        except Exception as e:
            logger.error(f'Error: {e}')
            return []
    else:
        logger.error(f'Error code = {r.status_code}')
        return []


def get_description(html_div):
    property_type = html_div.find('h2', class_='propertyCard-title').text.strip()
    address = html_div.find('address', class_='propertyCard-address').span.text.strip()
    description = f'{property_type}: {address}'
    return description


def get_postcode_area(description):
    postcode_search = re.search('[A-Z][A-Z]\d+', description)
    if postcode_search:
        postcode_area = postcode_search.group()
    else:
        postcode_area = ''
    return postcode_area


def get_price(html_div):
    price_and_month = html_div.find('span', class_='propertyCard-priceValue').text.strip()
    # String has pcm letters with price i.e. 999.00 pcm. Use regex to select only price
    price = extract_price(price_and_month)
    return price


def extract_price(original_string):
    price = re.search('\d+(,\d+)?(.\d+)?', original_string)
    if price:
        price = price.group().replace(',', '')
        # Remove decimal place and pence
        if '.' in price:
            price, _ = price.split('.')
        return int(price)
    else:
        return 0