from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service


import uuid
import time
import json
import os
from sys import platform
import itertools
from datetime import datetime

from scraper.config import ZEESCHUIMER_ID, X_LOG_DIR
from scraper.autocorrect.x import search_autocorrect

class XScraper:
  def __init__(self, run_config:dict):
    """
    XScraper: The object for scraping the social media platform X.

    Input:
      run_config(dict): Config for full run of scraping. See directory "./scraper/run-configs" for examples.

    Returns:
      XScraper instance. To start the run call the `.run()` method.    
    """
    self.username = run_config["user"]["name"]
    self.mail = run_config["user"]["name"]
    self.password = run_config["user"]["password"]
    self.log_path = X_LOG_DIR + run_config["log"]["fileName"] + ".txt"

    self.search_queue = self._resolve_searches(run_config["searchTerms"], run_config["timeBins"], run_config["additionalQuery"])
    self.run_config = run_config
    
    # stuff for activating zeeschuimer
    options = Options()
    add_on_id_dynamic = str(uuid.uuid4())
    options.set_preference('extensions.webextensions.uuids',
                            json.dumps({ZEESCHUIMER_ID: add_on_id_dynamic}))

    self.zeeschuimer_url = f"moz-extension://{add_on_id_dynamic}/popup/interface.html"
    
    # set download dir
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", f"{os.getcwd()}\data\X")
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-ndjson,application/json")


    # instantiating firefox and navigating to zeeschuimer
    if platform == "linux" or platform == "linux2":
      self.driver = webdriver.Firefox(options=options,
                                      service=Service("./scraper/driver/geckodriver-v0.36.0-linux64.tar.gz"))
    else:
      self.driver = webdriver.Firefox(options=options)
    self.driver.install_addon("./scraper/extensions/zeeschuimer-v1.12.3.zip", temporary=True)
    self.driver.get(self.zeeschuimer_url)

    # toggle X
    x_toggle_input = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[for="zs-enabled-twitter.com"]')))
    x_toggle_input.click()
  
  def run(self, continued = False):
    """
    Run the scraping.
    """
    if not continued: 
      self.login()

    for search_term in self.search_queue:
        self.search(search_term)
        self.scroll(self.run_config["scrollsPerSearch"],
                    self.run_config["scrollsOffset"],
                    self.run_config["secBetweenScrolls"],
                    self.run_config["secAfterScrolls"])
        self.search_queue.pop(0)
    
    self.download_posts()
  
  def login(self):
    self.driver.get("https://x.com/i/flow/login")

    usermail = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]')))
    usermail.send_keys(self.mail)
    usermail.send_keys(Keys.ENTER)

    time.sleep(1)
    ActionChains(self.driver).send_keys(self.username + Keys.ENTER).perform()

    password = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="password"]')))
    password.send_keys(self.password)
    password.send_keys(Keys.ENTER)
    time.sleep(3)

    self._log(f"Finished login to account: {self.username}")

  @search_autocorrect
  def search(self, text):
    search = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Search"]')))
    
    # make sure the search field is empty then do request
    search.clear()
    search.send_keys(text + Keys.ENTER)
    self._log(f"Searched for {text}")

  def download_posts(self):
    self.driver.get(self.zeeschuimer_url)
    download_button = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[class="download-ndjson"][data-platform="twitter.com"]')))
    download_button.click()
  
  def scroll(self, times, offset = 300, sleep = 1, sleep_after = 0):
    for _ in range(times):
      time.sleep(sleep)
      ActionChains(self.driver).scroll_by_amount(0, offset).perform()
    time.sleep(sleep_after)

  def _resolve_keywords(self, keywords:list[str]):
    if type(keywords) == list and len(keywords) > 0:
      if type(keywords[0]) == list:
        # do cartesian product of the lists provided
        temp = []
        for first in keywords[0]:
          for second in keywords[1]:
            temp.append(" AND ".join([first, second]))
        return temp
      # if just list of search terms was given return it
      return keywords
        
    raise RuntimeError("No searchterms provided in run config")
  
  def _resolve_timebins(self, time_bins:list[str]) -> list[str]:
    result = []
    for i in range(1,len(time_bins)):
      result.append(f"since:{time_bins[i-1]} until:{time_bins[i]}")
    return result
  
  def _resolve_searches(self, keywords:list[str], time_bins:list[str], additional_query:str) -> list[str]:
    """
    Builds queries from keywords, times and additional parameters.
    """
    keys = self._resolve_keywords(keywords)
    times = self._resolve_timebins(time_bins)
    
    searches = [f"{' '.join(words)} {additional_query}" for words in list(itertools.product(keys, times))]
    return searches
  
  def _log(self, message):
    """
    Write log message to specified log file.
    """
    log_message = f"[{datetime.now().__str__()}]: {message}"
    with open(self.log_path, "a") as f:
      f.write(log_message + "\n")