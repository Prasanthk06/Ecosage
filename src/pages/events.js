import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Container,
  Paper,
  Button,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar,
  Grid,
  Chip,
  Card,
  CardContent,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
} from '@mui/material';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import { requestNotificationPermission, setupForegroundMessaging } from '../../lib/firebase';

export default function Events() {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);
  const [notificationPermission, setNotificationPermission] = useState('default');
  const [showNotificationSnack, setShowNotificationSnack] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [reminderDialog, setReminderDialog] = useState(false);
  const [reminderType, setReminderType] = useState('waste_collection');
  const [reminderTime, setReminderTime] = useState('19:00');

  // Initialize notifications on component mount
  useEffect(() => {
    initializeNotifications();
    setupNotificationListeners();
    
    // Check local reminders every minute
    const reminderInterval = setInterval(() => {
      checkLocalReminders();
    }, 60000);

    return () => {
      clearInterval(reminderInterval);
    };
  }, []);

  // Fetch events from backend API
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/events');
        
        if (!response.ok) {
          throw new Error('Failed to fetch events');
        }
        
        const data = await response.json();
        
        if (data.success) {
          // Transform backend events to frontend format
          const transformedEvents = data.events.map(event => ({
            id: event.id.toString(),
            title: event.title,
            date: event.date.split('T')[0], // Extract date part
            time: new Date(event.date).toLocaleTimeString('en-US', { 
              hour: '2-digit', 
              minute: '2-digit' 
            }),
            location: event.location || 'TBA',
            description: event.description || '',
            category: 'Community Action', // Default category
            attendees: event.participants || 0,
            organizer: event.organizer
          }));
          
          setEvents(transformedEvents);
        } else {
          throw new Error(data.error || 'Failed to load events');
        }
      } catch (error) {
        console.error('Failed to fetch events:', error);
        
        // Fallback to mock events if API fails
        const currentDate = new Date();
        const currentYear = currentDate.getFullYear();
        const currentMonth = currentDate.getMonth();
        
        const mockEvents = [
          {
            id: '1',
            title: 'Community Tree Planting',
            date: new Date(currentYear, currentMonth, 5).toISOString().split('T')[0],
            time: '09:00 AM',
            location: 'Central Park',
            description: 'Join us for a community tree planting event to help green our neighborhood.',
            category: 'Community Action',
            attendees: 45,
          },
          {
            id: '2',
            title: 'Beach Cleanup Drive',
            date: new Date(currentYear, currentMonth, 18).toISOString().split('T')[0],
            time: '07:00 AM',
            location: 'Sunset Beach',
            description: 'Help us clean up the beach and protect marine life from plastic pollution.',
            category: 'Environmental',
            attendees: 67,
          },
          {
            id: '3',
            title: 'Renewable Energy Workshop (API Demo)',
            date: new Date(currentYear, currentMonth, 25).toISOString().split('T')[0],
            time: '11:00 AM',
            location: 'Community Center',
            description: 'Backend API connection failed - showing demo events.',
            category: 'Demo',
            attendees: 0,
          }
        ];
        
        setEvents(mockEvents);
      }
    };

    fetchEvents();
  }, []);

  // Initialize notification service
  const initializeNotifications = async () => {
    if (!('Notification' in window)) {
      console.log('Push notifications not supported');
      return;
    }

    // Check current permission status
    setNotificationPermission(Notification.permission);
    setNotificationsEnabled(Notification.permission === 'granted');

    // Setup Firebase foreground messaging
    setupForegroundMessaging((payload) => {
      const { title, body } = payload.notification || {};
      showInAppNotification({
        title: title || 'EcoSage Notification',
        body: body || 'You have a new notification',
        data: payload.data || {}
      });
    });
  };

  // Setup Firebase messaging (removed - now handled in firebase.js)
  const setupFirebaseMessaging = async () => {
    try {
      const token = await requestNotificationPermission();
      if (token) {
        console.log('✅ Firebase notifications setup complete');
      }
    } catch (error) {
      console.error('❌ Firebase setup failed:', error);
    }
  };

  // Setup notification event listeners
  const setupNotificationListeners = () => {
    // Listen for custom in-app notifications
    window.addEventListener('ecosage-notification', (event) => {
      const { title, body } = event.detail;
      setNotificationMessage(`${title}: ${body}`);
      setShowNotificationSnack(true);
    });
  };

  // Check for scheduled local reminders
  const checkLocalReminders = () => {
    const now = new Date();
    const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    
    // Get stored reminders from localStorage
    const reminders = JSON.parse(localStorage.getItem('ecosage-reminders') || '[]');
    
    reminders.forEach((reminder) => {
      if (reminder.time === currentTime && reminder.date === now.toISOString().split('T')[0]) {
        showInAppNotification({
          title: `🗑️ ${reminder.type} Reminder`,
          body: reminder.message,
          data: { type: 'waste_collection' }
        });
        
        // Remove triggered reminder
        const updatedReminders = reminders.filter(r => r.id !== reminder.id);
        localStorage.setItem('ecosage-reminders', JSON.stringify(updatedReminders));
      }
    });
  };

  // Show in-app notification
  const showInAppNotification = ({ title, body, data }) => {
    // Show browser notification if permitted
    if (notificationsEnabled && Notification.permission === 'granted') {
      new Notification(title, {
        body,
        icon: '/favicon.ico',
        data
      });
    }

    // Always show in-app notification
    setNotificationMessage(`${title}: ${body}`);
    setShowNotificationSnack(true);
  };

  // Handle notification permission toggle
  const handleNotificationToggle = async (event) => {
    const enabled = event.target.checked;
    
    if (enabled) {
      const token = await requestNotificationPermission();
      setNotificationsEnabled(!!token);
      setNotificationPermission(token ? 'granted' : 'denied');
      
      if (token) {
        // Send welcome notification
        setTimeout(() => {
          showInAppNotification({
            title: '🌱 Notifications Enabled!',
            body: 'You\'ll now receive eco-friendly reminders and event updates via push notifications and email!',
            data: { type: 'welcome' }
          });
        }, 1000);

        // Also send email notification
        sendEmailNotification({
          type: 'welcome',
          title: 'EcoSage Notifications Enabled!',
          message: 'You will now receive eco-friendly reminders via email and push notifications.'
        });
      }
    } else {
      setNotificationsEnabled(false);
      // Note: Can't revoke permission programmatically, user must do it manually
    }
  };

  // Send email notification via backend
  const sendEmailNotification = async (notificationData) => {
    try {
      const response = await fetch('http://localhost:5000/api/send-email-notification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...notificationData,
          userEmail: getUserEmail(),
          timestamp: new Date().toISOString()
        })
      });

      if (response.ok) {
        console.log('✅ Email notification sent');
      } else {
        console.error('❌ Failed to send email notification');
      }
    } catch (error) {
      console.error('❌ Email notification error:', error);
    }
  };

  // Get user email (you can modify this based on your auth system)
  const getUserEmail = () => {
    // For now, prompt user or get from localStorage
    let email = localStorage.getItem('ecosage-user-email');
    if (!email) {
      email = prompt('Please enter your Gmail address for notifications:');
      if (email) {
        localStorage.setItem('ecosage-user-email', email);
      }
    }
    return email || 'user@gmail.com';
  };

  // Schedule waste collection reminder
  const scheduleWasteReminder = (wasteType, date) => {
    if (!notificationsEnabled) {
      alert('Please enable notifications first!');
      return;
    }

    const reminders = JSON.parse(localStorage.getItem('ecosage-reminders') || '[]');
    const newReminder = {
      id: Date.now(),
      type: wasteType,
      date,
      time: reminderTime,
      message: `Don't forget to put out your ${wasteType.toLowerCase()} bins tonight!`
    };

    reminders.push(newReminder);
    localStorage.setItem('ecosage-reminders', JSON.stringify(reminders));

    // Send email notification
    sendEmailNotification({
      type: 'waste_collection',
      title: `🗑️ ${wasteType} Collection Reminder Set`,
      message: `Reminder set for ${wasteType} collection on ${date} at ${reminderTime}. You'll receive an email reminder.`,
      wasteType,
      date,
      time: reminderTime
    });

    setNotificationMessage(`📅 Reminder set for ${wasteType} collection! Email notification will be sent.`);
    setShowNotificationSnack(true);
  };

  // Trigger daily challenge nudge
  const triggerChallenge = (challengeType = 'plastic_free') => {
    if (!notificationsEnabled) {
      alert('Please enable notifications first!');
      return;
    }

    const challenges = {
      plastic_free: 'Today is your plastic-free day! 🚫🥤 Choose reusable alternatives.',
      energy_saver: 'Energy Saving Challenge! 💡 Unplug devices when not in use.',
      bike_day: 'Bike to Work Day! 🚴‍♀️ Leave the car at home today.',
      zero_waste: 'Zero Waste Challenge! 🌱 Try to produce no waste today.',
      water_saver: 'Water Conservation Day! 💧 Take shorter showers and fix leaks.'
    };

    const challengeMessage = challenges[challengeType] || challenges.plastic_free;

    showInAppNotification({
      title: '💪 Daily Challenge!',
      body: challengeMessage,
      data: { type: 'challenge', challengeType }
    });

    // Send email notification for challenge
    sendEmailNotification({
      type: 'challenge_nudge',
      title: `💪 EcoSage Daily Challenge: ${challengeType.replace('_', ' ').toUpperCase()}`,
      message: challengeMessage,
      challengeType
    });
  };

  // Send community event reminder
  const sendEventReminder = (event) => {
    if (!notificationsEnabled) {
      alert('Please enable notifications first!');
      return;
    }

    const eventDate = new Date(event.date);
    const now = new Date();
    const timeDiff = eventDate.getTime() - now.getTime();
    const hoursUntil = Math.ceil(timeDiff / (1000 * 3600));

    if (hoursUntil > 0 && hoursUntil <= 24) {
      showInAppNotification({
        title: `🎉 ${event.title} Starting Soon!`,
        body: `Join us at ${event.location} in ${hoursUntil} hour${hoursUntil > 1 ? 's' : ''}!`,
        data: {
          type: 'community_event',
          eventId: event.id,
          eventName: event.title,
          location: event.location,
          timeUntil: `${hoursUntil} hour${hoursUntil > 1 ? 's' : ''}`
        }
      });
    } else {
      setNotificationMessage('📅 Event reminder will be sent closer to the event time!');
      setShowNotificationSnack(true);
    }
  };

  const handleEventClick = (eventInfo) => {
    const event = events.find(e => e.id === eventInfo.event.id);
    setSelectedEvent(event);
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Community Action': 'success',
      'Education': 'primary',
      'Environmental': 'secondary',
      'Activism': 'warning',
      'Recreation': 'info',
    };
    return colors[category] || 'default';
  };

  const calendarEvents = events.map(event => ({
    id: event.id,
    title: event.title,
    date: event.date,
    backgroundColor: getCategoryColor(event.category) === 'primary' ? '#1976d2' :
                    getCategoryColor(event.category) === 'success' ? '#2e7d32' :
                    getCategoryColor(event.category) === 'secondary' ? '#9c27b0' :
                    getCategoryColor(event.category) === 'warning' ? '#ed6c02' :
                    getCategoryColor(event.category) === 'info' ? '#0288d1' : '#757575',
  }));

  return (
    <Container maxWidth="lg">
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h1" sx={{ fontSize: 60, color: 'primary.main', mb: 2 }}>
          📅
        </Typography>
        <Typography variant="h3" component="h1" gutterBottom>
          Eco Events Calendar
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Discover environmental events with smart push notifications
        </Typography>
      </Box>

      {/* Notification Controls */}
      <Paper elevation={2} sx={{ p: 3, mb: 4, bgcolor: 'primary.light', color: 'white' }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Typography variant="h1" sx={{ fontSize: 30 }}>
                🔔
              </Typography>
              <Box>
                <Typography variant="h6">Push Notifications</Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Get reminders for waste collection, events, and daily challenges
                </Typography>
              </Box>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, flexWrap: 'wrap' }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={notificationsEnabled}
                    onChange={handleNotificationToggle}
                    color="secondary"
                  />
                }
                label="Enable Notifications"
                sx={{ color: 'white' }}
              />
              
              {notificationsEnabled && (
                <>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => setReminderDialog(true)}
                    sx={{ color: 'white', borderColor: 'white' }}
                  >
                    Set Reminder
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => triggerChallenge()}
                    sx={{ color: 'white', borderColor: 'white' }}
                  >
                    Daily Challenge
                  </Button>
                </>
              )}
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Notification Status Alert */}
      {notificationPermission === 'denied' && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="body2">
            🔕 Notifications are blocked. Enable them in your browser settings to receive eco-friendly reminders!
          </Typography>
        </Alert>
      )}

      <Grid container spacing={4}>
        {/* Calendar Section */}
        <Grid item xs={12} lg={8}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Event Calendar
            </Typography>
            
            <Box sx={{ '& .fc': { height: '500px' } }}>
              <FullCalendar
                plugins={[dayGridPlugin]}
                initialView="dayGridMonth"
                events={calendarEvents}
                eventClick={handleEventClick}
                headerToolbar={{
                  left: 'prev,next today',
                  center: 'title',
                  right: 'dayGridMonth'
                }}
                eventDisplay="block"
                eventTextColor="white"
                eventBorderColor="transparent"
                height="500px"
              />
            </Box>
          </Paper>
        </Grid>

        {/* Event Details Section */}
        <Grid item xs={12} lg={4}>
          <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h5" gutterBottom>
              Event Details
            </Typography>

            {!selectedEvent ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h1" sx={{ fontSize: 60, color: 'text.disabled', mb: 2 }}>
                  📅
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Click on a calendar event to see details here
                </Typography>
              </Box>
            ) : (
              <Card elevation={0} sx={{ border: 1, borderColor: 'divider' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {selectedEvent.title}
                  </Typography>

                  <Box sx={{ mb: 2 }}>
                    <Chip
                      label={selectedEvent.category}
                      color={getCategoryColor(selectedEvent.category)}
                      size="small"
                    />
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <span style={{ fontSize: 16, marginRight: 8, color: '#757575' }}>⏰</span>
                    <Typography variant="body2" color="text.secondary">
                      {new Date(selectedEvent.date).toLocaleDateString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })} at {selectedEvent.time}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <span style={{ fontSize: 16, marginRight: 8, color: '#757575' }}>📍</span>
                    <Typography variant="body2" color="text.secondary">
                      {selectedEvent.location}
                    </Typography>
                  </Box>

                  <Typography variant="body2" paragraph>
                    {selectedEvent.description}
                  </Typography>

                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Typography variant="caption" color="text.secondary">
                      {selectedEvent.attendees} people attending
                    </Typography>
                    <Chip
                      label={`${selectedEvent.attendees} attendees`}
                      size="small"
                      variant="outlined"
                      color="primary"
                    />
                  </Box>

                  {/* Notification Actions */}
                  {notificationsEnabled && (
                    <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => sendEventReminder(selectedEvent)}
                        startIcon={<span>🔔</span>}
                      >
                        Notify Me
                      </Button>
                      
                      {selectedEvent.category === 'Community Action' && (
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => scheduleWasteReminder('General', selectedEvent.date)}
                          startIcon={<span>🗑️</span>}
                        >
                          Waste Reminder
                        </Button>
                      )}
                    </Box>
                  )}
                </CardContent>
              </Card>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Upcoming Events List */}
      <Paper elevation={3} sx={{ mt: 4, p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Upcoming Events
        </Typography>
        
        <Grid container spacing={2}>
          {events
            .sort((a, b) => new Date(a.date) - new Date(b.date))
            .slice(0, 6)
            .map((event) => (
              <Grid item xs={12} md={6} key={event.id}>
                <Card
                  sx={{
                    cursor: 'pointer',
                    transition: 'transform 0.2s ease-in-out',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: 2,
                    },
                  }}
                  onClick={() => setSelectedEvent(event)}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Typography variant="h6" component="h3">
                        {event.title}
                      </Typography>
                      <Chip
                        label={event.category}
                        color={getCategoryColor(event.category)}
                        size="small"
                      />
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <span style={{ fontSize: 14, marginRight: 4, color: '#757575' }}>⏰</span>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(event.date).toLocaleDateString()} • {event.time}
                      </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <span style={{ fontSize: 14, marginRight: 4, color: '#757575' }}>📍</span>
                      <Typography variant="caption" color="text.secondary">
                        {event.location}
                      </Typography>
                    </Box>

                    <Typography variant="body2" color="text.secondary">
                      {event.description.length > 80 
                        ? `${event.description.substring(0, 80)}...` 
                        : event.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
        </Grid>
      </Paper>

      {/* Floating Action Buttons for Quick Actions */}
      {notificationsEnabled && (
        <>
          <Fab
            color="primary"
            sx={{ position: 'fixed', bottom: 80, right: 20 }}
            onClick={() => triggerChallenge('plastic_free')}
            title="Trigger Plastic-Free Challenge"
          >
            <span style={{ fontSize: 24 }}>🚫</span>
          </Fab>
          
          <Fab
            color="secondary"
            sx={{ position: 'fixed', bottom: 20, right: 20 }}
            onClick={() => triggerChallenge('energy_saver')}
            title="Trigger Energy Saving Challenge"
          >
            <span style={{ fontSize: 24 }}>💡</span>
          </Fab>
        </>
      )}

      {/* Reminder Setup Dialog */}
      <Dialog open={reminderDialog} onClose={() => setReminderDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <span style={{ fontSize: 24 }}>⏰</span>
            Set Eco Reminder
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                select
                fullWidth
                label="Reminder Type"
                value={reminderType}
                onChange={(e) => setReminderType(e.target.value)}
              >
                <MenuItem value="waste_collection">🗑️ Waste Collection</MenuItem>
                <MenuItem value="recycling">♻️ Recycling Day</MenuItem>
                <MenuItem value="composting">🌱 Composting</MenuItem>
                <MenuItem value="energy_check">💡 Energy Usage Check</MenuItem>
              </TextField>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Reminder Time"
                type="time"
                value={reminderTime}
                onChange={(e) => setReminderTime(e.target.value)}
                InputLabelProps={{ shrink: true }}
                helperText="Time to receive daily reminder"
              />
            </Grid>
          </Grid>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setReminderDialog(false)}>
            Cancel
          </Button>
          <Button 
            onClick={() => {
              const tomorrow = new Date();
              tomorrow.setDate(tomorrow.getDate() + 1);
              const dateStr = tomorrow.toISOString().split('T')[0];
              
              scheduleWasteReminder(
                reminderType.charAt(0).toUpperCase() + reminderType.slice(1),
                dateStr
              );
              setReminderDialog(false);
            }}
            variant="contained"
          >
            Set Reminder
          </Button>
        </DialogActions>
      </Dialog>

      {/* Notification Snackbar */}
      <Snackbar
        open={showNotificationSnack}
        autoHideDuration={4000}
        onClose={() => setShowNotificationSnack(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setShowNotificationSnack(false)} 
          severity="info"
          variant="filled"
        >
          {notificationMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
}