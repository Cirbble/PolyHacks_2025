import csv

# Read the CSV file
with open('marine_species_data.csv', 'r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    header = next(reader)  # Save the header
    data = list(reader)    # Read all rows

# Filter out rows where monthlySightings is "0" (column index 1)
filtered_data = [row for row in data if row[1] != "0"]

# Sort the filtered data using the MonthlyIndex (column index 2)
filtered_data.sort(key=lambda x: int(x[2]))

# Write the filtered and sorted data back to the CSV
with open('marine_species_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(header)  # Write the header first
    writer.writerows(filtered_data)   # Write the filtered and sorted data

print(f"Data has been filtered (removed {len(data) - len(filtered_data)} entries with 0 sightings) and sorted by MonthlyIndex")