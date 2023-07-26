from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup 
from datetime import date, timedelta, datetime

options = Options()
options.use_chromium = True
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-extensions")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-ssl-errors")
driver = webdriver.Chrome(options=options)
driver.get("https://fightodds.io/recent-mma-events")
driver.maximize_window()

print(date.today())
# Wait for the sports list to load
wait = WebDriverWait(driver, 30)
get_url = driver.current_url
wait.until(EC.url_to_be("https://fightodds.io/recent-mma-events"))

try:
    target_date = True
    while target_date:
        page_source = driver.page_source
        soup = BeautifulSoup(page_source)
        game_elements = soup.findAll('div', attrs={"class":"MuiGrid-root MuiGrid-item MuiGrid-grid-xs-9"})
        count = 0
        for game_element in game_elements:
            head_element = game_element.find('a', attrs={"class":"MuiTypography-root MuiLink-root MuiLink-underlineNone MuiTypography-colorPrimary"})
            body_element = game_element.find_all('div', recursive=False)
            date_element = body_element[1].findAll('div')[0]
            venue_element = body_element[1].findAll('div')[1]
            city_element = body_element[1].findAll('div')[2]
            odds_url =head_element.get('href') + '/odds'
            # if head_element.text == 'Invicta FC 45: Zappitella vs. Delboni 2' and date_element.text == 'January 12, 2022':
            #     target_date = False
            if head_element.text == 'UFC Fight Night 224: Aspinall vs. Tybura' and date_element.text == 'July 22, 2023':
                target_date = False
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.implicitly_wait(2)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source)
    game_elements = soup.findAll('div', attrs={"class":"MuiGrid-root MuiGrid-item MuiGrid-grid-xs-9"})
    count = 0
    for game_element in game_elements:
        head_element = game_element.find('a', attrs={"class":"MuiTypography-root MuiLink-root MuiLink-underlineNone MuiTypography-colorPrimary"})
        body_element = game_element.find_all('div', recursive=False)
        date_element = body_element[1].findAll('div')[0]
        venue_element = body_element[1].findAll('div')[1]
        city_element = body_element[1].findAll('div')[2]
        odds_url ='https://fightodds.io' + head_element.get('href') + '/odds'
        odd_driver = webdriver.Chrome(options=options)
        odd_driver.get(odds_url)
        odd_driver.maximize_window()
        wait = WebDriverWait(odd_driver, 30)
        wait.until(EC.url_to_be(odds_url))
        table_source = odd_driver.page_source
        table_soup = BeautifulSoup(table_source)
        tbody_element = table_soup.find('tbody')
        fighters_element = tbody_element.find_all('tr')
        row = 0
        for fighter_element in fighters_element:
            name_element = fighter_element.find('a', attrs={"class":"MuiTypography-root MuiLink-root MuiLink-underlineHover MuiTypography-colorPrimary"})
            odds_elements = fighter_element.find_all('span', attrs={"class":"MuiButton-label"})
            # betonline_element = odds_elements[0].find('div').find('div').find('span')
            # pinnacle_element = odds_elements[3].find('div').find('div').find('span')
            for odds_element in odds_elements:
                print(odds_element.find('div').find('div').find('span').text)
        odd_driver.quit()
        
except:
    print("Element not found on the page.")
driver.quit()
