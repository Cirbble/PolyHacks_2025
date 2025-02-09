import { useState } from 'react';
import { Autocomplete, TextField, Button, Box, Typography, Paper } from '@mui/material';
import axios from 'axios';

interface PredictionParams {
  species_name: string;
  n_steps: number;
  prediction_amount: number;
}

interface PredictionResponse {
  success: boolean;
  plot?: string;
  error?: string;
}

const DataPage = () => {
  const [selectedSpecies, setSelectedSpecies] = useState<string | null>(null);
  const [nSteps, setNSteps] = useState<string>('');
  const [predictionAmount, setPredictionAmount] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [plotData, setPlotData] = useState<string | null>(null);

  // For now, just one species
  const speciesList = ['Disporella hispida'];

  const handleSubmit = async () => {
    if (!selectedSpecies || !nSteps || !predictionAmount) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError(null);
    setPlotData(null);

    try {
      const params: PredictionParams = {
        species_name: selectedSpecies,
        n_steps: parseInt(nSteps),
        prediction_amount: parseInt(predictionAmount)
      };

      const response = await axios.post<PredictionResponse>('http://localhost:5000/predict', params);
      
      if (response.data.success && response.data.plot) {
        setPlotData(response.data.plot);
      } else {
        setError('Failed to generate prediction');
      }
      
    } catch (err) {
      console.error('Prediction error:', err);
      setError('Failed to get prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box 
      sx={{
        width: '100%',
        minHeight: '100vh',
        backgroundColor: '#935341',
        paddingTop: '90px',
        paddingBottom: '2rem',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        margin: 0,
        padding: 0,
        boxSizing: 'border-box',
        position: 'relative',
        overflowY: 'auto',
      }}
    >
      <Box
        sx={{
          width: '100%',
          maxWidth: '800px',
          mx: 'auto',
          px: { xs: 2, sm: 3 },
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 4,
          position: 'relative',
          zIndex: 1
        }}
      >
        <Typography 
          variant="h2" 
          component="h1" 
          sx={{
            color: '#F5F3CD',
            fontWeight: 600,
            textAlign: 'center',
            fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' }
          }}
        >
          Species Prediction
        </Typography>
        
        <Paper 
          elevation={3} 
          sx={{ 
            width: '100%',
            maxWidth: '500px',
            backgroundColor: '#68392E',
            p: { xs: 3, sm: 4 },
            borderRadius: 2
          }}
        >
          <Box sx={{ 
            display: 'flex',
            flexDirection: 'column',
            gap: 3
          }}>
            <Autocomplete
              value={selectedSpecies}
              onChange={(_, newValue) => setSelectedSpecies(newValue)}
              options={speciesList}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Species"
                  variant="filled"
                  sx={{
                    backgroundColor: '#F5F3CD',
                    borderRadius: '4px',
                    '& .MuiFilledInput-root': {
                      backgroundColor: '#F5F3CD',
                      '&:hover': {
                        backgroundColor: '#F5F3CD',
                      },
                      '&.Mui-focused': {
                        backgroundColor: '#F5F3CD',
                      }
                    },
                    '& .MuiInputLabel-root': {
                      color: '#68392E',
                      '&.Mui-focused': {
                        color: '#68392E'
                      }
                    },
                    '& .MuiFormLabel-filled': {
                      transform: 'translate(12px, 6px) scale(0.75)'
                    }
                  }}
                />
              )}
            />

            <TextField
              label="Number of Steps"
              value={nSteps}
              onChange={(e) => setNSteps(e.target.value)}
              type="number"
              variant="filled"
              helperText="Enter a value between 1 and 12"
              autoComplete="off"
              sx={{
                backgroundColor: '#F5F3CD',
                borderRadius: '4px',
                '& .MuiFilledInput-root': {
                  backgroundColor: '#F5F3CD',
                  '&:hover': {
                    backgroundColor: '#F5F3CD',
                  },
                  '&.Mui-focused': {
                    backgroundColor: '#F5F3CD',
                  }
                },
                '& .MuiInputLabel-root': {
                  color: '#68392E',
                  '&.Mui-focused': {
                    color: '#68392E'
                  }
                },
                '& .MuiFormLabel-filled': {
                  transform: 'translate(12px, 6px) scale(0.75)'
                },
                '& .MuiFormHelperText-root': {
                  color: '#68392E'
                }
              }}
            />

            <TextField
              label="Prediction Amount (Seasons)"
              value={predictionAmount}
              onChange={(e) => setPredictionAmount(e.target.value)}
              type="number"
              variant="filled"
              helperText="Enter a value between 1 and 20"
              autoComplete="off"
              sx={{
                backgroundColor: '#F5F3CD',
                borderRadius: '4px',
                '& .MuiFilledInput-root': {
                  backgroundColor: '#F5F3CD',
                  '&:hover': {
                    backgroundColor: '#F5F3CD',
                  },
                  '&.Mui-focused': {
                    backgroundColor: '#F5F3CD',
                  }
                },
                '& .MuiInputLabel-root': {
                  color: '#68392E',
                  '&.Mui-focused': {
                    color: '#68392E'
                  }
                },
                '& .MuiFormLabel-filled': {
                  transform: 'translate(12px, 6px) scale(0.75)'
                },
                '& .MuiFormHelperText-root': {
                  color: '#68392E'
                }
              }}
            />

            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={loading}
              sx={{
                py: 1.5,
                backgroundColor: '#3892C6',
                borderRadius: '8px',
                fontSize: '1.1rem',
                fontWeight: 600,
                textTransform: 'none',
                '&:hover': {
                  backgroundColor: '#2d7aa6'
                },
                '&:disabled': {
                  backgroundColor: '#68392E',
                  color: '#F5F3CD'
                }
              }}
            >
              {loading ? 'Generating Prediction...' : 'Generate Prediction'}
            </Button>

            {error && (
              <Typography 
                sx={{ 
                  color: '#ff6b6b',
                  textAlign: 'center',
                  fontWeight: 500,
                  mt: 1
                }}
              >
                {error}
              </Typography>
            )}
          </Box>
        </Paper>

        <Paper 
          elevation={3} 
          sx={{ 
            width: '100%',
            backgroundColor: '#68392E',
            p: { xs: 3, sm: 4 },
            borderRadius: 2,
            minHeight: '400px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '2rem',
            overflow: 'hidden',
            position: 'relative'
          }}
        >
          {plotData ? (
            <img 
              src={`data:image/png;base64,${plotData}`}
              alt="Prediction Plot"
              style={{
                maxWidth: '100%',
                height: 'auto',
                borderRadius: '4px'
              }}
            />
          ) : (
            <Box sx={{ 
              position: 'relative',
              width: '100%',
              textAlign: 'center'
            }}>
              <Typography sx={{ 
                color: '#F5F3CD',
                textAlign: 'center',
                fontSize: '1.1rem',
                padding: '1rem',
                width: '100%'
              }}>
                {loading ? '' : 'Prediction results will appear here'}
              </Typography>
            </Box>
          )}
        </Paper>
      </Box>
    </Box>
  );
};

export default DataPage; 