import requests
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import csv
import os

def check_species_data_availability(species_key):
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
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data['count'] > 0  # Return True if there are any records
    except:
        return False

def search_marine_species(limit=100):
    """
    Search for terrestrial vertebrate species using GBIF API
    """
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
                
                class_name = species.get('class', '').lower()
                if class_name in ['mammalia', 'reptilia']:
                    all_results.append(species)
                    print(f"Found species: {scientific_name}")
                
                if len(all_results) >= limit:
                    break
            
            params['offset'] += params['limit']
            print(f"Checked {checked_species} species, found {len(all_results)} candidates...")
            
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

def get_seasonal_population(species_key, start_year=1980, end_year=2024):
    """
    Get seasonal occurrence counts for a specific species
    """
    base_url = "https://api.gbif.org/v1/occurrence/search"
    seasonal_counts = defaultdict(lambda: defaultdict(int))
    
    limit = 1000  # Increased from 300 for faster data collection
    offset = 0
    
    try:
        # First get total count
        params = {
            'speciesKey': species_key,
            'limit': 1,
            'year': f'{start_year},{end_year}',
            'basisOfRecord': 'HUMAN_OBSERVATION'
        }
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        total_records = response.json()['count']
        
        print(f"\nCollecting {total_records} seasonal records:")
        progress_length = 40  # Length of progress bar
        
        while True:
            params = {
                'speciesKey': species_key,
                'limit': limit,
                'offset': offset,
                'year': f'{start_year},{end_year}',
                'basisOfRecord': 'HUMAN_OBSERVATION'
            }
            
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data['results']:
                break
                
            # Update progress bar
            progress = min(offset + limit, total_records)
            filled_length = int(progress_length * progress // total_records)
            bar = '█' * filled_length + '-' * (progress_length - filled_length)
            percent = progress * 100 // total_records
            print(f'\rProgress: |{bar}| {percent}% Complete ({progress}/{total_records} records)', end='')
            
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
        
        print()  # New line after progress bar
                
    except requests.exceptions.RequestException as e:
        print(f"\nError getting data for species {species_key}: {e}")
        return None
    
    return dict(sorted(seasonal_counts.items())) if seasonal_counts else None

def get_monthly_population(species_key, species_name, first_species, start_year=1980, end_year=2024):
    """
    Get monthly occurrence counts for a specific species
    """
    base_url = "https://api.gbif.org/v1/occurrence/search"
    monthly_counts = defaultdict(lambda: defaultdict(int))
    
    # Dictionary to store all sightings for this species
    all_sightings = defaultdict(int)  # key: (year, month, monthlyIndex)
    
    # Increase limit to get more data per request
    limit = 1000
    offset = 0
    
    try:
        # First get total count
        params = {
            'speciesKey': species_key,
            'limit': 1,
            'year': f'{start_year},{end_year}',
            'basisOfRecord': 'HUMAN_OBSERVATION'
        }
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        total_records = response.json()['count']
        
        print(f"\nCollecting {total_records} records:")
        progress_length = 40
        
        while True:
            try:
                params = {
                    'speciesKey': species_key,
                    'limit': limit,
                    'offset': offset,
                    'year': f'{start_year},{end_year}',
                    'basisOfRecord': 'HUMAN_OBSERVATION'
                }
                
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('results'):
                    break
                
                # Update progress bar
                progress = min(offset + limit, total_records)
                filled_length = int(progress_length * progress // total_records)
                bar = '█' * filled_length + '-' * (progress_length - filled_length)
                percent = progress * 100 // total_records
                print(f'\rProgress: |{bar}| {percent}% Complete ({progress}/{total_records} records)', end='')
                
                # Process records
                for occurrence in data['results']:
                    year = occurrence.get('year')
                    event_date = occurrence.get('eventDate')
                    
                    if year or event_date:
                        try:
                            if event_date:
                                date_str = event_date.split('T')[0]
                                date = datetime.strptime(date_str, '%Y-%m-%d')
                                month = date.month
                            else:
                                month = 1
                            
                            if not year:
                                year = date.year if event_date else start_year
                            
                            monthly_counts[year][month] += 1
                            monthly_index = calculate_monthly_index(int(year), month)
                            
                            # Store sighting
                            key = (year, month, monthly_index)
                            all_sightings[key] += 1
                            
                        except (ValueError, IndexError, AttributeError):
                            continue
                
                offset += limit
                if offset >= data['count']:
                    break
                    
            except requests.exceptions.RequestException as e:
                # Save what we have so far before reporting the error
                if all_sightings:
                    save_current_data(all_sightings, species_name, first_species)
                print(f"\nWarning: Error in batch request: {e}")
                continue
        
        print()  # New line after progress bar
        
    except Exception as e:
        # Save any collected data before raising the error
        if all_sightings:
            save_current_data(all_sightings, species_name, first_species)
            print(f"\nSaved {len(all_sightings)} records before error")
        raise  # Re-raise the exception to be caught by the main loop
    
    # Save all collected data
    if all_sightings:
        save_current_data(all_sightings, species_name, first_species)
    
    return dict(sorted(monthly_counts.items()))

def save_current_data(all_sightings, species_name, first_species):
    """
    Helper method to save current data to CSV
    """
    # Create file with header if this is first species
    if first_species:
        with open('terrestrial_species_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['speciesName', 'year', 'month', 'monthlyIndex', 'sightings'])
    
    # Append all sightings for this species
    with open('terrestrial_species_data.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for (year, month, monthly_index), count in sorted(all_sightings.items()):
            writer.writerow([species_name, year, month, monthly_index, count])

def get_species_population_trend(scientific_name, start_year=1980):
    """
    Get population trend starting from 1980
    """
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

def get_existing_species():
    """
    Get list of species already processed from CSV file
    """
    existing_species = set()
    if os.path.exists('terrestrial_species_data.csv'):
        with open('terrestrial_species_data.csv', 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            for row in reader:
                existing_species.add(row[0])  # Add species name to set
    return existing_species

def main():
    print("Searching for terrestrial animals...")
    species_results = search_marine_species(limit=100)
    
    if species_results:
        # Get list of already processed species
        existing_species = get_existing_species()
        
        processed_count = 0
        skipped_count = 0
        first_write = not bool(existing_species)  # Only true if no existing species
        total_species = len(species_results)
        
        print(f"\nFound {total_species} species to process")
        print(f"Already processed: {len(existing_species)} species")
        
        for i, species in enumerate(species_results, 1):
            try:
                scientific_name = species.get('scientificName')
                clean_name = clean_species_name(scientific_name)
                species_key = species.get('key')
                class_name = species.get('class', 'Unknown')
                
                # Skip if species already processed
                if clean_name in existing_species:
                    print(f"\nSkipping {clean_name} - Already processed")
                    skipped_count += 1
                    continue
                
                print(f"\n{'='*50}")
                print(f"Species {i}/{total_species}: {clean_name} ({class_name})")
                print(f"{'='*50}")
                
                try:
                    monthly_data = get_monthly_population(species_key, clean_name, first_write)
                    
                    if monthly_data:
                        first_write = False
                        processed_count += 1
                        print(f"✓ Successfully processed and saved {clean_name}")
                        
                        # Print sample of data
                        print("\nSample of collected data:")
                        for year in list(sorted(monthly_data.keys()))[-3:]:
                            print(f"Year {year}: {sum(monthly_data[year].values())} total sightings")
                    else:
                        print(f"✗ No data available for {clean_name}")
                        skipped_count += 1
                        
                except Exception as e:
                    print(f"✗ Error processing {clean_name}: {str(e)}")
                    print(f"Current progress saved. Moving to next species...")
                    skipped_count += 1
                    continue
                    
            except Exception as e:
                print(f"✗ Error with species metadata: {str(e)}")
                skipped_count += 1
                continue
        
        print(f"\n{'='*50}")
        print("Processing complete:")
        print(f"✓ Successfully processed: {processed_count} new species")
        print(f"✗ Skipped: {skipped_count} species")
        print(f"📁 Data appended to 'terrestrial_species_data.csv'")
        print(f"{'='*50}")
    else:
        print("\nNo species found to process")

if __name__ == "__main__":
    main()