import React, { useState, useRef } from 'react';
import {
  Box,
  Typography,
  Container,
  Paper,
  Button,
  Grid,
  Card,
  CardMedia,
  CardContent,
  CircularProgress,
  Chip,
  Alert,
} from '@mui/material';
// import { PhotoCamera, CloudUpload, Eco } from '@mui/icons-material';

export default function Classify() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleImageSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type.startsWith('image/')) {
        setSelectedImage(file);
        setError('');
        
        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
          setImagePreview(e.target.result);
        };
        reader.readAsDataURL(file);
        
        // Reset previous results
        setResults(null);
      } else {
        setError('Please select a valid image file');
      }
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleClassify = async () => {
    if (!selectedImage) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Real API call to backend classifier
      const formData = new FormData();
      formData.append('image', selectedImage);

      const response = await fetch('http://localhost:5000/api/classify', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to classify image');
      }

      const data = await response.json();
      
      if (data.success) {
        // Transform backend response to match frontend format
        const transformedResults = [{
          species: data.classification.label,
          confidence: data.classification.confidence,
          category: 'Environmental Element',
          description: data.classification.environmental_impact,
          conservation_status: 'Unknown',
          environmental_impact: data.classification.environmental_impact,
          suggestions: data.classification.suggestions
        }];
        
        setResults(transformedResults);
      } else {
        throw new Error(data.error || 'Classification failed');
      }
    } catch (error) {
      console.error('Classification error:', error);
      setError('Failed to classify image. Showing demo results.');
      
      // Fallback to mock results if API fails
      const mockResults = [
        {
          species: 'Environmental Element',
          confidence: 0.87,
          category: 'Demo Mode',
          description: 'Demo classification result - API connection failed.',
          conservation_status: 'Unknown',
          environmental_impact: 'This is a demo result. Please check backend connection.',
        }
      ];
      
      setResults(mockResults);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setResults(null);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h1" sx={{ fontSize: 60, color: 'primary.main', mb: 2 }}>
          📸
        </Typography>
        <Typography variant="h3" component="h1" gutterBottom>
          AI Image Classification
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Upload images of plants, animals, or environmental elements for instant AI identification
        </Typography>
      </Box>

      <Grid container spacing={4}>
        {/* Upload Section */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h5" gutterBottom>
              Upload Image
            </Typography>
            
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleImageSelect}
              accept="image/*"
              style={{ display: 'none' }}
            />

            <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              {!imagePreview ? (
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h1" sx={{ fontSize: 80, color: 'primary.light', mb: 2 }}>
                    ☁️
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph>
                    Select an image to identify plants, animals, or environmental elements
                  </Typography>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleUploadClick}
                    startIcon={<span>📸</span>}
                  >
                    Choose Image
                  </Button>
                </Box>
              ) : (
                <Box sx={{ width: '100%' }}>
                  <Card>
                    <CardMedia
                      component="img"
                      sx={{ maxHeight: 300, objectFit: 'contain' }}
                      image={imagePreview}
                      alt="Selected image"
                    />
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Typography variant="body2" color="text.secondary">
                        {selectedImage.name}
                      </Typography>
                      <Box sx={{ mt: 2, display: 'flex', gap: 1, justifyContent: 'center' }}>
                        <Button
                          variant="contained"
                          onClick={handleClassify}
                          disabled={loading}
                          startIcon={loading ? <CircularProgress size={20} /> : <span>🌱</span>}
                        >
                          {loading ? 'Classifying...' : 'Classify!'}
                        </Button>
                        <Button variant="outlined" onClick={handleReset}>
                          Reset
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Box>
              )}
            </Box>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Paper>
        </Grid>

        {/* Results Section */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 4, height: '100%' }}>
            <Typography variant="h5" gutterBottom>
              Classification Results
            </Typography>

            {!results && !loading && (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <Typography variant="h1" sx={{ fontSize: 60, color: 'text.disabled', mb: 2 }}>
                  🌱
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Upload and classify an image to see results here
                </Typography>
              </Box>
            )}

            {loading && (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <CircularProgress size={60} sx={{ mb: 2 }} />
                <Typography variant="body1" color="text.secondary">
                  AI is analyzing your image...
                </Typography>
              </Box>
            )}

            {results && (
              <Box sx={{ maxHeight: 500, overflowY: 'auto' }}>
                {results.map((result, index) => (
                  <Paper
                    key={index}
                    elevation={1}
                    sx={{
                      p: 3,
                      mb: 2,
                      border: index === 0 ? 2 : 1,
                      borderColor: index === 0 ? 'primary.main' : 'divider',
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" sx={{ flexGrow: 1 }}>
                        {result.species}
                      </Typography>
                      <Chip
                        label={`${(result.confidence * 100).toFixed(1)}%`}
                        color={getConfidenceColor(result.confidence)}
                        size="small"
                      />
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Chip label={result.category} color="primary" variant="outlined" size="small" />
                      <Chip
                        label={result.conservation_status}
                        color="success"
                        variant="outlined"
                        size="small"
                        sx={{ ml: 1 }}
                      />
                    </Box>

                    <Typography variant="body2" paragraph>
                      {result.description}
                    </Typography>

                    <Typography variant="caption" color="text.secondary">
                      <strong>Environmental Impact:</strong> {result.environmental_impact}
                    </Typography>
                  </Paper>
                ))}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}