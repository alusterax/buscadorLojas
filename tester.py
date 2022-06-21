import time
from dataclasses import dataclass
from os import getcwd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from logger import logger
from placa import Placa
import logging
from re import sub
from decimal import Decimal

driver = webdriver

prefs = {'download.default_directory' : f'{getcwd()}/Downloads'}
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option('prefs', prefs)
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
s=Service(ChromeDriverManager(log_level=logging.CRITICAL,path=getcwd()).install())
driver = webdriver.Chrome(service=s,options=chrome_options, service_log_path='NUL')


# driver.get('https://www.pichau.com.br/hardware/placa-de-video')

# driver.get('https://www.kabum.com.br/hardware/placa-de-video-vga/placa-de-video-nvidia')
driver.get('https://www.kabum.com.br/hardware/placa-de-video-vga/placa-de-video-amd')



# EC.text_to_be_present_in_element((By.TAG_NAME, 'p'), text_='Esgotado')(driver)


# placa = driver.find_element(By.XPATH, '')

# EC.text_to_be_present_in_element((By.XPATH, '//*[@id="__next"]/main/div[2]/div/div[1]/div[2]/div[9]/a/div/div[2]/p'), text_='Esgotado')(driver)



# for placa in placas:
#     details = placa.find_element(By.CLASS_NAME, 'MuiCardContent-root')

#     link = placa.get_attribute('href') # Link
#     nome = details.find_element(By.TAG_NAME, 'h2').text

#     preco = details.find_element(By.XPATH, 'div/div/div/div[2]').text.replace('.','').replace(',','.') # Preco
#     print(preco)


# placa = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div[2]/div/div[1]/div[2]/div[1]/a/div/div[2]')

# placa = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div[2]/div/div[1]/div[2]/div[3]/a/div/div[2]')


def filterProducts():
    # driver.get('https://www.kabum.com.br/hardware/placa-de-video-vga')
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "option[value='price']")))
    driver.find_element(By.CSS_SELECTOR, "option[value='price']").click()
    time.sleep(0.5)
    WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '#kloader1')))
    driver.find_element(By.CSS_SELECTOR, "input[value='kabum_product']").click()
    time.sleep(0.5)
    WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '#kloader1')))
    # card = driver.find_element(By.CSS_SELECTOR, 'div.productCard')
    cards = driver.find_elements(By.CSS_SELECTOR, 'div.productCard')
    for card in cards:
        link = card.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
        nome = card.find_element(By.CSS_SELECTOR, 'span.nameCard').text
        preco = card.find_element(By.CSS_SELECTOR, 'span.priceCard').text
        print(f'{nome}\n{preco}\n{link}')