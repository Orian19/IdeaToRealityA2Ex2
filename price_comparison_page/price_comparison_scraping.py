from typing import List, Dict, Any

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
import undetected_chromedriver as uc
import json
import time
import os

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

allowed_origin = os.getenv('CORS_ORIGIN', 'http://localhost:3000')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Data(BaseModel):
    productName: str


def load_config(cfg_file='cfg.json'):
    """
    loading the json config
    :param cfg_file:
    :return:
    """
    with open(cfg_file) as config_file:
        return json.load(config_file)


def get_webdriver():
    """
    setting up the chrome webdriver with the relevant parameter (with headless mode)
    :return: chrome webdriver
    """
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.106 Safari/537.36")

    driver = uc.Chrome(options=options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win64",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    return driver


def scrape_site(cfg, driver, url, site_name):
    """
    scraping the given websites to get price data for comparison between an itme in different sites
    :param cfg: json cfg
    :param driver: webdriver
    :param url: site webpage
    :param site_name:
    :return: item, price, url
    """
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    item, price, item_url = "Item not found", "Price not available", "URL not found"

    try:
        if site_name == "Best Buy":
            # choosing a country to enter to be able to search the site
            us_link = wait.until(EC.presence_of_element_located((By.XPATH, cfg['xPaths']['bb_country'])))
            us_link.click()
            time.sleep(1)

            # getting item, price, url
            item_element = wait.until(EC.presence_of_element_located((By.XPATH, cfg['xPaths']['bb_item_name'])))
            item = item_element.text
            item_url = item_element.get_attribute('href')
            price = \
                wait.until(EC.presence_of_element_located((By.XPATH, cfg['xPaths']['bb_item_price']))).text.split("$")[1]

        elif site_name == "Walmart":
            # going to the specific item link to get the item, price, url (walmart uses images so need to go the extra mile)
            item_element = wait.until(EC.presence_of_element_located((By.XPATH, cfg['xPaths']['w_item_link'])))
            item_element.click()
            time.sleep(1)  # Consider using WebDriverWait here as well

            # getting item, price, url
            item = wait.until(EC.presence_of_element_located((By.XPATH, cfg['xPaths']['w_item_name']))).text
            item_url = driver.current_url
            price = \
                wait.until(EC.presence_of_element_located((By.XPATH, cfg['xPaths']['w_item_price']))).text.split('$')[1]

        elif site_name == "Newegg":
            # getting item, price, url
            item_element = wait.until(EC.presence_of_element_located((By.XPATH, cfg['xPaths']['ne_item_name'])))
            item = item_element.text
            item_url = item_element.get_attribute('href')
            price_strong = wait.until(
                EC.presence_of_element_located((By.XPATH, cfg['xPaths']['ne_item_price_strong']))).text
            price_sup = wait.until(EC.presence_of_element_located((By.XPATH, cfg['xPaths']['ne_item_price_sup']))).text
            price = price_strong + price_sup

    except NoSuchElementException:
        pass  # Item, Price, and Item URL are already set to default values

    return item, price, item_url


@app.post("/scrape/")
def scrape(product_name: Data):
    """
    main scrape function, scrapes each website separately
    :param product_name:
    :return: site, item name, price, url
    """
    cfg = load_config()

    # sites to scrape
    sites = {
        "Walmart": cfg['sites']['walmart'],
        "Best Buy": cfg['sites']['best_buy'],
        "Newegg": cfg['sites']['newegg']
    }

    # init driver
    driver = get_webdriver()

    results = []
    for site, base_url in sites.items():
        search_url = base_url + product_name.productName.replace(" ", "+")
        title, price, item_url = scrape_site(cfg, driver, search_url, site)
        results.append({'Site': site, 'Item Title Name': title, 'Price(USD)': price, 'Item URL': item_url})

    driver.quit()

    if not results:
        raise HTTPException(status_code=404, detail="Data not found")

    return results


if __name__ == "__main__":
    # running the (fastapi) app
    uvicorn.run("main:app", port=8001, reload=True)
