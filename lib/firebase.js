// lib/firebase.js
// Firebase configuration and initialization

import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage } from 'firebase/messaging';

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

// VAPID Key for web push notifications
// Note: This is a placeholder - you need to generate your actual VAPID key in Firebase Console
const VAPID_KEY = "BKxQZWtqz4g5L8f2hZ9dXvMnOaQw7eR1yTvGk3JpL4mN8xCvB2sA9dFgH1jK5oI7uY4tE6rW0qS3mL8vP1zXcV2nB";

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Cloud Messaging
let messaging = null;
if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
  messaging = getMessaging(app);
}

// Request notification permission and get token
export const requestNotificationPermission = async () => {
  try {
    if (!messaging) return null;

    // Register service worker
    await navigator.serviceWorker.register('/firebase-messaging-sw.js');
    
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      const token = await getToken(messaging, { vapidKey: VAPID_KEY });
      console.log('🔥 Firebase FCM Token:', token);
      
      // Send token to backend
      await sendTokenToBackend(token);
      
      return token;
    }
    return null;
  } catch (error) {
    console.error('Error getting notification permission:', error);
    return null;
  }
};

// Send FCM token to backend
const sendTokenToBackend = async (token) => {
  try {
    const response = await fetch('http://localhost:5000/api/save-fcm-token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        token,
        userEmail: getUserEmail(), // You'll implement this
        timestamp: new Date().toISOString()
      })
    });
    
    if (response.ok) {
      console.log('✅ FCM token saved to backend');
    }
  } catch (error) {
    console.error('❌ Failed to save FCM token:', error);
  }
};

// Get user email (implement based on your auth system)
const getUserEmail = () => {
  // TODO: Replace with actual user email from your auth system
  return localStorage.getItem('user-email') || 'user@example.com';
};

// Setup foreground message listener
export const setupForegroundMessaging = (callback) => {
  if (!messaging) return;
  
  onMessage(messaging, (payload) => {
    console.log('📨 Foreground message received:', payload);
    
    if (callback) {
      callback(payload);
    }
  });
};

export { messaging, VAPID_KEY };
export default app;