import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Replace with your actual public VAPID key
const applicationServerKey = 'BASurhxWN80cYcss_4_EPPmtyvuBN82PuqFsFM-uhvpdjifkowH5Qwos4I1UIe_-tdR3zuCEqmiGkGcn5FqmXxI';

const urlBase64ToUint8Array = (base64String) => {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
};

const NotificationComponent = () => {
    const [subscriptionInfo, setSubscriptionInfo] = useState(null);

    useEffect(() => {
        // Register the service worker
        if ('serviceWorker' in navigator && 'PushManager' in window) {
            navigator.serviceWorker.register('/static/notifications/service-worker.js')
                .then((registration) => {
                    console.log('Service Worker registered:', registration);
                })
                .catch((error) => {
                    console.error('Service Worker registration failed:', error);
                });
        } else {
            console.error('Service Worker or Push Manager not supported');
        }
    }, []);

    const subscribeUser = () => {
        navigator.serviceWorker.ready.then((registration) => {
            registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(applicationServerKey),
            }).then((subscription) => {
                console.log('Subscription successful:', subscription);
                setSubscriptionInfo(subscription);
                sendSubscriptionToServer(subscription);
            }).catch((error) => {
                console.error('Subscription failed:', error);
            });
        });
    };

    const sendSubscriptionToServer = (subscription) => {
        axios.post('/notifications/subscribe/', {
            subscription_info: subscription
        }, {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then((response) => {
            console.log('Subscription successful');
        })
        .catch((error) => {
            console.error('Error sending subscription:', error);
        });
    };

    const triggerNotification = () => {
        axios.post('/notifications/send_notification/', {
            user_id: 1 // Replace with the appropriate user id
        }, {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then((response) => {
            console.log('Notification triggered successfully');
        })
        .catch((error) => {
            console.error('Error triggering notification:', error);
        });
    };

    const getCSRFToken = () => {
        let csrfToken = null;
        const cookies = document.cookie.split(';');
        cookies.forEach(cookie => {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                csrfToken = value;
            }
        });
        return csrfToken;
    };

    return (
        <div>
            <h1>Welcome to Web Push Notifications</h1>
            <p>This is a demo page for web push notifications.</p>
            <button id="subscribeBtn" onClick={subscribeUser}>Subscribe to Notifications</button>
            <button id="triggerBtn" onClick={triggerNotification}>Trigger Notification</button>
        </div>
    );
};

export default NotificationComponent;
