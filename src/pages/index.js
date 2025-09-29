import React from 'react';
import { Box, Typography, Container, Paper, Grid, Card, CardContent } from '@mui/material';
// import { Eco, Calculate, Event, PhotoCamera } from '@mui/icons-material';

export default function Home() {
  const features = [
    {
      icon: <Typography variant="h2" sx={{ color: 'primary.main' }}>📸</Typography>,
      title: 'Image Classification',
      description: 'Upload images of plants, animals, or environmental elements to get instant AI-powered identification and insights.',
    },
    {
      icon: <Typography variant="h2" sx={{ color: 'primary.main' }}>🧮</Typography>,
      title: 'Carbon Calculator',
      description: 'Calculate your carbon footprint with our advanced environmental impact calculator.',
    },
    {
      icon: <Typography variant="h2" sx={{ color: 'primary.main' }}>📅</Typography>,
      title: 'Eco Events',
      description: 'Discover and participate in environmental events, workshops, and community activities near you.',
    },
  ];

  return (
    <Container maxWidth="lg">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          textAlign: 'center',
          py: 8,
        }}
      >
        <Typography variant="h1" sx={{ fontSize: 80, color: 'primary.main', mb: 2 }}>
          🌱
        </Typography>
        <Typography variant="h2" component="h1" gutterBottom>
          Welcome to EcoSage
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph sx={{ maxWidth: 600 }}>
          Your AI-powered environmental companion. Discover, learn, and take action for a sustainable future with intelligent tools and community insights.
        </Typography>
      </Box>

      <Grid container spacing={4} sx={{ mt: 4 }}>
        {features.map((feature, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Card 
              sx={{ 
                height: '100%',
                transition: 'transform 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                },
              }}
            >
              <CardContent sx={{ textAlign: 'center', p: 4 }}>
                <Box sx={{ mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h6" component="h3" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Paper 
        sx={{ 
          mt: 8, 
          p: 4, 
          background: 'linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%)',
          textAlign: 'center'
        }}
      >
        <Typography variant="h4" component="h2" gutterBottom>
          Join the Environmental Revolution
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Together, we can make a difference. Start exploring our tools and become part of the sustainable future.
        </Typography>
      </Paper>
    </Container>
  );
}