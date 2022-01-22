import json
import datetime
import pandas as pd
import sys
from os.path import exists
from numpy.lib.function_base import average

"""
# Program expects 1 argument: the path to a json data file extracted from clue app:

    > python3 clue-import.py [Clue data file]

# transforms cluedata into data object:
    data = {
        num_cycles : [int],
        max_cycle_length : [int],
        average_cycle_length : [int],
        average_period_length : [int],
        cycles : [
            {
                start_date : [Timestamp],
                cycle_length : [int],
                period_length : [int],
                period : [
                    {
                        day : [Timestamp],
                        period : [str], 
                        period_numeric : [int]
                    }
                ]
            }
        ]
    }
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

    # print result
    print(f'{len(cycles)} cycles extracted ({removed} entries removed)')
    for cycle in cycles:
        print(f'{cycle["start_date"].strftime("%d/%m/%Y")} - period {cycle["period_length"]} days - cycle {cycle["cycle_length"]} days')

    # build data object
    data = {
        "num_cycles" : len(cycles),
        "max_cycle_length" : max([cycle["cycle_length"] for cycle in cycles]),
        "average_cycle_length" : average([cycle["cycle_length"] for cycle in cycles]),
        "average_period_length" : average([cycle["period_length"] for cycle in cycles]),
        "cycles" : cycles
    }
    print(f'Average cycle length: {data["average_cycle_length"]}')
    print(f'Average period length: {data["average_period_length"]}')

    return data

# extract "period" entries not set to 'excluded' in the app
def filter_entries(entries):
    filtered = []
    removed = 0
    for entry in entries:
        if (not ("marks_excluded_cycle" in entry.keys() and entry["marks_excluded_cycle"] == True)) and ("period" in entry.keys()):
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
    cycle = {
        "start_date" : None,
        "cycle_length" : None,
        "period_length" : None,
        "period" : []
    }
    for entry in entries:
        cycle, cycles = add_entry_to_cycle(entry, cycle, cycles)

    return cycles

# add clue entry to cycles array
def add_entry_to_cycle(entry, cycle, cycles):

    # first entry in first cycle, set start date and add without checking dates
    if len(cycle["period"]) == 0:
        cycle["period"].append(entry)
        cycle["start_date"] = entry["day"]
    
    # if spotting entry, add without checking dates
    elif not is_period(entry):
        cycle["period"].append(entry)
    else:
        # add entry to current cycle if 5 days or less since last period day in current cycle
        last_entry = get_last_period_entry_in_cycle(cycle["period"])
        if (entry["day"] <= last_entry["day"] + datetime.timedelta(days=5)):
            cycle["period"].append(entry)
        else:
            # close cycle
            cycle["cycle_length"] = (entry["day"] - cycle["start_date"]).days
            cycle["period_length"] = (get_last_period_entry_in_cycle(cycle["period"])["day"] - cycle["start_date"]).days +1
            cycles.append(cycle)

            # start new cycle
            cycle = {
                "start_date" : entry["day"],
                "period_length" : 0,
                "period" : [
                    entry
                ]
            }

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
