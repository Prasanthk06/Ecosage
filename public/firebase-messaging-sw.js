// public/firebase-messaging-sw.js
// Firebase Service Worker for Background Push Notifications

// Import Firebase SDK modules for Service Worker
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.23.0/firebase-messaging-compat.js');

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDHeF6fd21uwzDssqvRXiwprwomQ5YAomQ",
  authDomain: "ecosage-19017.firebaseapp.com",
  projectId: "ecosage-19017",
  storageBucket: "ecosage-19017.firebasestorage.app",
  messagingSenderId: "477953743231",
  appId: "1:477953743231:web:3a1b32c688269cddc3a24a",
  measurementId: "G-EMJEF42JDD"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Get Firebase Messaging instance
const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  console.log('🔔 EcoSage Background Message:', payload);
  
  const { title, body, icon } = payload.notification;
  const notificationData = payload.data || {};
  
  // Customize notification based on type
  let notificationOptions = {
    body: body || 'EcoSage has an update for you!',
    icon: getNotificationIcon(notificationData.type),
    badge: '/icons/badge-icon.png',
    tag: notificationData.type || 'ecosage-general',
    data: notificationData,
    requireInteraction: true,
    vibrate: getVibrationPattern(notificationData.type),
    actions: getNotificationActions(notificationData.type)
  };

  self.registration.showNotification(
    title || 'EcoSage 🌱', 
    notificationOptions
  );
});

// Get appropriate icon based on notification type
function getNotificationIcon(type) {
  switch (type) {
    case 'waste_collection':
      return '/icons/waste-icon.png';
    case 'community_event':
      return '/icons/event-icon.png';
    case 'challenge_nudge':
      return '/icons/challenge-icon.png';
    default:
      return '/icons/icon-192x192.png';
  }
}

// Get vibration pattern based on notification type
function getVibrationPattern(type) {
  switch (type) {
    case 'waste_collection':
      return [200, 100, 200, 100, 200]; // Urgent pattern
    case 'community_event':
      return [100, 50, 100]; // Gentle pattern
    case 'challenge_nudge':
      return [150, 75, 150, 75]; // Motivational pattern
    default:
      return [200, 100, 200];
  }
}

// Get notification actions based on type
function getNotificationActions(type) {
  const baseActions = [
    {
      action: 'view',
      title: '👀 View',
      icon: '/icons/view-icon.png'
    },
    {
      action: 'dismiss',
      title: '❌ Dismiss',
      icon: '/icons/dismiss-icon.png'
    }
  ];

  switch (type) {
    case 'waste_collection':
      return [
        {
          action: 'set_reminder',
          title: '⏰ Set Reminder',
          icon: '/icons/reminder-icon.png'
        },
        ...baseActions
      ];
    case 'community_event':
      return [
        {
          action: 'join_event',
          title: '✅ Join Event',
          icon: '/icons/join-icon.png'
        },
        ...baseActions
      ];
    case 'challenge_nudge':
      return [
        {
          action: 'accept_challenge',
          title: '💪 Accept Challenge',
          icon: '/icons/challenge-icon.png'
        },
        ...baseActions
      ];
    default:
      return baseActions;
  }
}

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('🖱️ Notification clicked:', event);
  
  event.notification.close();
  
  const { action, notification } = event;
  const notificationData = notification.data || {};
  
  // Handle different actions
  if (action === 'dismiss') {
    return; // Just close the notification
  }
  
  // Determine target URL based on notification type and action
  let targetUrl = '/';
  
  switch (notificationData.type) {
    case 'waste_collection':
      targetUrl = action === 'set_reminder' ? '/events?reminder=true' : '/events';
      break;
    case 'community_event':
      targetUrl = action === 'join_event' ? `/events?join=${notificationData.eventId}` : '/events';
      break;
    case 'challenge_nudge':
      targetUrl = action === 'accept_challenge' ? `/challenges?accept=${notificationData.challengeId}` : '/challenges';
      break;
    default:
      targetUrl = '/events';
  }
  
  // Open the app
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((windowClients) => {
        // Check if app is already open
        for (let client of windowClients) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.focus();
            client.postMessage({
              type: 'NOTIFICATION_CLICK',
              action: action,
              data: notificationData,
              targetUrl: targetUrl
            });
            return;
          }
        }
        
        // Open new window if app is not open
        if (clients.openWindow) {
          return clients.openWindow(targetUrl);
        }
      })
  );
});

// Handle push subscription changes
self.addEventListener('pushsubscriptionchange', (event) => {
  console.log('🔄 Push subscription changed:', event);
  
  event.waitUntil(
    // Handle subscription renewal/updates here
    self.registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: 'YOUR_VAPID_KEY_HERE' // Add your VAPID key
    }).then((newSubscription) => {
      // Send new subscription to your backend
      return fetch('/api/update-push-subscription', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newSubscription)
      });
    })
  );
});