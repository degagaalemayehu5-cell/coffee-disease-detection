"""
PWA (Progressive Web App) Utilities
Handles install prompts and offline detection
"""

import streamlit as st

def get_pwa_install_html():
    """Return HTML/JS for PWA install button"""
    return """
    <div id="pwa-install-container" style="margin: 1rem 0;">
        <div id="pwa-install-banner" style="display: none; background: linear-gradient(135deg, #2c3e50, #27ae60); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 1rem;">
            <span style="font-size: 1.5rem;">📱</span>
            <h3 style="margin: 0.5rem 0;">Install App</h3>
            <p style="margin: 0; font-size: 0.9rem;">Install this app on your device for easy access and offline use</p>
            <button id="install-pwa-btn" style="background: white; color: #27ae60; border: none; padding: 0.5rem 1.5rem; border-radius: 25px; font-weight: bold; margin-top: 0.8rem; cursor: pointer;">
                📥 Install Now
            </button>
            <button id="close-install-banner" style="background: transparent; color: white; border: 1px solid white; padding: 0.5rem 1rem; border-radius: 20px; margin-top: 0.8rem; margin-left: 0.5rem; cursor: pointer;">
                Not Now
            </button>
        </div>
    </div>

    <script>
    let deferredPrompt;
    let isInstallBannerClosed = localStorage.getItem('pwaBannerClosed') === 'true';

    function attachPwaButtonHandlers() {
        const installButton = document.getElementById('install-pwa-btn');
        const closeButton = document.getElementById('close-install-banner');

        installButton?.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                if (outcome === 'accepted') {
                    console.log('User accepted install');
                    document.getElementById('pwa-install-banner')?.style.display = 'none';
                    localStorage.setItem('pwaInstalled', 'true');
                }
                deferredPrompt = null;
            }
        });

        closeButton?.addEventListener('click', () => {
            document.getElementById('pwa-install-banner')?.style.display = 'none';
            localStorage.setItem('pwaBannerClosed', 'true');
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', attachPwaButtonHandlers);
    } else {
        attachPwaButtonHandlers();
    }

    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;

        const banner = document.getElementById('pwa-install-banner');
        if (banner && !isInstallBannerClosed) {
            banner.style.display = 'block';
        }
    });

    window.addEventListener('appinstalled', () => {
        console.log('App installed successfully');
        localStorage.setItem('pwaInstalled', 'true');
        document.getElementById('pwa-install-banner')?.style.display = 'none';
        const popup = document.getElementById('pwa-install-popup');
        if (popup) popup.remove();
        checkPWAInstalled();
    });

    function checkPWAInstalled() {
        const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
        const statusDiv = document.getElementById('pwa-status');
        if (!statusDiv) {
            return;
        }
        statusDiv.style.display = 'block';
        if (isStandalone) {
            localStorage.setItem('pwaInstalled', 'true');
            statusDiv.innerHTML = '✅ App installed! You are using the installed version.';
            statusDiv.style.background = '#d4edda';
            statusDiv.style.color = '#155724';
        } else {
            statusDiv.innerHTML = '📱 Install this app for offline access and faster launch.';
            statusDiv.style.background = '#fff3cd';
            statusDiv.style.color = '#856404';
        }
    }

    checkPWAInstalled();

    // Online/Offline detection
    window.addEventListener('online', function() {
        const indicator = document.getElementById('offline-indicator');
        if (indicator) indicator.style.display = 'none';
        location.reload();
    });

    window.addEventListener('offline', function() {
        const indicator = document.getElementById('offline-indicator');
        if (indicator) indicator.style.display = 'block';
    });
    </script>
    """


def get_pwa_status_html():
    """Return HTML showing PWA installation status"""
    return """
    <div id="pwa-status" style="margin: 1rem 0; padding: 0.5rem; border-radius: 8px; text-align: center; display: block; background: #fff3cd; color: #856404;">
        <span id="pwa-status-icon">📱</span>
        <span id="pwa-status-text">Install this app for better experience and offline access.</span>
    </div>
    <div id="offline-indicator" style="display: none; margin: 0.75rem 0; padding: 0.5rem; border-radius: 8px; background: #dc3545; color: white; text-align: center; font-size: 0.9rem;">📴 You are offline</div>
    """
