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



class CharacterNetworkSpiderSpider(scrapy.Spider):
    logfile("ao3bot_spider_character_network.log", maxBytes=1e6, backupCount=3)
    name = 'character_network_spider'
    allowed_domains = ['toscrape.com']
    #start_urls = ['http://toscrape.com/']

    # Using a dummy website to start scrapy request
    def start_requests(self):
        url = "http://quotes.toscrape.com"
        yield scrapy.Request(url=url, callback=self.parse_character_network)
    
    def get_total(self, text):
        #from text extract number
        totals = [int(s) for s in str(text).split() if s.isdigit()]
        return max(totals)
    
    def get_totals_dict(self, l):
        #from text extract number
        dict = {}
        for s in l:
            starting_bracket = [x for x, z in enumerate(s) if z == '(']
            closing_bracket = [x for x, z in enumerate(s) if z == ')']
            subset = s[starting_bracket[-1]:]
            temp_list = [int(x) for x in list(subset) if x.isdigit()]
            count = ''
            for i in temp_list:
                count = count + str(i)
            temp = re.sub(r'[0-9]+', '', s)
            mod_string = temp[:-3]
            dict.update({s[:starting_bracket[-1]].rstrip():count})
        return dict
    
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
    
    def parse_character_network(self,response):
        base_url = "https://archiveofourown.org"
        logger.info(f"Scraping started at {time.strftime('%H:%M:%S')}")
        
        # Use headless option to not open a new browser window
        options = webdriver.ChromeOptions()
        #options.add_argument("headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        desired_capabilities = options.to_capabilities()
        driver = webdriver.Chrome(ChromeDriverManager().install(), options = options, desired_capabilities=desired_capabilities)

        with open("pop_fandoms_stats.json", "r") as f:
            temp_list = json.load(f)

        #urls = ['/tags/Eagles%20(TV%202019)/works']
        fandoms = list(map(lambda x: x.get("fandom"), temp_list))
        
        count = 0
        exception_count = 0
        restarted = False
        for i, fandom in enumerate(fandoms):
            characters_temp = temp_list[i]["characters"]
            characters = []
            for character in characters_temp.keys():
                characters.append(character)
            
            for j, character in enumerate(characters):
            
                try:
                    #Open fandom page
                    driver.get(base_url + "/tags/" + character + "/works")
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

                    
                    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div/ol[2]/li[1]/dl/dd[@class='bookmarks']/a")))
                    time.sleep(2)
                    
                    

                    # Hand-off between Selenium and Scrapy happens here
                    sel = Selector(text=driver.page_source)

                    total_works = self.get_total(sel.xpath("//h2[@class = 'heading']/text()").getall())
                    characters_dict = self.get_totals_dict(sel.xpath("//dd[@id = 'include_character_tags']/ul/li/label/span/text()").getall())
                    ships_dict = self.get_totals_dict(sel.xpath("//dd[@id = 'include_relationship_tags']/ul/li/label/span/text()").getall())
                    
                    yield {
                        "fandom": fandoms[i],
                        "character": character,
                        "total_works": total_works,
                        "characters": characters_dict,
                        "relationships": ships_dict
                    }
                    count += 1
                except Exception as e:
                    logger.error(f"Exception {e} has occurred with Character: {character}")
                    exception_count += 1
                except exceptions as f:
                    logger.error(f"Selenium Exception {f} has occured with character: {character}")
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