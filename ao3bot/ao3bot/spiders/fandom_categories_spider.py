import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from logzero import logfile, logger

class FandomsCategoriesSpiderSpider(scrapy.Spider):
    # Initializing log file
    logfile("ao3bot_spider.log", maxBytes=1e6, backupCount=3)
    name = 'fandom_categories_spider'
    allowed_domains = ['toscrape.com']
    #start_urls = ['http://toscrape.com/']

    # Using a dummy website to start scrapy request
    def start_requests(self):
        url = "http://quotes.toscrape.com"
        yield scrapy.Request(url=url, callback=self.parse_fandom_categories)

    def parse_fandom_categories(self, response):
        # driver = webdriver.Chrome()  # To open a new browser window and navigate it

        # Use headless option to not open a new browser window
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        desired_capabilities = options.to_capabilities()
        driver = webdriver.Chrome(ChromeDriverManager().install(), options = options,desired_capabilities=desired_capabilities)

        # Getting list of Fandoms
        driver.get("https://archiveofourown.org/media")

        # Implicit wait
        driver.implicitly_wait(10)

        # Explicit wait
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "heading")))

        # Extracting fandom category names
        fandom_categories = driver.find_elements_by_xpath("//h3/a")
        fandom_categories_count = 0
        # Using Scrapy's yield to store output instead of explicitly writing to a JSON file
        for fandom_cat in fandom_categories:
            yield {
                "fandom_cat": fandom_cat.text,
                "fandom_cat_link": fandom_cat.get_attribute("href")
            }
            fandom_categories_count += 1

        driver.quit()
        logger.info(f"Total number of Fandom Categories in ao3: {fandom_categories_count}")