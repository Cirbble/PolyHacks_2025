import requests
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import csv
import os

def check_species_data_availability(species_key, timeout=5):
    """
    Quickly check if a species has accessible data
    """
    base_url = "https://api.gbif.org/v1/occurrence/search"
    params = {
        'speciesKey': species_key,
        'limit': 1,
        'basisOfRecord': 'HUMAN_OBSERVATION'
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data['count'] > 0  # Return True if there are any records
    except:
        return False

def search_marine_species(limit=100):
    """
    Search for terrestrial vertebrate species using GBIF API
    """
    skip_species = {
        'Eptesicus serotinus',
    }
    
    base_url = "https://api.gbif.org/v1/species/search"
    params = {
        'habitat': 'terrestrial',
        'highertaxonKey': '44',
        'rank': 'SPECIES',
        'status': 'ACCEPTED',
        'limit': limit,
        'offset': 0
    }
    
    all_results = []
    checked_species = 0
    
    while len(all_results) < limit:
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data['results']:
                break
                
            for species in data['results']:
                checked_species += 1
                scientific_name = species.get('scientificName', '')
                
                if scientific_name in skip_species:
                    print(f"Skipping known slow species: {scientific_name}")
                    continue
                
                class_name = species.get('class', '').lower()
                if class_name in ['mammalia', 'reptilia']:
                    # Quick check if species has data
                    if check_species_data_availability(species.get('key')):
                        all_results.append(species)
                        print(f"Found viable species: {scientific_name}")
                    else:
                        print(f"Skipping {scientific_name} - No accessible data")
                
                if len(all_results) >= limit:
                    break
            
            params['offset'] += params['limit']
            print(f"Checked {checked_species} species, found {len(all_results)} viable candidates...")
            
        except requests.exceptions.RequestException as e:
            print(f"Error accessing GBIF API: {e}")
            break
    
    return all_results[:limit]

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

def get_seasonal_population(species_key, start_year=1980, end_year=2024, timeout=25):
    """
    Get seasonal occurrence counts for a specific species with timeout
    """
    base_url = "https://api.gbif.org/v1/occurrence/search"
    seasonal_counts = defaultdict(lambda: defaultdict(int))
    
    limit = 300
    offset = 0
    
    try:
        while True:
            params = {
                'speciesKey': species_key,
                'limit': limit,
                'offset': offset,
                'year': f'{start_year},{end_year}',
                'basisOfRecord': 'HUMAN_OBSERVATION'
            }
            
            response = requests.get(base_url, params=params, timeout=timeout)
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
                        seasonal_counts[year][season] += 1
                    except (ValueError, IndexError):
                        continue
            
            offset += limit
            if offset >= data['count']:
                break
                
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
        print(f"Timeout or error for species {species_key} - skipping...")
        return None
    
    return dict(sorted(seasonal_counts.items())) if seasonal_counts else None

def get_monthly_population(species_key, start_year=1980, end_year=2024, timeout=30):
    """
    Get monthly occurrence counts for a specific species with timeout
    """
    base_url = "https://api.gbif.org/v1/occurrence/search"
    monthly_counts = defaultdict(lambda: defaultdict(int))
    
    limit = 300
    offset = 0
    
    try:
        while True:
            params = {
                'speciesKey': species_key,
                'limit': limit,
                'offset': offset,
                'year': f'{start_year},{end_year}',
                'basisOfRecord': 'HUMAN_OBSERVATION'
            }
            
            response = requests.get(base_url, params=params, timeout=timeout)
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
                
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
        print(f"Error getting data for species {species_key}: {e}")
        return None
    
    return dict(sorted(monthly_counts.items())) if monthly_counts else None

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

def save_species_to_csv(species_name, monthly_data, filename='terrestrial_species_data.csv', first_write=False):
    """
    Save a single species' data to CSV, maintaining chronological order by month
    """
    # Read existing data if file exists and not first write
    existing_data = []
    if not first_write and os.path.exists(filename):
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)  # Skip header
            existing_data = list(reader)
    
    # Convert new data to rows, excluding 0 sightings
    new_data = []
    for year, months in sorted(monthly_data.items()):
        for month in range(1, 13):
            sightings = months.get(month, 0)
            if sightings > 0:  # Only include non-zero sightings
                monthly_index = calculate_monthly_index(int(year), month)
                new_data.append([
                    species_name,
                    year,
                    month,
                    monthly_index,
                    sightings
                ])
    
    # Combine and sort all data
    all_data = existing_data + new_data
    all_data.sort(key=lambda x: (int(x[1]), int(x[2])))  # Sort by year, then month
    
    # Write all data back to file
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['speciesName', 'year', 'month', 'monthlyIndex', 'sightings'])
        writer.writerows(all_data)

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
                if count > 0:  # Only write non-zero counts
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
    print("Searching for terrestrial animals...")
    species_results = search_marine_species(limit=20)
    
    if species_results:
        processed_count = 0
        skipped_count = 0
        first_species = True
        
        for species in species_results:
            try:
                scientific_name = species.get('scientificName')
                clean_name = clean_species_name(scientific_name)
                species_key = species.get('key')
                class_name = species.get('class', 'Unknown')
                
                print(f"\n{'='*50}")
                print(f"Processing: {clean_name} ({class_name})")
                print(f"{'='*50}")
                
                monthly_data = get_monthly_population(species_key)  # Using monthly instead of seasonal
                
                if monthly_data:
                    # Save data immediately for this species
                    save_species_to_csv(clean_name, monthly_data, first_write=first_species)
                    first_species = False
                    
                    processed_count += 1
                    print(f"Successfully processed and saved {clean_name}")
                    
                    # Print sample of data
                    print("Sample of collected data:")
                    for year in list(sorted(monthly_data.keys()))[-3:]:
                        print(f"\nYear {year}:")
                        total_year = sum(monthly_data[year].values())
                        print(f"Total sightings: {total_year}")
                else:
                    print(f"Skipping {clean_name} - No data available")
                    skipped_count += 1
                
                if processed_count >= 10:
                    break
                    
            except Exception as e:
                print(f"Error processing {clean_name}: {e}")
                skipped_count += 1
                continue
        
        print(f"\nProcessing complete:")
        print(f"- Successfully processed: {processed_count} species")
        print(f"- Skipped: {skipped_count} species")
        print(f"- Data saved to 'terrestrial_species_data.csv'")
    else:
        print("\nNo species found to process")

if __name__ == "__main__":
    main()