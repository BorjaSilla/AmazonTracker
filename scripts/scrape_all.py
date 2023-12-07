import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import re
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options

def insert_into_mongodb(data_list, mongo_uri, database_name, collection_name):
    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client[database_name]
    collection = db[collection_name]

    products_added = 0

    for data in data_list:
        # Insert data into MongoDB
        collection.insert_one(data)
        products_added += 1
        print(f"ASIN {data['asin']} Added. Total Products added: {products_added}")

    # Close MongoDB connection
    client.close()

# Example usage:
# insert_into_mongodb(data_list, "your_mongo_uri", "your_database_name", "your_collection_name")



def scrape_amazon_url(url, num_pages, mongo_uri, database_name, collection_name):
    counter = 1

    # Options for webdriver
    opciones=Options()
    opciones.add_experimental_option('excludeSwitches', ['enable-automation'])
    opciones.add_experimental_option('useAutomationExtension', False)
    # Start a driver instance
    driver = webdriver.Chrome(opciones)
    driver.get(url)

    data_list = []
        # Extract the category name from the URL
    category_name = re.search(r'/bestsellers/([^/]+)/', url).group(1)
    for page in range(num_pages):
        time.sleep(2)  # Add a delay if needed

        # Close cookies popup - if needed, if not proceed
        try:
            driver.find_element(By.XPATH, '//*[@id="sp-cc-accept"]').click()
            print('Cookies Accepted, starting scrape...')
            print(f'Scraping {category_name} Top 100 ----------------------------------------- page: {counter}')
            time.sleep(1)
        except:
            print("Cookies not needed")
            print(f'Scraping {category_name} Top 100 ----------------------------------------- page: {counter}')
        time.sleep(1)

        # SCROLL TO THE END OF THE PAGE
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)  # Increase the sleep duration to 4 seconds (or adjust as needed)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        time.sleep(2)

        wait = WebDriverWait(driver, 20)  # Adjust the timeout as needed
        caja_productos = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'a-cardui._cDEzb_grid-cell_1uMOS.expandableGrid.p13n-grid-content')))
        #print('The length of caja productos is:', len(caja_productos))

        n_of_reviews = []
        # Extract the number of reviews for each element
        for producto in caja_productos:
            try:
                reviews_element = producto.find_element(By.CSS_SELECTOR, 'a[class="a-link-normal"] span.a-size-small')
                number_of_reviews = str(reviews_element.text).replace('.', '')
                n_of_reviews.append(float(number_of_reviews))
            except:
                n_of_reviews.append(0)


        # Create a list to store the titles
        titles = []

        for producto in caja_productos:
            try:
                # Find the title element using XPath
                title_element = producto.find_element(By.XPATH,
                                                      './/a[contains(@class, "a-link-normal")]/div[contains(@class, "a-section")]/img[contains(@class, "a-dynamic-image")]')

                # Extract the title text from the "alt" attribute of the image
                title_text = title_element.get_attribute('alt')

                if title_text:  # Check if the title is not empty
                    titles.append(title_text)
            except Exception as e:
                print(f"Error while extracting title: {e}")

        ratings = []
        ratings_float = []
        prices = []  # Initialize an empty list to store prices

        for product in caja_productos:
            try:
                price_element = product.find_element(By.CSS_SELECTOR, ".a-size-base.a-color-price ._cDEzb_p13n-sc-price_3mJ9Z")
                price_text = price_element.text
                # Clean the price text (remove currency symbol and replace comma with dot)
                price_text = price_text.replace('€', '').replace(',', '.').strip()
                prices.append(float(price_text))
            except:
                prices.append('0')  # Append '0' when the price selector is not found for a product

        # RATING EXTRACTION AND CLEANING

        for product in caja_productos:
            try:
                rating_element = product.find_element(By.CSS_SELECTOR, "i.a-icon-star-small span.a-icon-alt")
                rating_text = rating_element.get_attribute("textContent")
                if rating_text.strip():
                    rating = rating_text.split(" de ")[0]
                else:
                    rating = '0'
            except:
                rating = '0'

            ratings.append(rating)
            rating_value = rating.replace(',', '.').strip()
            ratings_float.append(float(rating_value))

        # IMAGE EXTRACTION

        image_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-asin] a.a-link-normal img.a-dynamic-image")
        image_links = [image.get_attribute("src") for image in image_elements]

        # ASIN EXTRACTION

        asin_elements = driver.find_elements(By.XPATH, '//div[@data-asin]')
        asin = [i.get_attribute('data-asin') for i in asin_elements]

        # CHECK LEN OF EXTRACTED VALUES (SHOULD = 50)
        print('asin', len(asin), 'title', len(titles), 'precio', len(prices), 'ratings', len(ratings),
              'num_reviews', len(n_of_reviews), 'image links', len(image_links))

        # Create a list of dictionaries for the current page's data, including 'datetime'
        page_data = [
            {
                'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'category': category_name,
                'rank': rank + (page * 50),  # Adjust rank for each page
                'asin': a,
                'title': t,
                'price': p,
                'rating': rt,
                'num_reviews': nr,
                'img_link': il
            }
            for rank, (a, t, p, rt, nr, il) in enumerate(zip(asin, titles, prices, ratings_float, n_of_reviews, image_links), start=1)
        ]

        # Append data to MongoDB
        data_list.extend(page_data)

        # Step 6: Click on the element to navigate to the next page
        try:
            next_page_element = driver.find_element(By.CSS_SELECTOR,
                                                     'div.a-cardui._cDEzb_card_1L-Yx > div.a-text-center > ul > li.a-last')
            next_page_element.click()
            counter += 1
        except:
            print(f"Failed to navigate to page {page + 1}")

    # Insert data into MongoDB
    insert_into_mongodb(data_list, mongo_uri, database_name, collection_name)

    # Close the web driver when you're done
    driver.quit()
    
'''
  # Load environment variables from the .env file
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
print('Mongo_uri: ',mongo_uri)
database_name = "amazon-project"
collection_name = "scrape_collection"
num_pages = 2  # Replace with the number of pages you want to scrape

scrape_amazon_url('https://www.amazon.es/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0', num_pages, mongo_uri, database_name, collection_name)

'''