import requests
import pandas as pd
from bs4 import BeautifulSoup
import re


URL_BRICO = "https://www.bricodepot.ro/bucatarie.html"
URL_DEDEMAN = "https://www.dedeman.ro/ro/mobila-bucatarie/c/84"

def get_container_elements_brico(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    job_elements = soup.find_all("div", class_="product-item-info")
    print("BRICO: Nr rows on page: " , len(job_elements))
    return job_elements


def extract_elements_values_brico(job_elements):
    df = pd.DataFrame()
    for job_element in job_elements:
        title_element = job_element.find("a", class_="product-item-link")
        new_price = job_element.find("span", class_="price") 
        image = job_element.select("img.product-image-photo")[0].get('src')
        # print("title ", title_element.text)
        # print("new_price ", new_price.text)
        # print("image ", image)
        # print("review_count ", review_count)
        entry = pd.DataFrame.from_dict({
        "Name": [title_element.text],
        "Pret":  [new_price.text],
        "Image": [image]
        })

        df = pd.concat([df, entry], ignore_index=True)
    return df

def get_container_elements_dedeman(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    job_elements = soup.find_all("div", class_="product-box")
    print("DEDEMAN: Nr rows on page: " , len(job_elements))
    return job_elements


def extract_elements_values_dedemen(job_elements):
    df = pd.DataFrame()
    for job_element in job_elements:
        title_element = job_element.find("span", class_="product-name")
#     old_price = job_element.find("div", class_="old-price")
        currency = job_element.find("span", class_="currency")
        new_price = job_element.find("div", class_="product-price") 
        image = job_element.select("span.thumbnail img")[0].get('src')
        reviews = job_element.find("span", class_="reviews-count")
        reviews_count = None
        if reviews is not None:
            container_review = reviews.text.split(",")[0]
            reviews_count = re.findall('\(([^)]+)', container_review)
        entry = pd.DataFrame.from_dict({
        "Name": [title_element.text],
        "Pret":  [new_price.text],
        "Currency":  [currency.text],
        "Nr of reviews": [reviews_count],
        "Image": [image]
        })

        df = pd.concat([df, entry], ignore_index=True)
    
    return df



job_elements_brico = get_container_elements_brico(URL_BRICO)
job_elements_dedeman = get_container_elements_dedeman(URL_DEDEMAN)

extract_elements_values_dedemen(job_elements_dedeman).to_csv("dedeman.csv")
extract_elements_values_brico(job_elements_brico).to_csv("brico.csv")
