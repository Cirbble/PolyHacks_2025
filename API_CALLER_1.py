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

def get_monthly_population(species_key, start_year=1980, end_year=2024):
    """
    Get monthly occurrence counts for a specific species
    """
    base_url = "https://api.gbif.org/v1/occurrence/search"
    monthly_counts = defaultdict(lambda: defaultdict(int))
    
    limit = 300
    offset = 0
    
    while True:
        params = {
            'speciesKey': species_key,
            'limit': limit,
            'offset': offset,
            'year': f'{start_year},{end_year}',
            'basisOfRecord': 'HUMAN_OBSERVATION'
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
                        monthly_counts[year][date.month] += 1
                    except (ValueError, IndexError):
                        continue
            
            offset += limit
            if offset >= data['count']:
                break
                
        except requests.exceptions.RequestException as e:
            print(f"Error accessing GBIF API: {e}")
            break
    
    return dict(sorted(monthly_counts.items()))

def get_species_population_trend(scientific_name, start_year=1980):
    """
    Get population trend starting from 1980
    """
    # Define base URL
    base_url = "https://api.gbif.org/v1/"
    
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

def calculate_monthly_index(year, month):
    """
    Calculate monthly index starting from 0 in January 1980
    """
    base_year = 1980
    months_since_1980 = ((year - base_year) * 12) + (month - 1)
    return months_since_1980

def save_marine_data_to_csv(species_data, filename='marine_species_data.csv'):
    """
    Save marine species data with monthly calculations
    """
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['speciesName', 'monthlySightings', 'monthlyIndex'])
        
        for species_name, yearly_data in species_data.items():
            for year in sorted(yearly_data.keys()):
                for month in range(1, 13):
                    sightings = yearly_data[year].get(month, 0)
                    monthly_index = calculate_monthly_index(year, month)
                    
                    writer.writerow([
                        species_name,
                        sightings,
                        monthly_index
                    ])

def save_endangered_data_to_csv(species_data, species_name, filename='combined_species_data.csv', mode='a'):
    """
    Save endangered species data to CSV
    """
    with open(filename, mode, newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if mode == 'w':  # Only write header if creating new file
            writer.writerow(['Species Name', 'Year', 'Season', 'Observation Count', 'Data Type'])
        
        if species_data:
            for year, count in sorted(species_data.items()):
                writer.writerow([species_name, year, 'All', count, 'Endangered'])
        else:
            writer.writerow([species_name, 'No data', 'All', 0, 'Endangered'])

def clean_species_name(name):
    """
    Clean species name by removing:
    1. Year of description
    2. Authority (person who described it)
    3. Anything in parentheses
    """
    # First remove anything in parentheses
    name = name.split('(')[0]
    
    # Remove the year and authority
    parts = name.split(',')
    clean_name = parts[0].strip()
    
    return clean_name

def main():
    # Create/overwrite the data file
    with open('marine_species_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['speciesName', 'monthlySightings', 'monthlyIndex'])

    print("Searching for marine species...")
    species_results = search_marine_species(limit=10)
    
    if species_results:
        marine_species_data = {}
        for species in species_results:
            scientific_name = species.get('scientificName')
            clean_name = clean_species_name(scientific_name)
            species_key = species.get('key')
            
            print(f"\n{'='*50}")
            print(f"Marine Species: {clean_name}")
            print(f"{'='*50}")
            
            monthly_data = get_monthly_population(species_key)
            marine_species_data[clean_name] = monthly_data
            
            # Print data as it's collected
            for year in sorted(monthly_data.keys()):
                print(f"\nYear: {year}")
                for month in range(1, 13):
                    count = monthly_data[year].get(month, 0)
                    print(f"Month {month}: {count} sightings")
        
        # Save all data to CSV
        save_marine_data_to_csv(marine_species_data)
        print("\nData has been saved to 'marine_species_data.csv'")

if __name__ == "__main__":
    main()