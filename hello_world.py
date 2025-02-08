import requests
from datetime import datetime
import matplotlib.pyplot as plt
import csv

# Define the base URL for the GBIF API
base_url = "https://api.gbif.org/v1/"

def get_species_population_trend(scientific_name, start_year=2000):
    # First, get the taxonKey for the species
    search_params = {
        'q': scientific_name,
        'limit': 1
    }
    species_response = requests.get(base_url + "species/search", params=search_params)
    
    if species_response.status_code != 200 or not species_response.json()['results']:
        print(f"Species '{scientific_name}' not found")
        return None
    
    taxon_key = species_response.json()['results'][0]['key']
    
    # Now get occurrence counts by year
    current_year = datetime.now().year
    occurrence_params = {
        'taxonKey': taxon_key,
        'facet': 'year',
        'facetLimit': current_year - start_year + 1,
        'limit': 0  # We only want the facet counts, not actual occurrences
    }
    
    response = requests.get(base_url + "occurrence/search", params=occurrence_params)
    
    if response.status_code != 200:
        print(f"Failed to retrieve data: {response.status_code}")
        return None
    
    # Extract year counts from facets
    year_counts = {}
    facets = response.json()['facets']
    if facets:
        for facet in facets[0]['counts']:
            year = int(facet['name'])
            if year >= start_year:
                year_counts[year] = facet['count']
    
    return year_counts

def plot_population_trend(species_data, species_name):
    years = list(species_data.keys())
    counts = list(species_data.values())
    
    plt.figure(figsize=(12, 6))
    plt.plot(years, counts, marker='o')
    plt.title(f'Population Trend for {species_name}')
    plt.xlabel('Year')
    plt.ylabel('Number of Observations')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Example species to analyze
species_list = [
    "Panthera leo",  # Lion
    "Gorilla gorilla",  # Gorilla
    "Panda ailuropoda melanoleuca"  # Giant Panda
]

# Get and plot data for each species
with open('species_population_data.csv', 'w', newline='') as csvfile:
    # Create CSV writer
    csv_writer = csv.writer(csvfile)
    # Write header
    csv_writer.writerow(['Species Name', 'Year', 'Observation Count'])
    
    for species_name in species_list:
        print(f"\nAnalyzing population trend for {species_name}...")
        population_data = get_species_population_trend(species_name)
        
        if population_data:
            print(f"Year-wise observations for {species_name}:")
            # Sort the data by year and write to CSV
            for year, count in sorted(population_data.items()):
                print(f"Year {year}: {count} observations")
                csv_writer.writerow([species_name, year, count])
            
            plot_population_trend(population_data, species_name)
        else:
            print("nothing found")
            csv_writer.writerow([species_name, 'No data', 0])

print("\nData has been saved to 'species_population_data.csv'")