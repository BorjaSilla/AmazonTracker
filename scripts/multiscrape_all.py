import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import csv
import re
import multiprocessing
#from scrape_links import links
from scrape_all import scrape_amazon_url
import os
from dotenv import load_dotenv

links = ['https://www.amazon.es/gp/bestsellers/grocery/ref=zg_bs_nav_grocery_0', 'https://www.amazon.es/gp/bestsellers/boost/ref=zg_bs_nav_boost_0', 'https://www.amazon.es/gp/bestsellers/amazon-renewed/ref=zg_bs_nav_amazon-renewed_0', 'https://www.amazon.es/gp/bestsellers/mobile-apps/ref=zg_bs_nav_mobile-apps_0', 'https://www.amazon.es/gp/bestsellers/baby/ref=zg_bs_nav_baby_0', 'https://www.amazon.es/gp/bestsellers/beauty/ref=zg_bs_nav_beauty_0', 'https://www.amazon.es/gp/bestsellers/tools/ref=zg_bs_nav_tools_0', 'https://www.amazon.es/gp/bestsellers/music/ref=zg_bs_nav_music_0', 'https://www.amazon.es/gp/bestsellers/gift-cards/ref=zg_bs_nav_gift-cards_0', 'https://www.amazon.es/gp/bestsellers/climate-pledge/ref=zg_bs_nav_climate-pledge_0', 'https://www.amazon.es/gp/bestsellers/automotive/ref=zg_bs_nav_automotive_0', 'https://www.amazon.es/gp/bestsellers/sports/ref=zg_bs_nav_sports_0', 'https://www.amazon.es/gp/bestsellers/amazon-devices/ref=zg_bs_nav_amazon-devices_0', 'https://www.amazon.es/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0', 'https://www.amazon.es/gp/bestsellers/appliances/ref=zg_bs_nav_appliances_0', 'https://www.amazon.es/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0', 'https://www.amazon.es/gp/bestsellers/lighting/ref=zg_bs_nav_lighting_0', 'https://www.amazon.es/gp/bestsellers/industrial/ref=zg_bs_nav_industrial_0', 'https://www.amazon.es/gp/bestsellers/computers/ref=zg_bs_nav_computers_0', 'https://www.amazon.es/gp/bestsellers/musical-instruments/ref=zg_bs_nav_musical-instruments_0', 'https://www.amazon.es/gp/bestsellers/lawn-garden/ref=zg_bs_nav_lawn-garden_0', 'https://www.amazon.es/gp/bestsellers/toys/ref=zg_bs_nav_toys_0', 'https://www.amazon.es/gp/bestsellers/books/ref=zg_bs_nav_books_0', 'https://www.amazon.es/gp/bestsellers/fashion/ref=zg_bs_nav_fashion_0', 'https://www.amazon.es/gp/bestsellers/dmusic/ref=zg_bs_nav_dmusic_0', 'https://www.amazon.es/gp/bestsellers/office/ref=zg_bs_nav_office_0', 'https://www.amazon.es/gp/bestsellers/dvd/ref=zg_bs_nav_dvd_0', 'https://www.amazon.es/gp/bestsellers/handmade/ref=zg_bs_nav_handmade_0', 'https://www.amazon.es/gp/bestsellers/pet-supplies/ref=zg_bs_nav_pet-supplies_0', 'https://www.amazon.es/gp/bestsellers/hpc/ref=zg_bs_nav_hpc_0', 'https://www.amazon.es/gp/bestsellers/software/ref=zg_bs_nav_software_0', 'https://www.amazon.es/gp/bestsellers/digital-text/ref=zg_bs_nav_digital-text_0', 'https://www.amazon.es/gp/bestsellers/videogames/ref=zg_bs_nav_videogames_0']



# Function to scrape a single link
def scrape_single_link(link):
    # Load environment variables from the .env file
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    database_name = "amazon-project"
    collection_name = "scrape_collection"
    num_pages = 2  # Replace with the number of pages you want to scrape
    try:
        scrape_amazon_url(link, num_pages, mongo_uri, database_name, collection_name)
    except Exception as e:
        print(f"Error scraping {link}: {str(e)}")

if __name__ == '__main__':
    # Number of processes to create (you can adjust this as needed)
    num_processes = 8

    # Create a multiprocessing pool to run the scraping function in parallel
    with multiprocessing.Pool(num_processes) as pool:
        pool.map(scrape_single_link, links)