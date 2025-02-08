import requests
from collections import defaultdict
from datetime import datetime

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

def get_seasonal_population(species_key, start_year=1900, end_year=2024):
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

if __name__ == "__main__":
    main()