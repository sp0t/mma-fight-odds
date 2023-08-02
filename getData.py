from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options 
from datetime import date, timedelta, datetime
import sqlite3
import csv
import time
from apscheduler.schedulers.background import BackgroundScheduler

database = 'mma_odds.db'
limitdate = '2023-06-30'
outputfile = 'data.csv'

def connect_to_database(db_name):
    try:
        connection = sqlite3.connect(db_name)
        print(f"Connected to the database: {db_name}")
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to the database: {e}")
        return None
    
def create_table(connection):
    try:
        # Create a cursor object to execute SQL commands
        cursor = connection.cursor()

        # Define the SQL command to create the "odd" table
        event_query = """
        CREATE TABLE IF NOT EXISTS event (
            eventname TEXT,
            eventdate TEXT,
            venue TEXT,
            city TEXT,
            state INTEGER,
            link TEXT,
            num INTEGER PRIMARY KEY
        )
        """
        fight_query = """
        CREATE TABLE IF NOT EXISTS fighter (
            fighter1 TEXT,
            betonline_f1 TEXT,
            pinnacle_f1 TEXT,
            fighter2 TEXT,
            betonline_f2 TEXT,
            pinnacle_f2 TEXT,
            link TEXT,
            num INTEGER PRIMARY KEY
        )
        """
        # Execute the SQL command
        cursor.execute(event_query)
        cursor.execute(fight_query)
        connection.commit()
        print("Table OK.")
    except sqlite3.Error as e:
        print(f"Error table: {e}")

def insert_event(connection, event_data):
    try:
        cursor = connection.cursor()

        # Define the SQL command to insert or update data into the "event" table
        insert_or_replace_query = """
        INSERT OR IGNORE INTO event (eventname, eventdate, venue, city, state, link)
        VALUES (:eventname, :eventdate, :venue, :city, :state, :link)
        """

        # Execute the SQL command with the provided event_data dictionary
        cursor.execute(insert_or_replace_query, event_data)
        connection.commit()
        print("eventdata insert successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting event data: {e}")

def update_event(connection, link):
    try:
        cursor = connection.cursor()

        update_data = {
            "state": 1,
            "link": link
            }

        # Define the SQL command to insert or update data into the "event" table
        update_query = """
            UPDATE event
            SET state=:state
            WHERE link=:link
        """

        # Execute the SQL command with the provided event_data dictionary
        cursor.execute(update_query, update_data)
        connection.commit()
        print("eventdata updated successfully.")
    except sqlite3.Error as e:
        print(f"Error updating event data: {e}")

def insert_fighter(connection, fighter_data):
    try:
        cursor = connection.cursor()

        # Define the SQL command to insert or update data into the "event" table
        insert_or_replace_query = """
        INSERT OR IGNORE INTO fighter (fighter1, betonline_f1, pinnacle_f1, fighter2, betonline_f2, pinnacle_f2, link)
        VALUES (:fighter1, :betonline_f1, :pinnacle_f1, :fighter2, :betonline_f2, :pinnacle_f2, :link)
        """
        # Execute the SQL command with the provided event_data dictionary
        cursor.execute(insert_or_replace_query, fighter_data)
        connection.commit()
        print("fighterdata insert successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting fighter data: {e}")

def extract_data(connection):
    try:
        cursor = connection.cursor()

        # Define the SQL command to extract data from all three tables using INNER JOIN
        extract_data_query = """
        SELECT event.eventname, event.eventdate, event.venue, event.city,
               fighter.fighter1 AS fighter1, fighter.betonline_f1 AS betonline, fighter.pinnacle_f1 AS pinnacle,
               fighter.fighter2 AS fighter2, fighter.betonline_f2 AS betonline, fighter.pinnacle_f2 AS pinnacle, event.link
        FROM event
        INNER JOIN fighter ON event.link = fighter.link ORDER BY event.num DESC, fighter.num ASC
        """

        # Execute the SQL command with the provided link as a parameter
        cursor.execute(extract_data_query)
        result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print(f"Error extracting data: {e}")
        return None
    
def extract_event(connection, state):
    try:
        cursor = connection.cursor()

        # Define the SQL command to extract data from all three tables using INNER JOIN
        if state == 0:
            extract_data_query = """
            SELECT eventname, eventdate, link FROM event WHERE state = '0' ORDER BY num ASC
            """
        elif state == 1:
            extract_data_query = """
            SELECT eventname, eventdate FROM event ORDER BY num DESC
            """

        # Execute the SQL command with the provided link as a parameter
        cursor.execute(extract_data_query)
        result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        print(f"Error extracting data: {e}")
        return None
    
def save_to_csv(data, csv_filename):
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Write header row
            header = ["Event Name", "Event Date", "Venue", "City", "Fighter 1", "BetOnline", "Pinnacle", "Fighter 2", "BetOnline", "Pinnacle", "Link"]
            csv_writer.writerow(header)

            # Write data rows
            for row in data:
                csv_writer.writerow(row)
        print(f"Data saved to '{csv_filename}' successfully.")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

