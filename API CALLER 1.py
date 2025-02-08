import requests
from collections import defaultdict

def search_species(query, limit=10):
    """
    Search for species using GBIF API
    """
    base_url = "https://api.gbif.org/v1/species/search"
    params = {
        'q': query,
        'limit': limit
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data['results']
    except requests.exceptions.RequestException as e:
        print(f"Error accessing GBIF API: {e}")
        return None

def get_species_occurrences_by_year(species_key, start_year=1980, end_year=2024):
    """
    Get occurrence counts per year for a specific species
    """
    base_url = "https://api.gbif.org/v1/occurrence/search"
    
    # Initialize counts dictionary
    yearly_counts = defaultdict(int)
    
    # Set a larger limit to get more comprehensive data
    limit = 300
    offset = 0
    
    while True:
        params = {
            'speciesKey': species_key,
            'limit': limit,
            'offset': offset,
            'year': f'{start_year},{end_year}'
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Break if no more results
            if not data['results']:
                break
                
            # Count occurrences by year
            for occurrence in data['results']:
                year = occurrence.get('year')
                if year:
                    yearly_counts[year] += 1
            
            # Update offset for next page
            offset += limit
            
            # Break if we've got all results
            if offset >= data['count']:
                break
                
        except requests.exceptions.RequestException as e:
            print(f"Error accessing GBIF API: {e}")
            break
    
    return dict(sorted(yearly_counts.items()))

def main():
    # Search for species
    species_results = search_species("homo sapiens", limit=5)  # Limiting to 5 species for example
    
    if species_results:
        print("\nPopulation Data by Year:")
        for species in species_results:
            scientific_name = species.get('scientificName')
            species_key = species.get('key')
            print(f"\nSpecies: {scientific_name}")
            print("Year | Count")
            print("-" * 20)
            
            yearly_data = get_species_occurrences_by_year(species_key)
            for year, count in yearly_data.items():
                print(f"{year}: {count} occurrences")
            
            # Print total observations
            total = sum(yearly_data.values())
            print(f"Total observations: {total}")

if __name__ == "__main__":
    main()