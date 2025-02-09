import { useState, useEffect, useCallback } from 'react';
import { MapContainer, CircleMarker, Popup, TileLayer } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import axios from 'axios';
import { Autocomplete, TextField, Box, Typography, CircularProgress, Slider } from '@mui/material';
import TopBar from './components/TopBar';
import 'leaflet/dist/leaflet.css';

interface Occurrence {
  key: string;
  decimalLatitude: number;
  decimalLongitude: number;
  scientificName: string;
  vernacularName?: string;
  locality?: string;
  country?: string;
  eventDate?: string;
}

interface SpeciesSuggestion {
  key: string;
  scientificName: string;
  vernacularName?: string;
  count: number;
  selected?: boolean;
}

// Add these interfaces for API responses
interface GBIFSpeciesResponse {
  key: number;
  scientificName: string;
  vernacularName?: string;
}

interface GBIFOccurrenceCountResponse {
  count: number;
  limit: number;
  offset: number;
}

interface GBIFOccurrenceResponse {
  results: {
    key: string;
    decimalLatitude: number;
    decimalLongitude: number;
    scientificName: string;
    vernacularName?: string;
    locality?: string;
    country?: string;
    eventDate?: string;
  }[];
}

interface YearControl {
  selectedYear: string;
  isPlaying: boolean;
  playbackSpeed: number;
  progress: number;
}

const cleanScientificName = (name: string): string => {
  if (!name) return '';
  // Remove content in parentheses
  name = name.replace(/\s*\([^)]*\)/g, '');
  // Remove everything after comma
  name = name.split(',')[0];
  // Remove author names that follow the species name
  name = name.replace(/\s+(?:[A-Z][a-zA-Z.-]+\s*(?:&|et)?\s*)+$/, '');
  // Remove taxonomic author prefixes
  name = name.replace(/\s+(?:van|de|der|von)\s+[A-Z][a-zA-Z]*/, '');
  return name.trim();
};

