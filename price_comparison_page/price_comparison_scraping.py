from selenium.webdriver.common.by import By
from selenium_stealth import stealth
import undetected_chromedriver as uc
import json
import time

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Data(BaseModel):
    productName: str = None


def load_config(cfg_file):
    with open(cfg_file) as config_file:
        return json.load(config_file)


def get_webdriver():
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
    driver.get(url)
    time.sleep(3)  # Wait for the page to load
    if site_name == "Best Buy":
        us_link = driver.find_element(By.XPATH, cfg['xPaths']['bb_country'])
        us_link.click()
        time.sleep(1)

        item = driver.find_element(By.XPATH, cfg['xPaths']['bb_item_name'])
        item_url = item.get_attribute('href')
        item = item.text
        price = driver.find_element(By.XPATH, cfg['xPaths']['bb_item_price']).text
        price = price.split("$")[1]
    elif site_name == "Walmart":
        item_link = driver.find_element(By.XPATH, cfg['xPaths']['w_item_link'])
        item_link.click()
        time.sleep(1)

        item = driver.find_element(By.XPATH, cfg['xPaths']['w_item_name']).text
        item_url = driver.current_url
        price = driver.find_element(By.XPATH, cfg['xPaths']['w_item_price']).text
        price = price.split('$')[1]
    elif site_name == "Newegg":
        item = driver.find_element(By.XPATH, cfg['xPaths']['ne_item_name'])
        item_url = item.get_attribute('href')
        item = item.text
        price = (driver.find_element(By.XPATH, cfg['xPaths']['ne_item_price_strong']).text +
                 driver.find_element(By.XPATH, cfg['xPaths']['ne_item_price_sup']).text)

    else:
        item = "Item not found"
        price = "Price not available"
        item_url = "Item URL not found"

    return item, price, item_url


@app.post("/scrape/")
def scrape(product_name: Data):  # Note: This is now a regular function, not async.
    cfg = load_config('cfg.json')

    sites = {
        "Walmart": cfg['sites']['walmart'],
        "Best Buy": cfg['sites']['best_buy'],
        "Newegg": cfg['sites']['newegg']
    }

    driver = get_webdriver()

    results = []
    for site, base_url in sites.items():
        search_url = base_url + product_name.productName.replace(" ", "+")
        title, price, item_url = scrape_site(cfg, driver, search_url, site)
        results.append({'Site': site, 'Item Title Name': title, 'Price(USD)': price, 'Item URL': item_url})

    driver.quit()

    if results:
        return results
    else:
        raise HTTPException(status_code=404, detail="Data not found")


def main():
    uvicorn.run(app, port=8001)


if __name__ == "__main__":
    main()
