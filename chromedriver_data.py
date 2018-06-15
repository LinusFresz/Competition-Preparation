import sys, os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

chrome_options = Options()  
chrome_options.add_argument('--headless')  
chrome_options.add_argument('--window-size=%s' % '1920,1080')
chromedriver_path = find('chromedriver', '/Users')

driver = webdriver.Chrome(chromedriver_path, chrome_options=chrome_options)


