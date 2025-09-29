import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  Paper,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material';
// import { Calculate, Eco } from '@mui/icons-material';

export default function Calculator() {
  const [formData, setFormData] = useState({
    electricity: '',
    transportation: '',
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    setError('');
  };

  const handleCalculate = async () => {
    // Validation
    if (!formData.electricity || !formData.transportation) {
      setError('Please fill in all fields');
      return;
    }

    if (isNaN(formData.electricity) || isNaN(formData.transportation)) {
      setError('Please enter valid numbers');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Real API call to backend
      const response = await fetch('http://localhost:5000/api/calculate_carbon', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
        electricity_kwh: parseFloat(formData.electricity),
        transportation_miles: parseFloat(formData.transportation)
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to calculate carbon footprint');
      }
      
      const data = await response.json();
      
      if (data.success) {
        setResult({
          electricity: data.electricity_carbon?.toFixed(2) || '0.00',
          transportation: data.transportation_carbon?.toFixed(2) || '0.00',
          total: data.total_carbon.toFixed(2),
          comparison: data.impact_level === 'low' ? 'below average' : data.impact_level === 'medium' ? 'average' : 'above average',
          recommendations: data.recommendations
        });
      } else {
        throw new Error(data.error || 'Calculation failed');
      }
    } catch (error) {
      console.error('API Error:', error);
      setError('Failed to calculate carbon footprint. Please try again.');
      
      // Fallback to mock calculation if API fails
      const electricity = parseFloat(formData.electricity);
      const transportation = parseFloat(formData.transportation);
      
      const electricityCarbon = electricity * 0.708; // Match backend factor
      const transportationCarbon = (transportation * 1.60934) * 0.192;; // Match backend factor (car miles)
      const totalCarbon = electricityCarbon + transportationCarbon;

      setResult({
        electricity: electricityCarbon.toFixed(2),
        transportation: transportationCarbon.toFixed(2),
        total: totalCarbon.toFixed(2),
        comparison: totalCarbon < 150 ? 'below average' : totalCarbon < 300 ? 'average' : 'above average',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({ electricity: '', transportation: '' });
    setResult(null);
    setError('');
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h1" sx={{ fontSize: 60, color: 'primary.main', mb: 2 }}>
          🧮
        </Typography>
        <Typography variant="h3" component="h1" gutterBottom>
          Carbon Footprint Calculator
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Calculate your environmental impact and discover ways to reduce your carbon footprint
        </Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 4 }}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h5" gutterBottom>
              Monthly Usage Information
            </Typography>
            <Divider sx={{ mb: 3 }} />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              name="electricity"
              label="Electricity Usage (kWh)"
              value={formData.electricity}
              onChange={handleInputChange}
              type="number"
              placeholder="e.g., 350"
              helperText="Average monthly electricity consumption"
              variant="outlined"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              name="transportation"
              label="Transportation (miles)"
              value={formData.transportation}
              onChange={handleInputChange}
              type="number"
              placeholder="e.g., 1200"
              helperText="Average monthly miles traveled"
              variant="outlined"
            />
          </Grid>

          {error && (
            <Grid item xs={12}>
              <Alert severity="error">{error}</Alert>
            </Grid>
          )}

          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleCalculate}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <span>🧮</span>}
              >
                {loading ? 'Calculating...' : 'Calculate Footprint'}
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={handleReset}
                disabled={loading}
              >
                Reset
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {result && (
        <Paper elevation={3} sx={{ mt: 4, p: 4, bgcolor: 'background.paper' }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Typography variant="h1" sx={{ fontSize: 40, color: 'success.main' }}>
              🌱
            </Typography>
            <Typography variant="h5" gutterBottom>
              Your Carbon Footprint Results
            </Typography>
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.light', color: 'white' }}>
                <Typography variant="h6">Electricity</Typography>
                <Typography variant="h4">{result.electricity}</Typography>
                <Typography variant="body2">kg CO₂/month</Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'secondary.light', color: 'white' }}>
                <Typography variant="h6">Transportation</Typography>
                <Typography variant="h4">{result.transportation}</Typography>
                <Typography variant="body2">kg CO₂/month</Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.main', color: 'white' }}>
                <Typography variant="h6">Total</Typography>
                <Typography variant="h4">{result.total}</Typography>
                <Typography variant="body2">kg CO₂/month</Typography>
              </Paper>
            </Grid>

            <Grid item xs={12}>
              <Alert 
                severity={result.comparison === 'below average' ? 'success' : result.comparison === 'average' ? 'info' : 'warning'}
                sx={{ mt: 2 }}
              >
                Your carbon footprint is <strong>{result.comparison}</strong> compared to similar households.
                {result.comparison !== 'below average' && ' Consider reducing energy consumption and using sustainable transportation options.'}
              </Alert>
            </Grid>
          </Grid>
        </Paper>
      )}
    </Container>
  );
}