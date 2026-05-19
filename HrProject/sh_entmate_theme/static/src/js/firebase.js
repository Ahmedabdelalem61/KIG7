/** @odoo-module **/
import { rpc as jsonrpc } from "@web/core/network/rpc";

jsonrpc("/web/_config", {})
    .then(function (data) {
        if (!data || typeof firebase === "undefined") {
            return;
        }
        const json = JSON.parse(data);
        const vapid = json.vapid;
        const firebaseConfig = json.config;
        firebase.initializeApp(firebaseConfig);
        const messaging = firebase.messaging();

        messaging.onMessage((payload) => {
            const notificationOptions = {
                body: payload.notification.body,
            };
            const notification = payload.notification;
            navigator.serviceWorker.getRegistrations().then((registration) => {
                if (registration[0]) {
                    registration[0].showNotification(notification.title, notificationOptions);
                }
            });
        });
        messaging
            .requestPermission()
            .then(function () {
                messaging
                    .getToken({ vapidKey: vapid })
                    .then((currentToken) => {
                        if (currentToken && window.jQuery) {
                            window.jQuery.post("/web/push_token", {
                                name: currentToken,
                            });
                        }
                    })
                    .catch((err) => {
                        console.log("An error occurred while retrieving token. ", err);
                    });
            })
            .catch(() => {});
    })
    .catch(() => {});
