import time
from dataclasses import dataclass
from os import getcwd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
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
            
            def verificaPromocao(card):
                if EC.all_of(EC.presence_of_element_located((By.TAG_NAME, 's')))(card):
                    return True
                return False

            def verificaEsgotado(card):
                if EC.all_of(EC.text_to_be_present_in_element((By.TAG_NAME, 'p'), text_='Esgotado'))(card):
                    return True
                return False

            logger.info('Varrendo pagina...')

            placas = driver.find_elements(By.CSS_SELECTOR, "[data-cy*='list-product']")

            for placa in placas:
                if self.running:
                    details = placa.find_element(By.CLASS_NAME, 'MuiCardContent-root')
                    if verificaEsgotado(details):
                        self.running = False
                        break
                    link = placa.get_attribute('href') # Link
                    nome = details.find_element(By.TAG_NAME, 'h2').text # Nome
                    if verificaPromocao(details):
                        preco = details.find_element(By.XPATH, 'div/div/div/div[2]').text.replace('.','').replace(',','.') # Preco
                    else:
                        preco = details.find_element(By.XPATH, 'div/div/div/div').text.replace('.','').replace(',','.') # Preco
                    preco = Decimal(sub(r'[^\d.]', '', preco))
                    placa = Placa(link=link,nome=nome,preco=preco,site="Pichau")
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

    def buscaTerabyte(self):
        '''Realiza busca no site da Terabyte'''

    def buscaKabum(self):
        '''Realiza busca no site da Kabum'''
        def filterProducts():
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "option[value='price']")))
            driver.find_element(By.CSS_SELECTOR, "option[value='price']").click()
            time.sleep(0.5)
            WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '#kloader1')))
            if (EC.all_of(EC.visibility_of_element_located((By.CSS_SELECTOR, "#onetrust-accept-btn-handler")))):
                driver.find_element(By.CSS_SELECTOR, "#onetrust-accept-btn-handler").click()
                time.sleep(3)
            try:
                driver.find_element(By.CSS_SELECTOR, "input[value='kabum_product']").click()
            except ElementClickInterceptedException:
                driver.find_element(By.CSS_SELECTOR, "#onetrust-accept-btn-handler").click()
                time.sleep(3)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='kabum_product']").click()))
            time.sleep(0.5)
            WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '#kloader1')))

        def searchPage():
            WebDriverWait(driver, 10).until(EC.all_of(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.productCard')),
                EC.invisibility_of_element_located((By.CSS_SELECTOR, '#kloader1'))
            ))
            cards = driver.find_elements(By.CSS_SELECTOR, 'div.productCard')
            for card in cards:
                if self.running:
                    if (EC.any_of(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.unavailableFooterCard')))(card)):
                        self.running = False
                        break
                    link = card.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    nome = card.find_element(By.CSS_SELECTOR, 'span.nameCard').text
                    preco = card.find_element(By.CSS_SELECTOR, 'span.priceCard').text.replace('.','').replace(',','.') # Preco
                    
                    preco = Decimal(sub(r'[^\d.]', '', preco))
                    placa = Placa(link=link,nome=nome,preco=preco,site="Kabum")
                    self.processedCards.append(placa)

        def moveToNextPage():
            '''Desce ate o fundo da pagina e clica no Botao de Proxima Pagina. Para execucao quando nao houver mais paginas ou running = False'''
            action = ActionChains(driver)
            try:
                nextBtn = driver.find_element(By.CSS_SELECTOR, 'a.nextLink')
            except NoSuchElementException:
                self.running = False
            if self.running:
                action.move_to_element(nextBtn).perform()
                time.sleep(1)
                nextBtn.click()
                time.sleep(3)

        driver.get('https://www.kabum.com.br/hardware/placa-de-video-vga')
        filterProducts()
        self.running = True
        while self.running: # Loop executa, ate variavel running mudar para False.
            searchPage()
            moveToNextPage()

    def finishSearch(self):
        '''Fecha o driver e encerra a execucao'''
        driver.close()
        driver.quit()
        logger.info('Busca completa.')

a = Buscador()

a.setup()
a.buscaPichau()
a.buscaKabum()

# placasTeste = [placa for placa in a.processedCards if placa.site == "Kabum" and placa.preco > 2000]
# a.finishSearch()