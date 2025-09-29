// lib/notificationService.js
// EcoSage Push Notification Service

import { messaging } from './firebase';
import { getToken, onMessage } from 'firebase/messaging';

class NotificationService {
  constructor() {
    this.isSupported = this.checkSupport();
    this.permission = null;
    this.token = null;
  }

  // Check if push notifications are supported
  checkSupport() {
    return (
      typeof window !== 'undefined' &&
      'serviceWorker' in navigator &&
      'PushManager' in window &&
      'Notification' in window
    );
  }

  // Request notification permission
  async requestPermission() {
    if (!this.isSupported) {
      console.warn('Push notifications are not supported');
      return false;
    }

    try {
      this.permission = await Notification.requestPermission();
      
      if (this.permission === 'granted') {
        console.log('✅ Notification permission granted');
        await this.getRegistrationToken();
        return true;
      } else {
        console.log('❌ Notification permission denied');
        return false;
      }
    } catch (error) {
      console.error('Error requesting notification permission:', error);
      return false;
    }
  }

  // Get FCM registration token
  async getRegistrationToken() {
    if (!messaging) {
      console.warn('Firebase messaging not available');
      return null;
    }

    try {
      // Register service worker first
      if ('serviceWorker' in navigator) {
        await navigator.serviceWorker.register('/firebase-messaging-sw.js');
      }

      // Get token
      this.token = await getToken(messaging, {
        vapidKey: 'YOUR_VAPID_KEY_HERE' // You'll need to generate this in Firebase Console
      });

      if (this.token) {
        console.log('📱 FCM Token:', this.token);
        
        // Send token to backend for storage
        await this.sendTokenToBackend(this.token);
        
        return this.token;
      } else {
        console.log('❌ No registration token available');
        return null;
      }
    } catch (error) {
      console.error('Error getting registration token:', error);
      return null;
    }
  }

  // Send token to backend
  async sendTokenToBackend(token) {
    try {
      const response = await fetch('http://localhost:5000/api/save-fcm-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          token: token,
          userId: this.getCurrentUserId(), // Implement user identification
          device: this.getDeviceInfo()
        })
      });

      if (response.ok) {
        console.log('✅ FCM token saved to backend');
      } else {
        console.error('❌ Failed to save FCM token');
      }
    } catch (error) {
      console.error('Error sending token to backend:', error);
    }
  }

  // Setup foreground message listener
  setupForegroundListener() {
    if (!messaging) return;

    onMessage(messaging, (payload) => {
      console.log('📨 Foreground message received:', payload);
      
      const { title, body } = payload.notification;
      const notificationData = payload.data || {};

      // Show custom in-app notification
      this.showInAppNotification({
        title,
        body,
        data: notificationData
      });
    });
  }

  // Show custom in-app notification
  showInAppNotification({ title, body, data }) {
    // Create and dispatch custom event for in-app notification
    const event = new CustomEvent('ecosage-notification', {
      detail: { title, body, data }
    });
    
    window.dispatchEvent(event);
  }

  // Schedule local notifications for waste collection reminders
  scheduleWasteCollectionReminder(date, time, wasteType) {
    const reminderData = {
      type: 'waste_collection',
      title: `🗑️ Waste Collection Reminder`,
      body: `${wasteType} collection is tomorrow! Don't forget to put out your bins.`,
      data: {
        type: 'waste_collection',
        wasteType: wasteType,
        collectionDate: date
      }
    };

    // Store reminder in localStorage for client-side scheduling
    this.storeLocalReminder(reminderData, date, time);
  }

  // Schedule challenge nudges
  scheduleChallenge(challengeType, message) {
    const challengeData = {
      type: 'challenge_nudge',
      title: `💚 EcoSage Challenge`,
      body: message,
      data: {
        type: 'challenge_nudge',
        challengeType: challengeType,
        timestamp: Date.now()
      }
    };

    this.showInAppNotification(challengeData);
  }

  // Store local reminder
  storeLocalReminder(reminderData, date, time) {
    const reminders = JSON.parse(localStorage.getItem('ecosage-reminders') || '[]');
    
    reminders.push({
      ...reminderData,
      scheduledFor: new Date(`${date} ${time}`).getTime(),
      id: Date.now()
    });

    localStorage.setItem('ecosage-reminders', JSON.stringify(reminders));
  }

  // Check and trigger local reminders
  checkLocalReminders() {
    const reminders = JSON.parse(localStorage.getItem('ecosage-reminders') || '[]');
    const now = Date.now();

    reminders.forEach((reminder, index) => {
      if (reminder.scheduledFor <= now) {
        this.showInAppNotification(reminder);
        
        // Remove triggered reminder
        reminders.splice(index, 1);
        localStorage.setItem('ecosage-reminders', JSON.stringify(reminders));
      }
    });
  }

  // Get current user ID (implement based on your auth system)
  getCurrentUserId() {
    // TODO: Replace with actual user authentication logic
    return localStorage.getItem('ecosage-user-id') || 'anonymous';
  }

  // Get device information
  getDeviceInfo() {
    return {
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      timestamp: Date.now()
    };
  }

  // Notification templates for different types
  static getNotificationTemplate(type, data = {}) {
    const templates = {
      waste_collection: {
        title: `🗑️ ${data.wasteType || 'Waste'} Collection Tomorrow!`,
        body: `Don't forget to put out your ${data.wasteType?.toLowerCase() || 'waste'} bins tonight.`,
        icon: '/icons/waste-icon.png'
      },
      community_event: {
        title: `🎉 ${data.eventName || 'Community Event'} Starting Soon!`,
        body: `Join us at ${data.location || 'the venue'} in ${data.timeUntil || '1 hour'}!`,
        icon: '/icons/event-icon.png'
      },
      challenge_nudge: {
        title: `💪 ${data.challengeName || 'Daily Challenge'}`,
        body: data.message || 'Take on today\'s eco-friendly challenge!',
        icon: '/icons/challenge-icon.png'
      },
      achievement: {
        title: `🏆 Achievement Unlocked!`,
        body: `Congratulations! You've earned: ${data.achievementName}`,
        icon: '/icons/achievement-icon.png'
      }
    };

    return templates[type] || templates.challenge_nudge;
  }
}

export default new NotificationService();