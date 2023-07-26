
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

options = Options()
options.use_chromium = True
options.add_argument("--disable-extensions")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-ssl-errors")
driver = webdriver.Chrome(options=options)
driver.get('https://www.ladbrokes.com.au/sports/live')
driver.maximize_window()

# Wait for the sports list to load
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.XPATH, '//span[@data-testid="live-event-category-name"]')))

# Define the total number of seconds to run the scraping (24 hours)
total_seconds_to_run = 60

# Define the interval in seconds (20 seconds)
interval_seconds = 20

# Start time
start_time = time.time()

# Open the CSV file for writing
with open('scraped_data.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['Timestamp', 'Sport Name', 'Team Name 1', 'Team Name 2', 'Odds 1', 'Odds Draw', 'Odds 2', 'Team1 Score', 'Team2 Score'])

    while time.time() - start_time < total_seconds_to_run:
        # Get the timestamp for scraping
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Extract data
        sport_names = [sport.text for sport in driver.find_elements(By.XPATH, '//span[@data-testid="live-event-category-name"]')]
        team_names = [team.text for team in driver.find_elements(By.CLASS_NAME, 'displayTitle')]
        odds = [odd.text for odd in driver.find_elements(By.XPATH, '//span[@data-testid="price-button-odds"]')]
        scores = [score.text for score in driver.find_elements(By.CLASS_NAME, 'score')]

        print(sport_names, team_names, odds, scores)

        # Combine the data into a list of tuples
        data = list(zip(sport_names, team_names[::2], team_names[1::2], odds[::3], odds[1::3], odds[2::3], scores[::2], scores[1::2]))

        # Write data to CSV file
        for row in data:
            csv_writer.writerow([timestamp] + list(row))

        # Wait for the next interval (20 seconds)
        time.sleep(interval_seconds)

# Close the driver and quit the browser
driver.quit()

