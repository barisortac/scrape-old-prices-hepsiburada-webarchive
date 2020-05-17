import requests
import re

import bs4 as bs
import urllib.request  # In order to request

import numpy as np
import pandas as pd
import matplotlib as plt
import time



# FIRST GET HISTORICAL LINKS OF PRODUCT USING WEB ARCHIVE API (CDX)
def historical_prices_of_product(product_url):
    # using web_archive cdx api
    api_answer = requests.get(
        "http://web.archive.org/cdx/search/cdx?url={}".format(product_url))
    # take all results that contains date
    raw_api_answer_text = api_answer.text

    # scrape dates to use in webarchive url
    regex_to_find_dates = re.findall(r"\d{14}", raw_api_answer_text)

    product_links = []

    for date in regex_to_find_dates:
        # get web archive link structure
        archive_link = "https://web.archive.org/web/{}/{}".format(date,
                                                                  product_url)
        product_links.append(archive_link)

    return product_links, regex_to_find_dates


# TAKING PRICE FROM HEPSIBURADA.COM using beautiful soup
def hepsiburada_get_price(url):
    # sauce = urllib.request.urlopen(url).read()  # Returns the source code of the given URL
    try:
        sauce = requests.get(url, timeout=20).content
        soup = bs.BeautifulSoup(sauce,
                            'lxml')  # To make beautifulsoup object,the parser used is lxml
        priceBeforePointArray = soup.find_all("span", {
            "data-bind": "markupText:'currentPriceBeforePoint'"})
        priceBeforePoint = priceBeforePointArray[0].text
        priceAfterArray = soup.find_all("span", {
            "data-bind": "markupText:'currentPriceAfterPoint'"})
        priceAfterPoint = priceAfterArray[0].text
    except:
        return "0"

    return priceBeforePoint + "," + priceAfterPoint + " TL"

start_time = time.time()
# product url ##enter product url (hepsiburada.com)
product_url = "https://www.hepsiburada.com/apple-iphone-5s-16-gb-apple-turkiye-garantili-pm-telcepiph5s6gbgo"

# product link and date using historical_prices_of_product function
product_historical_links, dates = historical_prices_of_product(product_url)
sample_interval = 15
sampled_product_historical_links = product_historical_links[::sample_interval]
sampled_dates = dates[::sample_interval]
# %%

result_date_and_price = []

total_count = len(product_historical_links)
count = 0
# loop to get date and price of product using hepsiburada_get_price function
for date_index, link in enumerate(sampled_product_historical_links):
    price = hepsiburada_get_price(link)
    result_date_and_price.append([sampled_dates[date_index], price])
    print(f"{count} / {total_count}, price = {price}")
    count += 1


# %%

# raw format of date and price
print(result_date_and_price)

# %%

# Convert result into beautiful DataFrame
result_array = np.array(result_date_and_price)
date = result_array[:, 0]
price = result_array[:, 1]
df = pd.DataFrame(data=[date, price])
df = df.T
df.columns = ["Date", "Price"]

# Extract "0" prices values (when product no longer available - price is taken as "0")
df.loc[df['Price'] == '0'] = np.nan
df = df.dropna()

# Date and Price columns are dirty, to clean and tidy them:
df['Date'] = df['Date'].apply(lambda x: x[:8])
df['Date'] = df['Date'].apply(lambda x: x[:4] + "/" + x[4:6] + "/" + x[6:8])
df['Date'] = pd.to_datetime(df['Date'], format="%Y/%m/%d")

df['Price'] = df['Price'].apply(lambda x: x[:-3])
df['Price'] = df['Price'].apply(lambda x: re.sub("\.", "", x))
df['Price'] = df['Price'].apply(lambda x: re.sub("\,", ".", x))
df['Price'] = df['Price'].astype('float64')

df.head()

# %%

# 127 historical prices of Iphone 5s is collected.
end_time = time.time()
elapsed_time = end_time - start_time
how_many = len(sampled_product_historical_links)
print(f"It took {elapsed_time} seconds to finish this process.., {how_many} prices were taken..")

df.plot('Date', 'Price', style='*', grid=True)

# %%
