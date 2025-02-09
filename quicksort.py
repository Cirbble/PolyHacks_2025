import csv

# Read the CSV file
with open('marine_species_data.csv', 'r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    header = next(reader)  # Save the header
    data = list(reader)    # Read all rows

# Sort the data using the MonthlyIndex (column index 2)
data.sort(key=lambda x: int(x[2]))

# Write the sorted data back to the CSV
with open('message.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(header)  # Write the header first
    writer.writerows(data)   # Write the sorted data

print("Data has been sorted by MonthlyIndex")

