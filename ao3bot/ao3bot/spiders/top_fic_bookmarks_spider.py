import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from logzero import logger, logfile
import json
import time
import re
import os

class TopFicBookmarksSpiderSpider(scrapy.Spider):
    logfile("ao3bot_spider_bookmarks.log", maxBytes=1e6, backupCount=3)
    name = 'top_fic_bookmarks_spider'
    allowed_domains = ['toscrape.com']
    #start_urls = ['http://toscrape.com/']

    # Using a dummy website to start scrapy request
    def start_requests(self):
        url = "http://quotes.toscrape.com"
        yield scrapy.Request(url=url, callback=self.parse_fandom_stats)

    def get_total(self, text):
        #from text extract number
        totals = [int(s) for s in str(text).split() if s.isdigit()]
        return max(totals)
    
    def get_users(self, l):
        #from text extract number
        user_list = []
        for item in l:
            quote_indexes = [x for x, z in enumerate(item) if z == '\"']
            text_open = [x for x, z in enumerate(item) if z == '<']
            text_close = [x for x, z in enumerate(item) if z == '>']
            user_link = item[quote_indexes[0]+1:quote_indexes[1]]
            user_name = item[text_close[0]+1:text_open[1]]
            user_list.append({
                "user_link": user_link, 
                "user_name": user_name
                })
        return user_list
    
    def get_info(self, item):
        
        quote_indexes = [x for x, z in enumerate(item) if z == '\"']
        text_open = [x for x, z in enumerate(item) if z == '<']
        text_close = [x for x, z in enumerate(item) if z == '>']
        fic_link = item[quote_indexes[0]+1:quote_indexes[1]]
        fic_name = item[text_close[0]+1:text_open[1]]
        fic = {
            "fic_link": fic_link, 
            "fic_name": fic_name
        }
        return fic
    
    def check_consent(self, driver):
        # Open provided link in a browser window using the driver
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'tos_agree'))
            )
            element.click()
            btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'accept_tos'))
            )
            btn.click()
            return
        finally:
            print("TOS Form accepted.")
    
    def parse_fandom_stats(self, response):
        base_url = "https://archiveofourown.org"
        logger.info(f"Scraping started at {time.strftime('%H:%M:%S')}")

        # Use headless option to not open a new browser window
        options = webdriver.ChromeOptions()
        #options.add_argument("headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        desired_capabilities = options.to_capabilities()
        driver = webdriver.Chrome(ChromeDriverManager().install(), options = options, desired_capabilities=desired_capabilities)

        #open fandoms_list written by fandoms spider
        with open("pop_fandoms_clean.json", "r") as f:
            temp_list = json.load(f)
        
        urls = list(map(lambda x: x.get("fandom_link"), temp_list))
        #urls = ['/tags/Eagles%20(TV%202019)/works']
        fandoms = list(map(lambda x: x.get("fandom"), temp_list))

        count = 0
        exception_count = 0
        restarted = False
        for i, url in enumerate(urls):

            try:
                #Open fandom page
                driver.get(url)
                time.sleep(5)
                #page_html = driver.page_source
                #check TOS
                if count == 0 or restarted == True:
                    self.check_consent(driver)
                    logger.info("TOS Accepted")
                    restarted = False

                #wait
                wait = WebDriverWait(driver, 5)
                wait.until(EC.presence_of_element_located((By.ID, "work_search_sort_column")))
                time.sleep(2)

                driver.execute_script("document.querySelector('#work_search_sort_column').value = 'bookmarks_count'")
                #driver.execute_script("$x('/html/body/div[1]/div[2]/div/form/fieldset/dl/dd[1]/input')[0].click()")
                driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/form/fieldset/dl/dd[1]/input').click()
                
                wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div/ol[2]/li[1]/dl/dd[@class='bookmarks']/a")))
                time.sleep(2)
                
                #driver.execute_script("$x('/html/body/div[1]/div[2]/div/ol[2]/li[1]/dl/dd[6]/a')[0].click()")
                driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/ol[2]/li[1]/dl/dd[@class="bookmarks"]/a').click()
                
                wait.until(EC.presence_of_element_located((By.XPATH, "//h2[@class = 'heading']")))
                time.sleep(2)

                # Hand-off between Selenium and Scrapy happens here
                sel = Selector(text=driver.page_source)

                total_works = self.get_total(sel.xpath("//h2[@class = 'heading']/text()").getall())
                users = self.get_users(sel.xpath("//h5[@class = 'byline heading']/a").getall())
                fic_info = self.get_info(sel.xpath("//h4[@class='heading']/a").get())
                
                yield {
                    "fandom": fandoms[i],
                    "total_bookmarks": total_works,
                    "users": users,
                    "fic_info": fic_info
                }
                count += 1
            except Exception as e:
                logger.error(f"Exception {e} has occurred with URL: {url}")
                exception_count += 1
            except exceptions as f:
                logger.error(f"Selenium Exception {f} has occured with URL: {url}")
                exception_count += 1
            # Terminating and reinstantiating webdriver every 70 URL to reduce the load on RAM
            if (i != 0) and (i % 200 == 0):
                time.sleep(100)
                driver.quit()
                driver = webdriver.Chrome(ChromeDriverManager().install(), options = options, desired_capabilities=desired_capabilities)
                logger.info("Chromedriver restarted")
                restarted = True
            

        logger.info(f"Scraping ended at {time.strftime('%H:%M:%S')}")
        logger.info(f"Scraped {count} fandoms_stats.")
        driver.quit()
