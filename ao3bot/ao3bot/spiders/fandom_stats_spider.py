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

class FandomStatsSpiderSpider(scrapy.Spider):
    logfile("ao3bot_spider.log", maxBytes=1e6, backupCount=3)
    name = 'fandom_stats_spider'
    allowed_domains = ['toscrape.com']
    #start_urls = ['http://toscrape.com/']

    # Using a dummy website to start scrapy request
    def start_requests(self):
        url = "http://quotes.toscrape.com"
        yield scrapy.Request(url=url, callback=self.parse_fandom_stats)

    def get_total(self, text):
        #from text extract number
        logger.info("header: " + str(text))
        totals = [int(s) for s in str(text).split() if s.isdigit()]
        return max(totals)

    def get_totals_dict(self, l):
        #from text extract number
        dict = {}
        logger.info(l)
        for i, s in l:
            count = max([int(x) for x in str(s).split() if x.isdigit()])
            mod_string = ''.join((item for item in s if not item.isalpha()))
            
            dict.update({mod_string:count})
        logger.info(f"ratings: {dict}")
        return dict

    def parse_fandom_stats(self, response):
        base_url = "https://archiveofourown.org"
        logger.info(f"Scraping started at {time.strftime('%H:%M:%S')}")

        # Use headless option to not open a new browser window
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        desired_capabilities = options.to_capabilities()
        driver = webdriver.Chrome(ChromeDriverManager().install(), options = options, desired_capabilities=desired_capabilities)

        #open fandoms_list written by fandoms spider
        with open("fandoms_list.json", "r") as f:
            temp_list = json.load(f)
        
        urls = list(map(lambda x: x.get("fandom_link"), temp_list))
        fandoms = list(map(lambda x: x.get("fandom"), temp_list))

        count = 0
        exception_count = 0

        for i, url in enumerate(urls):

            try:
                #Open fandom page
                driver.get(base_url + url)
                # Explicit wait
                wait = WebDriverWait(driver, 5)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tag")))
                time.sleep(2)
                #temp = driver.find_elements_by_xpath("//dd[@class = 'expandable rating tags']/ul/li")
                
                # Hand-off between Selenium and Scrapy happens here
                sel = Selector(text=driver.page_source)

                total_works = self.get_total(sel.xpath("//h2[@class = 'heading']/text()").getall())
                temp = sel.xpath("//dd[@class = 'expandable rating tags']").getall()
                logger.info(f"getting ratings: {temp}")
                #rating_dict = self.get_totals_dict()
                # warnings_na
                # warnings_notchosen
                # warnings_mcd
                # warnings_violence
                # warnings_underage
                # warnings_noncon
                # cat_mm
                # cat_fm
                # cat_ff
                # cat_gen
                # cat_multi
                # cat_other
                # fandoms
                # characters
                # relationships
                # freeform
                yield {
                    "fandom": fandoms[i],
                    "total_works": total_works,
                    "ratings": rating_dict
                }
                count += 1
            except Exception as e:
                logger.error(f"Exception {e} has occurred with URL: {url}")
                exception_count += 1
            except exceptions as f:
                logger.error(f"Selenium Exception {f} has occured with URL: {url}")
                exception_count += 1
            # Terminating and reinstantiating webdriver every 200 URL to reduce the load on RAM
            if (i != 0) and (i % 200 == 0):
                driver.quit()
                driver = webdriver.Chrome(desired_capabilities=desired_capabilities)
                logger.info("Chromedriver restarted")
            break

        logger.info(f"Scraping ended at {time.strftime('%H:%M:%S')}")
        logger.info(f"Scraped {count} fandoms_stats.")
        driver.quit()