def scrapping_event(limitdate):

    limit = datetime.fromisoformat(limitdate)
    old_headname = ''
    old_date = ''

    db_connection = connect_to_database(database)
    old_data = extract_event(db_connection, 1)

    if len(old_data) != 0:
        old_headname = old_data[0][0]
        old_date = old_data[0][1]

    #run webdriver
    options = Options()
    options.use_chromium = True
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver_path = ChromeDriverManager().install()
    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    # driver = webdriver.Chrome(options=options)

    driver.get("https://fightodds.io/recent-mma-events")

    # Wait for the sports list to load
    time.sleep(3)
    event_datas = []

    try:
        target_date = True
        while target_date :
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            game_elements = soup.findAll('div', attrs={"class":"MuiGrid-root MuiGrid-item MuiGrid-grid-xs-9"})
            for game_element in game_elements:
                head_element = game_element.find('a', attrs={"class":"MuiTypography-root MuiLink-root MuiLink-underlineNone MuiTypography-colorPrimary"})
                body_element = game_element.find_all('div', recursive=False)
                date_element = body_element[1].findAll('div')[0]
                venue_element = body_element[1].findAll('div')[1]
                city_element = body_element[1].findAll('div')[2]
                odds_url ='https://fightodds.io' + head_element.get('href') + '/odds'
                current = datetime.strptime(date_element.text, '%B %d, %Y')

                if head_element.text == old_headname and date_element.text == old_date:
                    target_date = False
                    break

                if current < limit:
                    target_date = False
                    break

                event_data = {
                    "eventname": head_element.text,
                    "eventdate": date_element.text,
                    "venue": venue_element.text,
                    "city": city_element.text,
                    "state": 0,
                    "link": odds_url
                }

                if event_data not in event_datas:
                    event_datas.append(event_data)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.implicitly_wait(2)
    except:
        print("Element not found on the page.")

    driver.quit()

    event_datas.reverse()

    for event_data in event_datas:
        insert_event(db_connection, event_data)

    db_connection.close()

def scrapping_odds():
    db_connection = connect_to_database(database)
    old_data = extract_event(db_connection, 0)
    for event_data in old_data:
        betonline = ''
        pinnacle = ''

        options = Options()
        options.use_chromium = True
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver_path = ChromeDriverManager().install()
        odd_driver = webdriver.Chrome(service=Service(driver_path), options=options)
        # odd_driver = webdriver.Chrome(options=options)
        odd_driver.get(event_data[2])
        odd_driver.maximize_window()
        time.sleep(5)
        
        table_source = odd_driver.page_source
        table_soup = BeautifulSoup(table_source, "html.parser")
        try:
            table_element = table_soup.find('table')
            tbody_element = table_element.find(attrs={"class": "MuiTableBody-root"})
            fighters_element = tbody_element.find_all('tr')
            row = 0
            fighter_data = {}
            for fighter_element in fighters_element:
                name_element = fighter_element.find('a', attrs={"class":"MuiTypography-root MuiLink-root MuiLink-underlineHover MuiTypography-colorPrimary"})
                td_elements = fighter_element.find_all('td')
                try:
                    betonline_element = td_elements[1].find('button').find('span').find('div').find('div').find('span')
                    betonline = betonline_element.text
                except:
                    betonline = ''
                try:
                    pinnacle_element = td_elements[3].find('button').find('span').find('div').find('div').find('span')
                    pinnacle = pinnacle_element.text
                except:
                    pinnacle = ''
            
                if row % 2 == 0:
                    fighter_data['fighter1'] = name_element.text
                    fighter_data['betonline_f1'] = betonline
                    fighter_data['pinnacle_f1'] = pinnacle
                
                if row % 2 == 1:
                    fighter_data['fighter2'] = name_element.text
                    fighter_data['betonline_f2'] = betonline
                    fighter_data['pinnacle_f2'] = pinnacle
                    fighter_data['link'] = event_data[2]
                    insert_fighter(db_connection, fighter_data)
                    fighter_data = {}
                row = row + 1
        except:
            print('No ODDs')
        update_event(db_connection, event_data[2])
        odd_driver.quit()

    new_data = extract_data(db_connection)
    save_to_csv(new_data, outputfile)
    db_connection.close()

def run_scrapping():
    # Create the BackgroundScheduler instance
    scheduler = BackgroundScheduler()

    # Schedule the functions to run at a specific interval (600 seconds = 10 minutes)
    scheduler.add_job(func=scrapping_event, trigger="cron", day="*", args=[limitdate])
    scheduler.add_job(func=scrapping_odds, trigger="interval", seconds=3600)

    # Start the scheduler
    scheduler.start()

    try:
        # Keep the main function alive to allow the scheduler to run in the background
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # Shutdown the scheduler gracefully when a termination signal is received
        scheduler.shutdown()

if __name__ == "__main__":
    db_connection = connect_to_database(database)
    create_table(db_connection)
    db_connection.close()
    run_scrapping()
