from fastapi import FastAPI, HTTPException
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import pandas as pd
import uvicorn
import time

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # This is for development only!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Data(BaseModel):
    productName: str = None


def get_webdriver():
    options = uc.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = uc.Chrome(options=options)

    return driver


def scrape_site(driver, url, site_name):
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    if site_name == "Best Buy":
        us_link = driver.find_element(By.XPATH, '(//div[@class="country-selection"])[1]//a[@class="us-link"]')
        us_link.click()
        time.sleep(1)

        item = driver.find_element(By.XPATH, "//ol[@class=\"sku-item-list\"]//li[@class=\"sku-item\"][1]//h4[@class=\"sku-title\"]/a").text
        price = driver.find_element(By.XPATH, "//ol[@class=\"sku-item-list\"]//li[@class=\"sku-item\"][1]//div[@class=\"sku-list-item-price\"]//span[1]").text
        price = price.split("$")[1]
    elif site_name == "Walmart":
        item_link = driver.find_element(By.XPATH, "//*[@id=\"0\"]/section/div/div[1]/div/div/a")
        item_link.click()
        time.sleep(1)

        item = driver.find_element(By.XPATH, "//*[@id=\"main-title\"]").text
        price = driver.find_element(By.XPATH, "//*[@id=\"maincontent\"]/section/main/div[2]/div[2]/div/div[1]/div/div[2]/div/div/span[1]/span[2]/span").text
        price = price.split('$')[1]
    elif site_name == "Newegg":
        item = driver.find_element(By.XPATH, "//div[@class=\"item-cell\"][1]//a[@class=\"item-title\"]").text
        price = (driver.find_element(By.XPATH, "//div[@class=\"item-cell\"][1]//div[@class=\"item-action\"]//ul[@class=\"price\"]//li[3]/strong").text +
                 driver.find_element(By.XPATH, "//div[@class=\"item-cell\"][1]//div[@class=\"item-action\"]//ul[@class=\"price\"]//li[3]/sup").text)

    else:
        item = "Item not found"
        price = "Price not available"

    return item, price


@app.post("/scrape/")
def scrape(product_name: Data):  # Note: This is now a regular function, not async.
    sites = {
        "Walmart": "https://www.walmart.com/search/?query=",
        "Best Buy": "https://www.bestbuy.com/site/searchpage.jsp?st=",
        "Newegg": "https://www.newegg.com/p/pl?d="
    }
    results = []

    driver = get_webdriver()

    for site, base_url in sites.items():
        search_url = base_url + product_name.productName.replace(" ", "+")
        title, price = scrape_site(driver, search_url, site)
        results.append({'Site': site, 'Item Title Name': title, 'Price(USD)': price})

    driver.quit()

    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Data not found")


if __name__ == "__main__":
    uvicorn.run(app, port=8001)

