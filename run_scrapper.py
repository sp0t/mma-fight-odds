import sys
import funtion


if __name__ == "__main__":
    if len(sys.argv) > 1:
        limitdate = sys.argv[1]
        funtion.run_scrapping(limitdate)
    else:
        limitdate = '2013-01-01'
        funtion.run_scrapping(limitdate)