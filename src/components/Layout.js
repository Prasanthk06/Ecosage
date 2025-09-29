import React from 'react';
import { AppBar, Toolbar, Typography, Button, Container, Box } from '@mui/material';
import Link from 'next/link';
import { useRouter } from 'next/router';

const Layout = ({ children }) => {
  const router = useRouter();

  const navItems = [
    { label: 'Home', path: '/' },
    { label: 'Classify', path: '/classify' },
    { label: 'Calculator', path: '/calculator' },
    { label: 'Events', path: '/events' },
    { label: 'Trivia', path: '/trivia' },
  ];

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <AppBar position="static">
        <Toolbar>
          <Link href="/" style={{ textDecoration: 'none', color: 'inherit', flexGrow: 1, display: 'flex' }}>
            <Typography variant="h6" component="div" sx={{ cursor: 'pointer' }}>
              EcoSage 🌱
            </Typography>
          </Link>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {navItems.map((item) => (
              <Link key={item.path} href={item.path} style={{ textDecoration: 'none' }}>
                <Button 
                  color="inherit"
                  variant={router.pathname === item.path ? 'outlined' : 'text'}
                  sx={{ 
                    color: 'white',
                    borderColor: router.pathname === item.path ? 'white' : 'transparent'
                  }}
                >
                  {item.label}
                </Button>
              </Link>
            ))}
          </Box>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ flexGrow: 1, py: 4 }}>
        {children}
      </Container>
    </Box>
  );
};

export default Layout;