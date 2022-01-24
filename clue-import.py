from os.path import exists
import sys
from pathlib import Path
from datetime import date
from lib import process_cluedata
from lib import generate_csv

"""
# Program expects 1 argument: the path to a json data file extracted from clue app:

    > python3 clue-import.py [Clue data file]
    > python3 clue-import.py data/SampleData.cluedata

"""
def main(args):
    if len(args) != 2:
        print('Error: 1 argument expected')
        print('Usage:\n > python3 clue-import.py [data.json]')
        return
    else:
        file_path = args[1]
        if (exists(file_path)):
            data = process_cluedata.extract_cycles(file_path)

            # generate csv
            csv_file_path = f'output_csv/{Path(file_path).stem}_processed_{date.today().strftime("%d-%m-%Y")}.csv'
            generate_csv.write_to_csv(data, csv_file_path)

            # generate pdf report
            # TODO

        else:
            print(f'Error: File \'{file_path}\' not found')
            print('Usage:\n > python3 clue-import.py [data.json]')


# run main with sys args
args = sys.argv
main(args)
