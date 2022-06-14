from ast import List
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
from tenacity import *
from logger import logger
from placa import Placa
import logging
from re import sub
from decimal import Decimal

driver = webdriver

@dataclass
class Buscador():
    processedCards = []
    running = False

    def setup(self):
        '''Configura as variaveis e opcoes do driver para execucao'''
        global driver
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

    def buscaPichau(self):
        '''Realiza busca no site da Pichau'''

        orderBox = By.ID, 'demo-customized-select'
        loading = By.CSS_SELECTOR, '#__next > main > div.MuiBackdrop-root.dark-mode'
        pathMenor = By.XPATH, '//*[@id="menu-"]/div[3]/ul/li[4]'

        # Index at bottom of page
        selPages = By.XPATH, '//*[@id="__next"]/main/div[2]/div/div[1]/nav/ul' # Pages index
        selNext = By.XPATH, 'li[9]/button' # Next page button

        def searchPage():
            '''Realiza varredura da pagina. Execucao para quando todos produtos forem lidos ou algum produto estiver Esgotado.\n\n
            Quando produto estiver esgotado, running = False'''

            logger.info('Varrendo pagina...')

            placas = [a for a in driver.find_elements(By.CSS_SELECTOR, "[data-cy*='list-product']")]

            for placa in placas:
                if self.running:
                    details = placa.find_element(By.CLASS_NAME, 'MuiCardContent-root')
                    if EC.all_of(EC.visibility_of_element_located((By.CLASS_NAME,'jss191')))(details):
                        self.running = False
                        break

                    link = placa.get_attribute('href') # Link
                    nome = details.find_element(By.TAG_NAME, 'h2').text # Nome
                    preco = details.find_element(By.CLASS_NAME, 'jss200').text.replace('.','').replace(',','.') # Preco
                    
                    preco = Decimal(sub(r'[^\d.]', '', preco))
                    placa = Placa(link=link,nome=nome,preco=preco)
                    self.processedCards.append(placa)

        def searchAndConfirmPopup():
            '''Verifica se há popups na parte do rodapé ou flutuando na tela, e clica'''
            if (EC.any_of(EC.visibility_of_element_located((By.XPATH, '//*[@id="rcc-confirm-button"]')))(driver)):
                driver.find_element(By.XPATH,'//*[@id="rcc-confirm-button"]').click()
            if (EC.any_of(EC.visibility_of_element_located((By.ID, 'onesignal-slidedown-cancel-button')))(driver)):
                driver.find_element(By.ID, 'onesignal-slidedown-cancel-button').click()

        def orderByPrice():
            '''Troca ordenacao para menor preco, so continua quando mudar e loading estiver acabado'''
            driver.find_element(*orderBox).click()
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located(pathMenor)).click()
            time.sleep(2)
            WebDriverWait(driver, 10).until(EC.all_of(EC.text_to_be_present_in_element(orderBox, 'Menor valor'),EC.invisibility_of_element_located(loading)))

        def moveToNextPage():
            '''Desce ate o fundo da pagina e clica no Botao de Proxima Pagina. Para execucao quando nao houver mais paginas ou running = False'''
            action = ActionChains(driver)
            pages = driver.find_element(*selPages)
            try:
                nextBtn = pages.find_element(*selNext)
            except NoSuchElementException:
                self.running = False
            if self.running:
                action.move_to_element(nextBtn).perform()
                time.sleep(2)
                nextBtn.click()
                time.sleep(4)

        driver.get('https://www.pichau.com.br/hardware/placa-de-video')
        orderByPrice()
        self.running = True
        while self.running: # Loop executa, ate variavel running mudar para False.
            searchAndConfirmPopup()
            searchPage()
            moveToNextPage()
        
        logger.info(f'[PICHAU] {len(a.processedCards)} placas carregadas.')

    def buscaTerabyte():
        ...

    def finishSearch(self):
        '''Fecha o driver e encerra a execucao'''
        driver.close()
        driver.quit()
        logger.info('Busca completa.')

a = Buscador()

a.setup()
a.buscaPichau()
a.finishSearch()