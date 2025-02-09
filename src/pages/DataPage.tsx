import { useState } from 'react';
import { 
  Autocomplete, 
  TextField, 
  Button, 
  Box, 
  Typography, 
  CircularProgress,
  Slider,
  Paper
} from '@mui/material';
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
  const [nSteps, setNSteps] = useState<number>(1);
  const [predictionAmount, setPredictionAmount] = useState<number>(4);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [plotData, setPlotData] = useState<string | null>(null);

  // For now, just one species
  const speciesList = ['Disporella hispida'];

  const handleSubmit = async () => {
    if (!selectedSpecies) {
      setError('Please select a species');
      return;
    }

    setLoading(true);
    setError(null);
    setPlotData(null);

    try {
      const params: PredictionParams = {
        species_name: selectedSpecies,
        n_steps: nSteps,
        prediction_amount: predictionAmount
      };

      const response = await axios.post<PredictionResponse>(
        'http://localhost:5000/predict', 
        params
      );
      
      if (response.data.success && response.data.plot) {
        setPlotData(response.data.plot);
      } else {
        setError(response.data.error || 'Failed to generate prediction');
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
        paddingTop: '90px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 4
      }}
    >
      <Typography variant="h4" sx={{ color: '#F5F3CD', mb: 4 }}>
        Species Population Prediction
      </Typography>

      <Paper 
        elevation={3}
        sx={{
          p: 4,
          width: '90%',
          maxWidth: 600,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderRadius: 2
        }}
      >
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <Autocomplete
            value={selectedSpecies}
            onChange={(_, newValue) => setSelectedSpecies(newValue)}
            options={speciesList}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Species"
                variant="outlined"
              />
            )}
          />

          <Box>
            <Typography gutterBottom>
              Number of Steps per Prediction (1-12)
            </Typography>
            <Slider
              value={nSteps}
              onChange={(_, value) => setNSteps(value as number)}
              min={1}
              max={12}
              marks
              valueLabelDisplay="auto"
            />
          </Box>

          <Box>
            <Typography gutterBottom>
              Prediction Amount (Seasons into the Future) (1-20)
            </Typography>
            <Slider
              value={predictionAmount}
              onChange={(_, value) => setPredictionAmount(value as number)}
              min={1}
              max={20}
              marks
              valueLabelDisplay="auto"
            />
          </Box>

          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={loading}
            sx={{
              backgroundColor: '#3892C6',
              '&:hover': {
                backgroundColor: '#2d7aa8'
              }
            }}
          >
            {loading ? <CircularProgress size={24} /> : 'Generate Prediction'}
          </Button>

          {error && (
            <Typography color="error" sx={{ mt: 2 }}>
              {error}
            </Typography>
          )}
        </Box>
      </Paper>

      {plotData && (
        <Paper 
          elevation={3}
          sx={{
            p: 4,
            width: '90%',
            maxWidth: 800,
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            borderRadius: 2,
            mt: 4
          }}
        >
          <img 
            src={`data:image/png;base64,${plotData}`}
            alt="Prediction Plot"
            style={{ width: '100%', height: 'auto' }}
          />
        </Paper>
      )}
    </Box>
  );
};

export default DataPage; 