const BiodiversityMap = () => {
  const [occurrences, setOccurrences] = useState<Occurrence[]>([]);
  const [options, setOptions] = useState<SpeciesSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState('');
  const currentYear = new Date().getFullYear();
  const years = Array.from(
    { length: currentYear - 1980 + 1 }, 
    (_, i) => (1980 + i).toString()
  );
  const [yearControl, setYearControl] = useState<YearControl>({
    selectedYear: 'all',
    isPlaying: false,
    playbackSpeed: 1000,
    progress: 0
  });
  const [yearInput, setYearInput] = useState('All');
  const [isManuallyEditing, setIsManuallyEditing] = useState(false);
  const [selectedSpeciesKey, setSelectedSpeciesKey] = useState<string | null>(null);

  const searchSpecies = async (input: string) => {
    if (!input) {
      setOptions([]);
      return;
    }

    try {
      setLoading(true);
      
      // First get species suggestions
      const speciesResponse = await axios.get<GBIFSpeciesResponse[]>('https://api.gbif.org/v1/species/suggest', {
        params: {
          q: input,
          limit: 10
        }
      });

      // Check occurrence counts for each species
      const occurrenceChecks = await Promise.all(
        speciesResponse.data.map(async (species) => {
          const occResponse = await axios.get<GBIFOccurrenceCountResponse>('https://api.gbif.org/v1/occurrence/search', {
            params: {
              taxonKey: species.key,
              hasCoordinate: true,
              hasGeospatialIssue: false,
              limit: 0  // We only need the count
            }
          });
          return {
            species,
            count: occResponse.data.count
          };
        })
      );

      // Filter and map species with occurrences
      const suggestions = occurrenceChecks
        .filter(item => item.count > 0)
        .map(item => ({
          key: item.species.key.toString(),
          scientificName: cleanScientificName(item.species.scientificName),
          vernacularName: item.species.vernacularName,
          count: item.count
        }));

      setOptions(suggestions);
    } catch (error) {
      console.error('Error searching species:', error);
      setOptions([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchOccurrences = useCallback(async (speciesKey: string, year?: string) => {
    try {
      setLoadingStatus(`Loading data...`);
      const params: any = {
        taxonKey: speciesKey,
        hasCoordinate: true,
        hasGeospatialIssue: false,
      };

      // First, get the total count
      const countResponse = await axios.get<GBIFOccurrenceCountResponse>(
        'https://api.gbif.org/v1/occurrence/search',
        { 
          params: {
            ...params,
            limit: 0,
            year: year !== 'all' ? year : undefined
          }
        }
      );

      const totalCount = countResponse.data.count;
      const maxRecords = Math.min(totalCount, year === 'all' ? 10000 : 1000); // Increased for all years
      const batchSize = 1000; // Increased batch size for efficiency

      let allResults: GBIFOccurrenceResponse['results'] = [];
      let offset = 0;

      setLoadingStatus(`Loading ${maxRecords} records...`);

      while (allResults.length < maxRecords) {
        const batchParams = {
          ...params,
          limit: Math.min(batchSize, maxRecords - allResults.length),
          offset,
          year: year !== 'all' ? year : undefined
        };

        const response = await axios.get<GBIFOccurrenceResponse>(
          'https://api.gbif.org/v1/occurrence/search',
          { params: batchParams }
        );

        if (response.data.results.length === 0) break;

        allResults = [...allResults, ...response.data.results];
        offset += response.data.results.length;

        // Update loading status to show percentage
        const percentage = Math.round((allResults.length / maxRecords) * 100);
        setLoadingStatus(`Loading... ${percentage}%`);
      }

      const uniqueLocations = new Map();
      allResults.forEach((occurrence) => {
        const key = `${occurrence.decimalLatitude}-${occurrence.decimalLongitude}`;
        if (!uniqueLocations.has(key)) {
          uniqueLocations.set(key, {
            key: occurrence.key,
            decimalLatitude: occurrence.decimalLatitude,
            decimalLongitude: occurrence.decimalLongitude,
            scientificName: cleanScientificName(occurrence.scientificName),
            vernacularName: occurrence.vernacularName,
            locality: occurrence.locality,
            country: occurrence.country,
            eventDate: occurrence.eventDate
          });
        }
      });

      const uniqueOccurrences = Array.from(uniqueLocations.values());
      
      // Final status message with unique locations and total available
      const statusMessage = year && year !== 'all' 
        ? `Found ${uniqueOccurrences.length} unique locations in ${year} (from ${totalCount} total records)`
        : `Found ${uniqueOccurrences.length} unique locations (from ${totalCount} total records)`;
      
      setOccurrences(uniqueOccurrences);
      setLoadingStatus(statusMessage);
      
      return uniqueOccurrences;
    } catch (error) {
      console.error('Error fetching occurrences:', error);
      setLoadingStatus('Error loading data');
      setOccurrences([]);
      throw error;
    }
  }, []);

  const toggleYearPlayback = () => {
    setYearControl(prev => ({
      ...prev,
      isPlaying: !prev.isPlaying,
      // If starting playback and at the end, reset to beginning
      progress: prev.progress >= years.length - 1 ? 0 : prev.progress
    }));
  };

  const handleAllYearsClick = async () => {
    if (yearControl.isPlaying) {
      setYearControl(prev => ({ ...prev, isPlaying: false }));
    }
    
    setYearControl(prev => ({ ...prev, selectedYear: 'all' }));
    setYearInput('All');
    
    if (selectedSpeciesKey) {
      try {
        setLoadingStatus('Loading data for all years...');
        await fetchOccurrences(selectedSpeciesKey, 'all');
      } catch (error) {
        console.error('Error loading all years:', error);
        setLoadingStatus('Error loading data');
      }
    }
  };

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    
    if (yearControl.isPlaying) {
      timeoutId = setTimeout(() => {
        setYearControl(prev => {
          let newProgress = prev.progress + 1;
          
          if (newProgress >= years.length - 1) {
            newProgress = 0;
          }
          
          const newYear = years[Math.floor(newProgress)];
          
          // Use the stored selectedSpeciesKey
          if (selectedSpeciesKey) {
            fetchOccurrences(selectedSpeciesKey, newYear);
          }
          
          return {
            ...prev,
            progress: newProgress,
            selectedYear: newYear
          };
        });
      }, yearControl.playbackSpeed);
    }
    
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [yearControl.isPlaying, yearControl.progress, years, selectedSpeciesKey, fetchOccurrences]);

  useEffect(() => {
    // Only update yearInput from slider if we're not manually editing
    if (!isManuallyEditing) {
      setYearInput(yearControl.selectedYear === 'all' ? 'All' : years[Math.floor(yearControl.progress)]);
    }
  }, [yearControl.progress, yearControl.selectedYear, years, isManuallyEditing]);

  return (
    <div className="map-page">
      <div style={{ 
        width: '100vw',
        height: '100vh',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#f5f5f5'
      }}>
        <TopBar />

        <Box sx={{
          width: '100%',
          height: 'calc(100vh - 70px)',
          mt: '70px',
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          padding: '16px'
        }}>
          {/* Search Container */}
          <Box sx={{
            width: '100%',
            padding: '16px',
            backgroundColor: 'white',
            display: 'flex',
            justifyContent: 'center',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            borderRadius: '8px',
            zIndex: 2,
            gap: 2
          }}>
            <Autocomplete
              sx={{ width: '600px' }}
              options={options}
              getOptionLabel={(option) => 
                `${option.scientificName}${option.vernacularName ? ` (${option.vernacularName})` : ''}`
              }
              isOptionEqualToValue={(option, value) => option.key === value.key}
              onInputChange={(_, newValue) => searchSpecies(newValue)}
              onChange={(_, newValue) => {
                if (newValue?.key) {
                  setSelectedSpeciesKey(newValue.key);
                  setOptions(prev => prev.map(opt => ({
                    ...opt,
                    selected: opt.key === newValue.key
                  })));
                  // Fetch all years data by default
                  fetchOccurrences(newValue.key, 'all');
                } else {
                  setSelectedSpeciesKey(null);
                  setOptions(prev => prev.map(opt => ({
                    ...opt,
                    selected: false
                  })));
                }
              }}
              loading={loading}
              renderInput={(params) => (
                <TextField
                  {...params}
                  placeholder="Search for a species..."
                  size="small"
                  InputProps={{
                    ...params.InputProps,
                    endAdornment: (
                      <>
                        {loading && <CircularProgress color="inherit" size={20} />}
                        {params.InputProps.endAdornment}
                      </>
                    ),
                  }}
                />
              )}
            />
            <Typography variant="body2" sx={{ 
              minWidth: 150,
              display: 'flex',
              alignItems: 'center'
            }}>
              {loadingStatus}
            </Typography>
          </Box>

          {/* Map Container */}
          <Box sx={{
            flex: 1,
            border: '2px solid #3892C6',
            borderRadius: '8px',
            overflow: 'hidden',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            position: 'relative',
            '& .leaflet-container': {
              width: '100%',
              height: '100%',
              background: '#7FBADC'
            }
          }}>
            <MapContainer
              center={[20, 0]}
              zoom={2}
              minZoom={2}
              maxBounds={[[-90, -180], [90, 180]]}
              maxBoundsViscosity={1.0}
              style={{
                width: '100%',
                height: '100%'
              }}
              scrollWheelZoom={true}
            >
              <TileLayer
                noWrap={true}
                bounds={[[-90, -180], [90, 180]]}
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <MarkerClusterGroup
                chunkedLoading
                maxClusterRadius={50}
              >
                {occurrences.map((occurrence) => (
                  <CircleMarker
                    key={occurrence.key}
                    center={[occurrence.decimalLatitude, occurrence.decimalLongitude]}
                    radius={5}
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
                        {occurrence.locality && (
                          <p>Locality: {occurrence.locality}</p>
                        )}
                        {occurrence.country && (
                          <p>Country: {occurrence.country}</p>
                        )}
                        {occurrence.eventDate && (
                          <p>Date: {new Date(occurrence.eventDate).toLocaleDateString()}</p>
                        )}
                      </div>
                    </Popup>
                  </CircleMarker>
                ))}
              </MarkerClusterGroup>
            </MapContainer>

            {/* Year Control Bar */}
            <Box
              sx={{
                position: 'absolute',
                bottom: 20,
                left: '50%',
                transform: 'translateX(-50%)',
                width: '90%',
                maxWidth: 800,
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                padding: '16px',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                zIndex: 1000,
                display: 'flex',
                alignItems: 'center',
                gap: 2
              }}
            >
              <button
                onClick={handleAllYearsClick}
                style={{
                  backgroundColor: '#3892C6',
                  color: 'white',
                  padding: '8px 16px',
                  borderRadius: '4px',
                  border: 'none',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                All Years
              </button>
              
              <button
                onClick={toggleYearPlayback}
                style={{
                  backgroundColor: '#3892C6',
                  color: 'white',
                  width: '36px',
                  height: '36px',
                  borderRadius: '50%',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '20px'
                }}
              >
                {yearControl.isPlaying ? '⏸' : '▶️'}
              </button>
              
              <Slider
                value={yearControl.progress}
                min={0}
                max={years.length - 1}
                step={0.01}
                disabled={isManuallyEditing}
                onChange={(_, value) => {
                  if (!isManuallyEditing) {
                    const progress = typeof value === 'number' ? value : value[0];
                    const yearIndex = Math.floor(progress);
                    const selectedYear = years[yearIndex];
                    
                    setYearControl(prev => ({
                      ...prev,
                      progress,
                      selectedYear
                    }));
                    
                    setYearInput(selectedYear);

                    // Use the stored selectedSpeciesKey instead of searching through options
                    if (selectedSpeciesKey) {
                      fetchOccurrences(selectedSpeciesKey, selectedYear);
                    } else {
                      setLoadingStatus(`Select a species to view data for ${selectedYear}`);
                    }
                  }
                }}
                sx={{
                  '& .MuiSlider-thumb': {
                    backgroundColor: isManuallyEditing ? '#ccc' : '#3892C6',
                  },
                  '& .MuiSlider-track': {
                    backgroundColor: isManuallyEditing ? '#ccc' : '#3892C6',
                  },
                  '& .MuiSlider-rail': {
                    backgroundColor: isManuallyEditing ? '#ddd' : '#a8d4eb',
                  }
                }}
              />
              
              <TextField
                size="small"
                value={yearInput}
                onFocus={(e) => {
                  setIsManuallyEditing(true);
                  e.target.select();
                }}
                onChange={(e) => {
                  if (yearControl.isPlaying) {
                    setYearControl(prev => ({ ...prev, isPlaying: false }));
                  }
                  
                  const value = e.target.value;
                  if (value === '' || value.match(/^\d{0,4}$/)) {
                    setYearInput(value);
                    
                    if (value.match(/^\d{4}$/) && years.includes(value)) {
                      const yearIndex = years.indexOf(value);
                      
                      setYearControl(prev => ({
                        ...prev,
                        progress: yearIndex,
                        selectedYear: value
                      }));

                      if (selectedSpeciesKey) {
                        fetchOccurrences(selectedSpeciesKey, value);
                      }
                    }
                  }
                }}
                onBlur={() => {
                  // Only reset if the input is invalid
                  if (!yearInput.match(/^\d{4}$/) || !years.includes(yearInput)) {
                    const currentYear = years[Math.floor(yearControl.progress)];
                    setYearInput(currentYear);
                  }
                  setIsManuallyEditing(false);
                }}
                sx={{ width: 100 }}
                InputProps={{
                  sx: { 
                    backgroundColor: 'white',
                    '& input': {
                      textAlign: 'center',
                      fontWeight: 'bold',
                      color: '#3892C6'
                    }
                  }
                }}
              />
            </Box>
          </Box>
        </Box>
      </div>
    </div>
  );
};

export default BiodiversityMap; 