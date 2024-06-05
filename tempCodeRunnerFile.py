"""
Text Scraping Module for E-commerce Websites

This module scrapes product data from Bricodepot and Dedeman websites, including product names, prices,
images, and reviews. The data is then saved into CSV files.

Modules Required:
    - requests
    - pandas
    - BeautifulSoup (from bs4)
    - re
    - concurrent.futures

Functions:
    - get_container_elements(url, site): Scrapes the product containers from the given website.
    - extract_elements_values(site, job_elements): Extracts product details from the given website containers.
    - scrape_site(url, site): Scrapes and processes data from a given URL and site, saving the results to a CSV file.
"""

import concurrent.futures
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

URL_BRICO = "https://www.bricodepot.ro/bucatarie.html"
URL_DEDEMAN = "https://www.dedeman.ro/ro/mobila-bucatarie/c/84"

def get_container_elements(url, site):
    """
    Scrapes the product containers from the given website.
    
    Parameters:
    url (str): The URL of the page to scrape.
    site (str): The site identifier ('brico' or 'dedeman').
    
    Returns:
    list: A list of BeautifulSoup tag objects containing product details.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    job_elements = []
    if site == 'brico':
        job_elements = soup.find_all("div", class_="product-item-info")
        print(f"BRICO: Nr rows on page: {len(job_elements)}")
    elif site == 'dedeman':
        job_elements = soup.find_all("div", class_="product-box")
        print(f"DEDEMAN: Nr rows on page: {len(job_elements)}")
    return job_elements

def extract_elements_values(site, job_elements):
    """
    Extracts product details from the given website containers.
    
    Parameters:
    site (str): The site identifier ('brico' or 'dedeman').
    job_elements (list): A list of BeautifulSoup tag objects containing product details.
    
    Returns:
    pd.DataFrame: A DataFrame containing product details.
    """
    if site == 'brico':
        df = pd.DataFrame(columns=["Name", "Price", "Image"])
        for job_element in job_elements:
            title_element = job_element.find("a", class_="product-item-link")
            new_price = job_element.find("span", class_="price")
            image = job_element.select("img.product-image-photo")[0].get('src')
            
            if title_element and new_price:
                entry = pd.DataFrame({
                    "Name": [title_element.text.strip()],
                    "Price": [new_price.text.strip()],
                    "Image": [image]
                })
                df = pd.concat([df, entry], ignore_index=True)
                
    elif site == 'dedeman':
        df = pd.DataFrame(columns=["Name", "Price", "Currency", "Nr of Reviews", "Image"])
        for job_element in job_elements:
            title_element = job_element.find("span", class_="product-name")
            new_price = job_element.find("div", class_="product-price")
            currency = job_element.find("span", class_="currency")
            image = job_element.select("span.thumbnail img")[0].get('src')
            reviews = job_element.find("span", class_="reviews-count")
            
            reviews_count = None
            if reviews is not None:
                container_review = reviews.text.split(",")[0]
                reviews_count = re.findall(r'\(([^)]+)', container_review)
                if reviews_count:
                    reviews_count = reviews_count[0]
            
            if title_element and new_price and currency:
                entry = pd.DataFrame({
                    "Name": [title_element.text.strip()],
                    "Price": [new_price.text.strip()],
                    "Currency": [currency.text.strip()],
                    "Nr of Reviews": [reviews_count],
                    "Image": [image]
                })
                df = pd.concat([df, entry], ignore_index=True)
                
    return df

def scrape_site(url, site, filename):
    """
    Scrapes and processes data from a given URL and site, saving the results to a CSV file.
    
    Parameters:
    url (str): The URL of the page to scrape.
    site (str): The site identifier ('brico' or 'dedeman').
    filename (str): The name of the CSV file to save the results.
    """
    job_elements = get_container_elements(url, site)
    df = extract_elements_values(site, job_elements)
    df.to_csv(filename, index=False)

# URLs and site identifiers
urls_sites = [(URL_BRICO, 'brico', 'brico.csv'), (URL_DEDEMAN, 'dedeman', 'dedeman.csv')]

# Scraping data from websites in parallel and saving to CSV files
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(scrape_site, url, site, filename) for url, site, filename in urls_sites]
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as exc:
            print(f'Generated an exception: {exc}')
