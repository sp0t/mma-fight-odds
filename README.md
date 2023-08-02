# MMA Events | Fight Odds Scrapper
Scrapper which is scrapping event details and odds from [MMA recent events](https://fightodds.io/recent-mma-events).

## Installation
### 1. Installing individual package

install selenium.
```bash
pip install selenium
```
install webdriver-manager.
```bash
pip install webdriver-manager
```
install beautifulsoup4.
```bash
pip install beautifulsoup4
```
install Flask-BasicAuth.
```bash
pip install Flask-BasicAuth
```

### 2. Using _requirements.txt_ file.
```bash
pip install -r requirements.txt
```

## Database
Use SQLite database.
DB **mma_odds.db**

## Run Script
Use **Python Command line** to run script.
### 1. Run Scrapper
Use **args** as _Limitdate_ to scrappe. If not set args, Default value(_2013-01-01_) will be set for _Limitdate_.
```bash
python3 run_scrapper.py 2022-01-01
```
### 2. Export data to csv file.
Use **args** as _filename_ to save as file. If not set args, Default value(_current time:2023-07-30_8_12_36.csv_) will be set for _filename_.
```bash
python3 export_csv.py mydata.csv
```