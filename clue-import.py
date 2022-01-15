import json
import datetime
import pandas as pd
import sys
from os.path import exists

"""
Program expects 1 argument: the path to the json data file, extracted from clue app, i.e.:
    > python3 clue-import.py data/ClueBackup-2022-01-11.cluedata

"""
def main(args):
    if len(args) != 2:
        print('Error: 1 argument expected')
        print('Usage:\n > python3 clue-import.py [data.json]')
        return
    else:
        file_name = args[1]
        if (exists(file_name)):
            # file_name = "data/ClueBackup-2022-01-11.json"
            cycles = extract_cycles(file_name)

        else:
            print(f'Error: File \'{file_name}\' not found')
            print('Usage:\n > python3 clue-import.py [data.json]')

# extract cycles from json file
def extract_cycles(file_name):
    with open(file_name, "r") as read_file:
        try:
            data = json.load(read_file)
        except json.decoder.JSONDecodeError:
            print('Error: data file not in correct format, expects json file')
            print('Usage:\n > python3 clue-import.py [data.json]')
            return

    entries, removed = filter_entries(data["data"]) # remove data we're not interested in
    entries = process_entries(entries) # assign numeric values to periods
    cycles = break_into_cycles(entries) # separate clue entries into cycles

    print(f'{len(cycles)} cycles extracted ({removed} entries removed)')
    return cycles

# extract "period" and "iud" entries not set to 'excluded' in the app
def filter_entries(entries):
    filtered = []
    removed = 0
    for entry in entries:
        if (not ("marks_excluded_cycle" in entry.keys() and entry["marks_excluded_cycle"] == True)) and ("period" in entry.keys() or "iud" in entry.keys()):
            filtered.append(entry)
        else:
            removed+=1
    return filtered, removed

# add numeric value for period
def process_entries(entries):
    period_key = {
        "spotting" : 1,
        "light" : 2,
        "medium" : 3,
        "heavy" : 4
    }
    for entry in entries:
        entry["day"] = pd.to_datetime(entry["day"])
        if "period" in entry.keys():
            entry["period_numeric"] = period_key[entry["period"]]
    return entries

# add clue entry to cycles array
def break_into_cycles(entries):
    cycles = []
    cycle = []
    for entry in entries:
        cycle, cycles = add_entry_to_cycle(entry, cycle, cycles)

    return cycles

# add clue entry to cycles array
def add_entry_to_cycle(entry, cycle, cycles):
    # if first entry in cycle, or entry is not true period (i.e. spotting/IUD), add without checking dates
    if len(cycle) == 0 or not is_period(entry):
        cycle.append(entry)
    else:
        # add entry to current cycle if dates adjacent
        last_entry = get_last_period_entry_in_cycle(cycle) # returns last period day in current cycle
        if (last_entry["day"] == entry["day"] - datetime.timedelta(days=1) or last_entry["day"] == entry["day"] - datetime.timedelta(days=2)):
            cycle.append(entry)
        else:
            # add to new cycle if there's a gap of more than 1 day
            cycles.append(cycle)
            cycle=[entry]

    return cycle, cycles

# return true if entry contains true period (i.e. excluding spotting / IUD entries)
def is_period(entry):
    return ("period" in entry.keys() and entry["period"] != "spotting")

# return last true period entry in given cycle (i.e. excluding spotting / IUD entries)
def get_last_period_entry_in_cycle(cycle):
    last_entry = cycle[len(cycle)-1]
    i = 1   
    while not is_period(last_entry):
        i+=1
        last_entry = cycle[len(cycle)-i]
    
    return last_entry


# run main with sys args
args = sys.argv
main(args)
