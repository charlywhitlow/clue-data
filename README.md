# Clue Period Tracker - Data Export

This program takes period data exported from the Clue App, converts it into csv form, and produces a pdf report with some simple charts and predictions.

## Sample data

A [sample data file](data/SampleData.cluedata) is included, describing 9 complete cycles and 1 incomplete cycle.

You can also find 1 [sample output csv](output_csv/SampleData_processed_03-02-2022.csv), and 1 [sample pdf report](output_report/SampleData_processed_03-02-2022.pdf), created by running the program on the included sample data file.

## To run

The program expects 1 argument: the path to a json data file extracted from clue app:

    > python3 clue-import.py [Clue data file]
    > python3 clue-import.py data/SampleData.cluedata

Dependencies are saved in `environment.yaml`

### To run in a virtual environment:

    # create a virtual environment called env
    python3 -m venv env

    # activate virtual environment env
    source ./env/bin/activate

    # install dependencies in env
    pip3 install -r environment.yaml

    # run program
    python3 clue-import.py [cluedata file]
    python3 clue-import.py data/SampleData.cluedata

    # to update environment.yaml file from active environment
    pip3 freeze > environment.yaml

    # deactivate virtual environment
    deactivate
