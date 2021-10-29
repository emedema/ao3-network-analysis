import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from webdriver_manager.chrome import ChromeDriverManager
from logzero import logger, logfile
import json
import time


class FandomsSpiderSpider(scrapy.Spider):
    logfile("ao3bot_spider.log", maxBytes=1e6, backupCount=3)
    name = 'fandoms_spider'
    allowed_domains = ['toscrape.com']
    #start_urls = ['http://toscrape.com/']

    # Using a dummy website to start scrapy request
    def start_requests(self):
        url = "http://quotes.toscrape.com"
        yield scrapy.Request(url=url, callback=self.parse_fandoms)

    def parse_fandoms(self, response):
        logger.info(f"Scraping started at {time.strftime('%H:%M:%S')}")

        # Use headless option to not open a new browser window
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        desired_capabilities = options.to_capabilities()
        driver = webdriver.Chrome(ChromeDriverManager().install(),options = options, desired_capabilities=desired_capabilities)

        # Load the fandom categories list written by fandom_categories spider
        with open("fandom_categories_list.json", "r") as f:
            temp_list = json.load(f)

        urls = list(map(lambda x: x.get("fandom_cat_link"), temp_list))
        count = 0
        exception_count = 0

        for i, url in enumerate(urls):

            try:
                # Opening locations webpage
                driver.get(url)
                # Explicit wait
                wait = WebDriverWait(driver, 5)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tag")))
                time.sleep(2)

                # Hand-off between Selenium and Scrapy happens here
                sel = Selector(text=driver.page_source)
                #TODO: customize for list of fandoms
                # Extract fandom name and fandom link
                fandoms = sel.xpath("//li/a[@class = 'tag']/text()").getall()
                fandom_link = sel.xpath("//li/a[@class = 'tag']/@href").getall()

                fandom_count = 0
                # Using Scrapy's yield to store output instead of explicitly writing to a JSON file
                for i in range(len(fandoms)):
                    yield {
                        "fandom": fandoms[i],
                        "fandom_link": fandom_link[i]
                    }
                    fandom_count += 1
            except Exception as e:
                logger.error(f"Exception {e} has occured with URL: {url}")
                exception_count += 1
            except exceptions as f:
                logger.error(f"Selenium Exception {f} has occured with URL: {url}")
                exception_count += 1

            # Terminating and reinstantiating webdriver every 200 URL to reduce the load on RAM
            if (i != 0) and (i % 200 == 0):
                driver.quit()
                driver = webdriver.Chrome(desired_capabilities=desired_capabilities)
                logger.info("Chromedriver restarted")

        logger.info(f"Scraping ended at {time.strftime('%H:%M:%S')}")
        logger.info(f"Scraped {fandom_count} fandoms.")
        driver.quit()