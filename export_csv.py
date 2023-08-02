import sys
import funtion
from datetime import datetime

if __name__ == "__main__":
    if len(sys.argv) > 1:
        outputfile = sys.argv[1]
        funtion.export_csv(outputfile)
    else:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        outputfile = timestamp + '.csv'
        funtion.export_csv(outputfile)
