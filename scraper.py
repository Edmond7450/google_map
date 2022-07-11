import os.path
import time

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from sys import platform
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = 'https://www.google.de/maps'

REGIONS = ['Augsburg','Stuttgart','Baden-Württemberg','Bayern','Hessen','Rheinland-Pfalz']
QUERIES = ['Investment Bank', 'Merger & Aquisition', 'Investmentbank', 'Großbanken','Investmentbanking','Unternehmensinvestmentbank','corpoarate investment bank','Merger And Aquisition Bank','Finanzierungsunternehmen','unabhängige Corporate-Finance-Boutique-Investmentbank','Corporate-Finance-Boutique','M&A','Corporate Finance','Dept Advisory','Corporate Finance Dienstleister','Dept Advisory','Merger and Aquisitions']


def get_urls():
    urls = []

    ele_search = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="searchboxinput"]')))
    for region in REGIONS:
        for query in QUERIES:
            try:
                ele_search.click()
                ele_search.clear()
                ele_search.send_keys(f'{query} in {region}')
                ele_search.send_keys(Keys.ENTER)
                time.sleep(3)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@role="main"]/div/div//a')))
            except:
                continue

            while True:
                ele_container = driver.find_element(By.XPATH, '//*[@role="main"]/div/div')
                scrollHeight = int(ele_container.get_attribute('scrollHeight'))
                scrollPos = 0
                while (scrollPos < scrollHeight):
                    scrollPos = scrollHeight
                    driver.execute_script("arguments[0].scroll(0, arguments[1])", ele_container, scrollPos)
                    time.sleep(1)
                    scrollHeight = int(ele_container.get_attribute('scrollHeight'))

                results = ele_container.find_elements(By.XPATH, './/a')
                for result in results:
                    try:
                        if result.get_attribute('href'):
                            urls.append(result.get_attribute('href'))
                    except:
                        pass

                try:
                    driver.find_element(By.XPATH, '//button[contains(@class, "hV1iCc")][2]').click()
                    time.sleep(3)
                except:
                    break

    return urls


def get_page(urls):
    start = True
    for url in urls:
        try:
            driver.get(url)

            if start == True:
                mode = 'w'
                start = False
            else:
                mode = 'a+'

            company_name = driver.find_element(By.XPATH, '//h1').text.strip()
            if company_name.find(',') > 0:
                company_name = f'"{company_name}"'
            try:
                address = driver.find_element(By.XPATH, '//button[@data-item-id="address"]').text.strip()
                if address.find(',') > 0:
                    address = f'"{address}"'
            except:
                address = ''
            try:
                website = driver.find_element(By.XPATH, '//button[@data-item-id="authority"]').text.strip()
            except:
                website = ''
            try:
                phone_number = driver.find_element(By.XPATH, '//button[starts-with(@data-item-id, "phone:")]').text.strip()
                if phone_number.find(',') > 0:
                    phone_number = f'"{phone_number}"'
            except:
                phone_number = ''

            try:
                plus_code = driver.find_element(By.XPATH, '//button[@data-item-id="oloc"]').text.strip()
                if plus_code.find(',') > 0:
                    plus_code = f'"{plus_code}"'
            except:
                plus_code = ''

            with open('google_map.csv', mode, encoding='utf-8') as of:
                of.write(','.join([company_name, website, phone_number, address, plus_code]) + '\n')
        except Exception as e:
            print(str(e))


def main():
    driver.get(BASE_URL)

    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//c-wiz//form//button')))
        driver.find_element(By.XPATH, '//c-wiz//form//button').click()
    except:
        pass

    urls = get_urls()

    with open('google_map_urls.csv', 'w', encoding='utf-8') as of:
        of.writelines(url + '\n' for url in urls)

    # with open('google_map_urls.csv', 'r', encoding='utf-8') as of:
    #     urls = of.readlines()

    get_page(urls)


if __name__ == "__main__":
    if platform == "linux" or platform == "linux2":
        display = Display(visible=0, size=(1152, 1000))
        display.start()

    chrome_options = Options()
    chrome_options.add_argument("window-size=1152,1000")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--no-sandbox")
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
    chrome_options.add_argument(f'Upgrade-Insecure-Requests=1')
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument('--verbose')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')

    if platform == "win32" or platform == "win64":
        data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'selenium')
        chrome_options.add_argument(f"--user-data-dir={data_dir}")
        # chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    print("Start! : " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

    main()

    driver.close()
    driver.quit()

    if platform == "linux" or platform == "linux2":
        display.stop()

    print("End! : " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    exit(1)
