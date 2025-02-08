import requests
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import csv

def search_marine_species(limit=100):
    """
    Search for marine species using GBIF API
    """
    base_url = "https://api.gbif.org/v1/species/search"
    params = {
        'habitat': 'marine',
        'limit': limit,
        'status': 'ACCEPTED',
        'rank': 'SPECIES'
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data['results']
    except requests.exceptions.RequestException as e:
        print(f"Error accessing GBIF API: {e}")
        return None

def get_season(month):
    """
    Convert month to season
    """
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

def get_seasonal_population(species_key, start_year=1980, end_year=2024):
    """
    Get seasonal occurrence counts for a specific species
    """
    base_url = "https://api.gbif.org/v1/occurrence/search"
    seasonal_counts = defaultdict(lambda: defaultdict(int))
    
    limit = 300
    offset = 0
    
    while True:
        params = {
            'speciesKey': species_key,
            'limit': limit,
            'offset': offset,
            'year': f'{start_year},{end_year}',
            'basisOfRecord': 'HUMAN_OBSERVATION'  # Only count actual observations
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data['results']:
                break
                
            for occurrence in data['results']:
                year = occurrence.get('year')
                event_date = occurrence.get('eventDate')
                
                if year and event_date:
                    try:
                        date = datetime.strptime(event_date.split('T')[0], '%Y-%m-%d')
                        season = get_season(date.month)
                        key = f"{year}-{season}"
                        seasonal_counts[year][season] += 1
                    except (ValueError, IndexError):
                        continue
            
            offset += limit
            if offset >= data['count']:
                break
                
        except requests.exceptions.RequestException as e:
            print(f"Error accessing GBIF API: {e}")
            break
    
    return dict(sorted(seasonal_counts.items()))

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

def main():
    # Search for marine species
    print("Searching for marine species...")
    species_results = search_marine_species(limit=10)  # Limiting to 10 species for example
    
    if species_results:
        for species in species_results:
            scientific_name = species.get('scientificName')
            species_key = species.get('key')
            
            print(f"\n{'='*50}")
            print(f"Species: {scientific_name}")
            print(f"{'='*50}")
            
            seasonal_data = get_seasonal_population(species_key)
            
            # Print seasonal data
            for year, seasons in seasonal_data.items():
                print(f"\nYear: {year}")
                print("Season | Count")
                print("-" * 20)
                for season in ['Winter', 'Spring', 'Summer', 'Fall']:
                    count = seasons.get(season, 0)
                    print(f"{season:8}| {count:5}")
            
            # Print total observations
            total = sum(sum(seasons.values()) for seasons in seasonal_data.values())
            print(f"\nTotal observations: {total}")

    # Example species to analyze
    species_list = [
        "Panthera leo",  # Lion
        "Gorilla gorilla",  # Gorilla
        "Panda ailuropoda melanoleuca",  # Giant Panda
        "Elephas maximus",  # Asian Elephant
        "Rhinoceros unicornis",  # Greater One-horned Rhinoceros
        "Panthera tigris",  # Tiger
        "Balaenoptera musculus",  # Blue Whale
        "Pongo abelii",  # Sumatran Orangutan
        "Geochelone elephantopus",  # Galápagos Giant Tortoise
        "Panthera onca"  # Jaguar
    ]

    # Get and plot data for each species
    with open('endangered_species_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
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

    print("\nData has been saved to 'endangered_species_data.csv'")

if __name__ == "__main__":
    main()