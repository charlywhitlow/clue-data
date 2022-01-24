import csv

# write data object to csv
def write_to_csv(data, file_path):

    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)

        headers = ["Cycle Start Date","Cycle Length","Period Length"]
        for i in range (1, data["max_cycle_length"]+1):
            headers.append(f'Day {i}')
        writer.writerow(headers)

        for cycle in data["cycles"]:
            row = [0 for day in range(cycle["cycle_length"]+3)]
            row[0] = cycle["start_date"].strftime("%d/%m/%Y")
            row[1] = cycle["cycle_length"]
            row[2] = cycle["period_length"]
            for day in cycle["period"]:
                num = (day["day"]-cycle["start_date"]).days
                row[num+3] = day["period_numeric"]
            writer.writerow(row)
    
    print(f'CSV created: {file_path}')