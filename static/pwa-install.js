// static/pwa-install.js
// Enhanced PWA install handler with popup support

let deferredPrompt;
let isInstallBannerClosed = localStorage.getItem('pwaBannerClosed') === 'true';

// Show install popup
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // Show install popup
    showInstallPopup();
});

function showInstallPopup() {
    if (isInstallBannerClosed) return;
    
    // Create popup element
    const popup = document.createElement('div');
    popup.id = 'pwa-install-popup';
    popup.innerHTML = `
        <div style="position: fixed; bottom: 20px; left: 20px; right: 20px; background: linear-gradient(135deg, #2c3e50, #27ae60); color: white; padding: 1rem; border-radius: 15px; z-index: 9999; box-shadow: 0 4px 20px rgba(0,0,0,0.3); animation: slideUp 0.3s ease;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 2rem;">📱</span>
                <div style="flex: 1;">
                    <strong style="font-size: 1.1rem;">Install App</strong>
                    <p style="margin: 0; font-size: 0.85rem;">Install for offline use and faster access</p>
                </div>
                <button id="install-popup-btn" style="background: white; color: #27ae60; border: none; padding: 0.5rem 1rem; border-radius: 25px; font-weight: bold; cursor: pointer;">Install</button>
                <button id="close-popup-btn" style="background: transparent; color: white; border: none; font-size: 1.2rem; cursor: pointer;">✕</button>
            </div>
        </div>
        <style>
            @keyframes slideUp {
                from { transform: translateY(100%); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
        </style>
    `;
    
    document.body.appendChild(popup);
    
    // Install button handler
    document.getElementById('install-popup-btn')?.addEventListener('click', async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            if (outcome === 'accepted') {
                console.log('User accepted install');
                localStorage.setItem('pwaInstalled', 'true');
            }
            deferredPrompt = null;
            popup.remove();
        }
    });
    
    // Close button handler
    document.getElementById('close-popup-btn')?.addEventListener('click', () => {
        popup.remove();
        localStorage.setItem('pwaBannerClosed', 'true');
    });
}

// Check if already installed
function checkPWAInstalled() {
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || 
                        window.navigator.standalone === true;
    
    if (isStandalone) {
        localStorage.setItem('pwaInstalled', 'true');
        isInstallBannerClosed = true;
    }
}

checkPWAInstalled();

// Listen for app installed event
window.addEventListener('appinstalled', () => {
    console.log('App installed successfully');
    localStorage.setItem('pwaInstalled', 'true');
    const popup = document.getElementById('pwa-install-popup');
    if (popup) popup.remove();
});