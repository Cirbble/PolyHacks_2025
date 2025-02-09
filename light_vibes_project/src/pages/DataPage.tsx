import { useState } from 'react';
import { Autocomplete, TextField, Button, Box, Typography, Paper } from '@mui/material';
import axios from 'axios';
import { keyframes } from '@emotion/react';

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

const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const shimmer = keyframes`
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
`;

const float = keyframes`
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0px);
  }
`;

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
        width: '100vw',
        minHeight: '100vh',
        paddingTop: '64px',
        backgroundColor: '#935341',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        overflow: 'hidden',
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.1) 0%, rgba(0, 0, 0, 0.1) 100%)',
          pointerEvents: 'none'
        }
      }}
    >
      <Typography
        variant="h2"
        sx={{
          color: '#F5F3CD',
          textAlign: 'center',
          fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' },
          fontWeight: 'bold',
          mb: 4,
          mt: 3,
          textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
          animation: `${float} 3s ease-in-out infinite`,
          position: 'relative',
          '&::after': {
            content: '""',
            position: 'absolute',
            bottom: '-10px',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '60%',
            height: '2px',
            background: 'linear-gradient(90deg, transparent, #F5F3CD, transparent)',
            opacity: 0.6
          }
        }}
      >
        Species Prediction
      </Typography>

      <Box
        sx={{
          width: '100%',
          maxWidth: '800px',
          height: '100%',
          overflowY: 'auto',
          px: { xs: 2, sm: 3 },
          pb: '2rem',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 4,
          margin: '0 auto',
          '&::-webkit-scrollbar': { display: 'none' },
          msOverflowStyle: 'none',
          scrollbarWidth: 'none',
        }}
      >
        <Paper 
          elevation={3} 
          sx={{ 
            width: '100%',
            backgroundColor: 'rgba(104, 57, 46, 0.9)',
            backdropFilter: 'blur(10px)',
            p: { xs: 3, sm: 4 },
            borderRadius: 2,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            animation: `${fadeIn} 0.8s ease-out`,
            transition: 'transform 0.3s ease, box-shadow 0.3s ease',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 12px 48px rgba(0, 0, 0, 0.2)'
            }
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
                transition: 'all 0.3s ease',
                position: 'relative',
                overflow: 'hidden',
                '&::after': loading ? {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '200%',
                  height: '100%',
                  background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
                  animation: `${shimmer} 1.5s infinite linear`
                } : {},
                transform: 'scale(1)',
                '&:hover': {
                  transform: 'scale(1.02)',
                  backgroundColor: '#2d7aa6'
                },
                '&:active': {
                  transform: 'scale(0.98)'
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
            backgroundColor: 'rgba(104, 57, 46, 0.9)',
            backdropFilter: 'blur(10px)',
            p: { xs: 3, sm: 4 },
            borderRadius: 2,
            minHeight: '400px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '2rem',
            overflow: 'hidden',
            position: 'relative',
            animation: `${fadeIn} 0.8s ease-out 0.4s backwards`,
            transition: 'all 0.3s ease',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 12px 48px rgba(0, 0, 0, 0.2)'
            }
          }}
        >
          {plotData ? (
            <img 
              src={`data:image/png;base64,${plotData}`}
              alt="Prediction Plot"
              style={{
                maxWidth: '100%',
                height: 'auto',
                borderRadius: '4px',
                transition: 'transform 0.3s ease',
                animation: `${fadeIn} 0.8s ease-out`
              }}
            />
          ) : (
            <Box sx={{ 
              position: 'relative',
              width: '100%',
              textAlign: 'center',
              background: loading ? 
                'linear-gradient(90deg, #68392E, #7a4437, #68392E)' : 
                'transparent',
              backgroundSize: '1000px 100%',
              animation: loading ? 
                `${shimmer} 2s infinite linear` : 
                `${fadeIn} 0.8s ease-out`
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