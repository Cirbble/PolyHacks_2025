import React, { useState } from 'react';
import { CircleMarker, Popup } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import axios from 'axios';
import { Typography, Box, Autocomplete, TextField } from '@mui/material';
import debounce from 'lodash/debounce';

const OCEANS = [
  "Pacific Ocean",
  "Atlantic Ocean",
  "Indian Ocean",
  "Southern Ocean",
  "Arctic Ocean",
  "Mediterranean Sea",
  "Caribbean Sea"
];

const BiodiversityMap = () => {
  const [occurrences, setOccurrences] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState('');
  const [options, setOptions] = useState([]);
  const [open, setOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');

  const cleanScientificName = (name) => {
    if (!name) return '';
    // First remove parenthetical notes
    name = name.replace(/\s*\([^)]*\)/g, '');
    // Remove everything after the first comma
    name = name.split(',')[0];
    // Remove any trailing author names (including those without commas)
    name = name.replace(/\s+(?:[A-Z][a-zA-Z.-]+\s*(?:&|et)?\s*)+$/, '');
    // Remove any remaining author-like patterns
    name = name.replace(/\s+(?:van|de|der|von)\s+[A-Z][a-zA-Z]*/, '');
    return name.trim();
  };

  const fetchSpeciesSuggestions = async (input) => {
    try {
      // Also search directly with the input to catch common names
      const [speciesResponse, vernacularResponse] = await Promise.all([
        axios.get('https://api.gbif.org/v1/species/suggest', {
          params: {
            q: input || '',
            limit: 50
          }
        }),
        axios.get('https://api.gbif.org/v1/species/search', {
          params: {
            q: input || '',
            limit: 50
          }
        })
      ]);

      // Combine results from both endpoints
      const allResults = [...speciesResponse.data, ...vernacularResponse.data.results];

      // Check occurrence counts for each unique species
      const uniqueKeys = new Set(allResults.map(item => item.key));
      const occurrencePromises = Array.from(uniqueKeys).map(async key => {
        if (key) {
          try {
            const occurrenceResponse = await axios.get('https://api.gbif.org/v1/occurrence/search', {
        params: {
                taxonKey: key,
          hasCoordinate: true,
          hasGeospatialIssue: false,
                limit: 0 // We only need the count
              }
            });
            return {
              key,
              count: occurrenceResponse.data.count
            };
          } catch (error) {
            console.warn(`Could not fetch occurrence count for key ${key}:`, error);
            return { key, count: 0 };
          }
        }
        return { key, count: 0 };
      });

      const occurrenceCounts = await Promise.all(occurrencePromises);
      const occurrenceMap = new Map(occurrenceCounts.map(item => [item.key, item.count]));

      // Fetch vernacular names for species that have occurrences
      const vernacularPromises = Array.from(uniqueKeys).map(async key => {
        if (key && occurrenceMap.get(key) > 0) {
          try {
            // First try to get the name from iNaturalist
            const iNatResponse = await axios.get(`https://api.inaturalist.org/v1/taxa/autocomplete`, {
              params: {
                q: allResults.find(r => r.key === key)?.scientificName || '',
                locale: 'en'
              }
            });

            let commonName = '';
            if (iNatResponse.data.results && iNatResponse.data.results.length > 0) {
              // Find exact match by scientific name
              const exactMatch = iNatResponse.data.results.find(
                r => cleanScientificName(r.name).toLowerCase() === 
                     cleanScientificName(allResults.find(ar => ar.key === key)?.scientificName || '').toLowerCase()
              );
              if (exactMatch && exactMatch.preferred_common_name) {
                commonName = exactMatch.preferred_common_name;
              }
            }

            // If no name found from iNat, try GBIF as fallback
            if (!commonName) {
              const vernacularResponse = await axios.get(`https://api.gbif.org/v1/species/${key}/vernacularNames`);
              const englishNames = vernacularResponse.data.results
                .filter(name => name.language === 'eng')
                .map(name => name.vernacularName);
              commonName = englishNames[0] || '';
            }

            return {
              key,
              vernacularNames: commonName ? [commonName] : []
            };
          } catch (error) {
            console.warn(`Could not fetch vernacular names for key ${key}:`, error);
            return { key, vernacularNames: [] };
          }
        }
        return { key, vernacularNames: [] };
      });

      const vernacularResults = await Promise.all(vernacularPromises);
      const vernacularMap = new Map(vernacularResults.map(item => [item.key, item.vernacularNames]));

      // Group suggestions by cleaned scientific name, only including those with occurrences
      const groupedSuggestions = new Map();
      
      allResults.forEach(item => {
        if (!item.key || occurrenceMap.get(item.key) === 0) return; // Skip items with no occurrences

        const cleanedName = cleanScientificName(item.scientificName);
        
        if (!groupedSuggestions.has(cleanedName)) {
          // Get all vernacular names for this species
          const vernacularNames = item.key ? vernacularMap.get(item.key) || [] : [];
          if (item.vernacularName && !vernacularNames.includes(item.vernacularName)) {
            vernacularNames.push(item.vernacularName);
          }
          
          // Create new entry
          groupedSuggestions.set(cleanedName, {
            scientificName: cleanedName,
            commonName: vernacularNames[0] || item.vernacularName,
            allCommonNames: vernacularNames,
            rank: item.rank,
            kingdom: item.kingdom,
            keys: new Set(), // Store all taxon keys
            genusKey: item.genusKey,
            genus: item.genus,
            family: item.family,
            order: item.order,
            class: item.class,
            phylum: item.phylum,
            occurrenceCount: occurrenceMap.get(item.key)
          });
        }
        
        // Add the key to the set of keys
        if (item.key) {
          groupedSuggestions.get(cleanedName).keys.add(item.key);
        }
      });

      // Convert to array and prepare for filtering
      let suggestions = Array.from(groupedSuggestions.values())
        .map(suggestion => ({
          ...suggestion,
          key: Array.from(suggestion.keys)[0],
          allKeys: Array.from(suggestion.keys),
          displayName: `${suggestion.scientificName}${suggestion.commonName ? ` [${suggestion.commonName}]` : ''}`
        }))
        .filter(item => {
          if (!input) return true;
          return item.scientificName.toLowerCase().includes(input.toLowerCase());
        });

      // Simple sort by name length to keep shorter names first
      suggestions.sort((a, b) => a.scientificName.length - b.scientificName.length);

      console.log('Filtered suggestions:', suggestions);
      setOptions(suggestions);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      setOptions([]);
    }
  };

  const debouncedFetch = debounce(fetchSpeciesSuggestions, 300);

  const searchSpecies = async (species) => {
    if (!species) return;

    setLoading(true);
    setLoadingStatus('Searching...');
    
    try {
      console.log('Searching for species:', species);

      // First try to get the full species info to ensure we have the correct keys
      const speciesInfo = await axios.get(`https://api.gbif.org/v1/species/${species.key}`);
      console.log('Species info:', speciesInfo.data);

      // Build search parameters based on the rank
      let searchParams = {
        hasCoordinate: true,
        hasGeospatialIssue: false,
        limit: 1000
      };

      // If it's a genus, search by genusKey, otherwise try both taxonKey and higherTaxonKey
      if (species.rank === 'GENUS' || speciesInfo.data.rank === 'GENUS') {
        searchParams.genusKey = species.key;
      } else {
        // Try both the specific taxon and its parent taxon
        searchParams.taxonKey = species.key;
      }

      console.log('Using search parameters:', searchParams);

      // First try with the main search parameters
      let response = await axios.get('https://api.gbif.org/v1/occurrence/search', {
        params: searchParams
      });

      let allResults = response.data.results || [];
      let totalRecords = response.data.count || 0;

      // If we got no results and we have a genusKey, try searching by genus
      if (totalRecords === 0 && species.genusKey) {
        console.log('No results found with taxonKey, trying genusKey:', species.genusKey);
        response = await axios.get('https://api.gbif.org/v1/occurrence/search', {
          params: {
            ...searchParams,
            genusKey: species.genusKey,
            taxonKey: undefined
          }
        });
        allResults = response.data.results || [];
        totalRecords = response.data.count || 0;
      }

      // If we still have no results and we have parent keys, try those
      if (totalRecords === 0 && speciesInfo.data.parentKey) {
        console.log('No results found with genusKey, trying parentKey:', speciesInfo.data.parentKey);
        response = await axios.get('https://api.gbif.org/v1/occurrence/search', {
          params: {
            ...searchParams,
            taxonKey: speciesInfo.data.parentKey,
            genusKey: undefined
          }
        });
        allResults = response.data.results || [];
        totalRecords = response.data.count || 0;
      }

      console.log(`Total records found: ${totalRecords}`);

      // Deduplicate locations
      const uniqueLocations = new Map();
      allResults.forEach(occurrence => {
        const key = `${occurrence.decimalLatitude}-${occurrence.decimalLongitude}`;
        if (!uniqueLocations.has(key)) {
          occurrence.scientificName = cleanScientificName(occurrence.scientificName);
          uniqueLocations.set(key, occurrence);
        }
      });

      const uniqueOccurrences = Array.from(uniqueLocations.values());
      console.log('Final unique locations:', uniqueOccurrences.length);
      
      setOccurrences(uniqueOccurrences);
      setLoadingStatus(`Found ${uniqueOccurrences.length.toLocaleString()} locations for ${species.scientificName} (Total records: ${totalRecords})`);
    } catch (error) {
      console.error('Error details:', error.response?.data || error.message);
      console.error('Full error:', error);
      setLoadingStatus('Error loading data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Box 
        position="absolute" 
        zIndex={1000} 
        top={0} 
        left={0} 
        right={0}
        bgcolor="white" 
        p={2} 
        sx={{ 
          display: 'flex',
          gap: 2,
          alignItems: 'center',
          boxShadow: 1
        }}
      >
        <Autocomplete
          sx={{ flex: 1, maxWidth: 800, mx: 'auto' }}
          open={open}
          onOpen={() => setOpen(true)}
          onClose={() => setOpen(false)}
          options={options}
          loading={loading}
          getOptionLabel={(option) => option.displayName || ''}
          filterOptions={(options, { inputValue }) => {
            const searchStr = inputValue.toLowerCase();
            return options.filter(option => 
              option.scientificName.toLowerCase().includes(searchStr)
            );
          }}
          noOptionsText="No species found"
          freeSolo
          autoComplete
          includeInputInList
          value={null}
          onChange={(event, newValue) => {
            if (newValue && newValue.key) {
              searchSpecies(newValue);
            }
          }}
          onInputChange={(event, newInputValue) => {
            setInputValue(newInputValue);
            debouncedFetch(newInputValue);
          }}
          renderInput={(params) => (
            <TextField
              {...params}
              size="small"
              placeholder="Search for species or common name..."
              fullWidth
            />
          )}
          renderOption={(props, option) => (
            <li {...props}>
              <Box>
                <Typography variant="body1">
                  {option.scientificName}
                  {option.commonName && (
                    <Typography component="span" sx={{ ml: 1, fontStyle: 'italic' }}>
                      [{option.commonName}]
          </Typography>
        )}
                </Typography>
              </Box>
            </li>
          )}
        />

        <Typography variant="body2" sx={{ minWidth: 200 }}>
          {loadingStatus}
        </Typography>
      </Box>

      <MarkerClusterGroup
        chunkedLoading
        maxClusterRadius={100}
        spiderfyOnMaxZoom={false}
        disableClusteringAtZoom={12}
        removeOutsideVisibleBounds={true}
      >
        {occurrences.map((occurrence, index) => (
          <CircleMarker
            key={`${occurrence.key}-${index}`}
            center={[occurrence.decimalLatitude, occurrence.decimalLongitude]}
            radius={3}
            pathOptions={{
              fillColor: '#1976D2',
              color: '#0D47A1',
              weight: 1,
              opacity: 0.7,
              fillOpacity: 0.5
            }}
          >
            <Popup>
              <div>
                <h3>{occurrence.scientificName}</h3>
                {occurrence.vernacularName && (
                  <p><i>{occurrence.vernacularName}</i></p>
                )}
                {occurrence.waterBody && (
                  <p>Water Body: {occurrence.waterBody}</p>
                )}
                {occurrence.locality && (
                  <p>Locality: {occurrence.locality}</p>
                )}
                {occurrence.stateProvince && (
                  <p>State/Province: {occurrence.stateProvince}</p>
                )}
                {occurrence.country && (
                  <p>Country: {occurrence.country}</p>
                )}
                {occurrence.eventDate && (
                  <p>Date: {new Date(occurrence.eventDate).toLocaleDateString()}</p>
                )}
                {occurrence.depth && (
                  <p>Depth: {occurrence.depth}m</p>
                )}
                {occurrence.elevation && (
                  <p>Elevation: {occurrence.elevation}m</p>
                )}
                {occurrence.habitat && (
                  <p>Habitat: {occurrence.habitat}</p>
                )}
                {occurrence.recordedBy && (
                  <p>Recorded by: {occurrence.recordedBy}</p>
                )}
                {occurrence.institutionCode && (
                  <p>Institution: {occurrence.institutionCode}</p>
                )}
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MarkerClusterGroup>
    </>
  );
};

export default BiodiversityMap; 