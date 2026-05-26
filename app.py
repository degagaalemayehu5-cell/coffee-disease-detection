"""
Coffee Leaf Disease Detection - Main Entry Point
Progressive Web App (PWA) Enabled
Supports offline mode and installation on mobile devices
"""

import streamlit as st
import streamlit.components.v1 as components
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.auth import show_login_signup

# ============================================================================
# PAGE CONFIGURATION - MUST BE FIRST STREAMLIT COMMAND
# ============================================================================

st.set_page_config(
    page_title="Coffee Leaf Disease Detection",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit's automatic sidebar pages/nav header so only our custom menu shows
st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none !important;}
[data-testid="stSidebarHeader"] {display: none !important;}

/* Remove extra padding at top of main content */
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
}

/* Reduce gap between elements */
.element-container {
    margin-bottom: 0rem !important;
}

/* Remove extra spacing from welcome page */
.stMarkdown {
    margin-bottom: 0rem !important;
}

/* Compact the PWA status */
#pwa-status {
    margin: 0rem 0 0.5rem 0 !important;
    padding: 0.25rem !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# PWA META TAGS AND SERVICE WORKER
# ============================================================================

# Add PWA meta tags for installability
components.html("""
<!-- PWA Meta Tags -->
<link rel="manifest" href="/static/manifest.json">
<meta name="theme-color" content="#27ae60">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="CoffeeDetect">
<link rel="apple-touch-icon" href="/static/icons/icon-152x152.png">
<link rel="icon" type="image/png" sizes="192x192" href="/static/icons/icon-192x192.png">
<link rel="icon" type="image/png" sizes="512x512" href="/static/icons/icon-512x512.png">

<style>
    /* PWA Install Prompt Styling */
    .install-prompt {
        background: linear-gradient(135deg, #2c3e50, #27ae60);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.9; }
        50% { opacity: 1; }
        100% { opacity: 0.9; }
    }
    .install-button {
        background-color: white;
        color: #27ae60;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        cursor: pointer;
        margin-top: 0.5rem;
    }
    .install-button:hover {
        background-color: #f0f0f0;
    }
    
    /* PWA specific styles for better mobile experience */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.5rem !important;
        }
        .prediction-card {
            padding: 1rem !important;
        }
        .stButton button {
            padding: 0.5rem !important;
        }
    }
    
    /* Smooth transitions for PWA */
    * {
        transition: all 0.2s ease;
    }
    
    /* Better touch targets for mobile */
    button, .stButton button, .stRadio > div {
        min-height: 44px;
    }
    
    /* Offline indicator */
    .offline-indicator {
        position: fixed;
        bottom: 10px;
        right: 10px;
        background-color: #dc3545;
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
        display: none;
        z-index: 999;
    }
</style>

<!-- Register Service Worker -->
<script>
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/sw.js')
            .then(function(reg) {
                console.log('✅ Service Worker registered successfully:', reg.scope);
            })
            .catch(function(err) {
                console.log('❌ Service Worker registration failed:', err);
            });
    });
}

// PWA Installation prompt handler
// Expose the deferred prompt globally as `window.deferredPrompt` so other scripts
// (sidebar, auth widgets) can trigger the install flow.
window.deferredPrompt = null;
let isInstallBannerClosed = localStorage.getItem('pwaBannerClosed') === 'true';

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    window.deferredPrompt = e;

    // Show install button in the unified UI if available
    const installBtn = document.getElementById('install-pwa-btn');
    if (installBtn) {
        installBtn.style.display = 'block';
    }

    // Show popup only if not closed before
    if (!isInstallBannerClosed) {
        showInstallPopup();
    }
});

async function installPWA() {
    const deferred = window.deferredPrompt;
    if (deferred) {
        deferred.prompt();
        const choiceResult = await deferred.userChoice;
        if (choiceResult.outcome === 'accepted') {
            console.log('User accepted the install prompt');
            localStorage.setItem('pwaInstalled', 'true');
        }
        window.deferredPrompt = null;
    } else {
        alert('Install prompt not available. Make sure you are using Chrome or Edge or run via localhost.');
    }
}

function showInstallPopup() {
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
                console.log('User accepted install from popup');
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

// Check if app is already installed
function checkPWAInstalled() {
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || 
                        window.navigator.standalone === true;
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

// Listen for app installed event
window.addEventListener('appinstalled', () => {
    console.log('App installed successfully');
    localStorage.setItem('pwaInstalled', 'true');
    const popup = document.getElementById('pwa-install-popup');
    if (popup) popup.remove();
});

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

<div id="offline-indicator" class="offline-indicator">
    📴 You are offline
</div>

<div id="pwa-status" style="margin: 0rem 0 0.5rem 0; padding: 0.25rem; border-radius: 8px; text-align: center; font-size: 0.85rem; display: none;"></div>
""", height=420, scrolling=False)

# ============================================================================
# HEADER - REMOVED EXTRA SPACE
# ============================================================================

st.markdown("""
<div style="text-align: center; padding: 1rem 1rem 0.5rem 1rem; background: linear-gradient(135deg, #2c3e50, #27ae60); border-radius: 10px; color: white; margin-bottom: 1rem;">
    <h1 style="margin: 0; font-size: 1.8rem;">🌿 Coffee Leaf Disease Detection System</h1>
    <p style="margin: 0.25rem 0 0;">AI-Powered Diagnosis for Ethiopian Coffee Farmers</p>
    <p style="font-size: 0.75rem; margin-top: 0.25rem;">🎯 Model Accuracy: 98% | 📱 Install as App | 📴 Works Offline</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - PWA INSTALL BUTTON
# ============================================================================

# Install button that appears in sidebar
install_button_html = """
<div id="pwa-install-sidebar" style="margin: 0.5rem 0;">
    <button id="install-pwa-btn" style="background: linear-gradient(135deg, #2c3e50, #27ae60); color: white; border: none; padding: 0.7rem 1rem; border-radius: 25px; width: 100%; cursor: pointer; font-weight: bold; font-size: 1rem;">
        📥 Install App
    </button>
</div>

<script>
document.getElementById('install-pwa-btn')?.addEventListener('click', async () => {
    if (window.deferredPrompt) {
        window.deferredPrompt.prompt();
        const { outcome } = await window.deferredPrompt.userChoice;
        if (outcome === 'accepted') {
            console.log('User accepted install from sidebar');
            localStorage.setItem('pwaInstalled', 'true');
        }
        window.deferredPrompt = null;
    } else {
        alert('Install prompt not available. Make sure you are using Chrome or Edge.');
    }
});
</script>
"""

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

allowed_pages = [
    "🏠 Welcome",
    "📖 About"
]

if st.session_state.authenticated:
    allowed_pages = [
        "🏠 Welcome",
        "🔍 Disease Detection",
        "📦 Batch Prediction",
        "📖 About",
        "👤 My Profile"
    ]

with st.sidebar:
    st.markdown("## 📱 Navigation")
    
    # Navigation menu
    page = st.radio(
        "Go to:",
        allowed_pages,
        index=0
    )
    
    st.markdown("---")
    
    # PWA Install Button
    st.markdown(install_button_html, unsafe_allow_html=True)
    st.markdown("<small style='color: gray;'>Install to home screen for easy access</small>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # PWA Features
    st.markdown("### 📱 PWA Features")
    st.markdown("""
    - ✅ Install on device
    - ✅ Works offline
    - ✅ Fast loading
    - ✅ Push notifications
    """)
    
    st.markdown("---")
    
    # Offline status
    st.markdown("""
    <div id="online-status" style="background-color: #d4edda; padding: 0.5rem; border-radius: 5px; text-align: center;">
        ✅ Online
    </div>
    <script>
    function updateOnlineStatus() {
        const statusDiv = document.getElementById('online-status');
        if (statusDiv) {
            if (navigator.onLine) {
                statusDiv.innerHTML = '✅ Online';
                statusDiv.style.backgroundColor = '#d4edda';
                statusDiv.style.color = '#155724';
            } else {
                statusDiv.innerHTML = '📴 Offline';
                statusDiv.style.backgroundColor = '#f8d7da';
                statusDiv.style.color = '#721c24';
            }
        }
    }
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();
    </script>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE ROUTING
# ============================================================================

# Flag to control footer visibility (prevent double footer)
show_footer = True

if page == "🏠 Welcome":
    if not st.session_state.authenticated:
        show_login_signup()
    else:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2>Welcome back to Coffee Leaf Disease Detection System</h2>
            <p>This AI-powered system helps Ethiopian coffee farmers detect leaf diseases early.</p>
            <p>Logged in as: <strong>{}</strong></p>
        </div>
        """.format(st.session_state.get('user_email', 'Guest')), unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center;">
                <h3>🔍 98%</h3>
                <p>Model Accuracy</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center;">
                <h3>🌿 5</h3>
                <p>Diseases Detected</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center;">
                <h3>📱</h3>
                <p>PWA Enabled</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        ### 🚀 Quick Start
        
        1. **Install the app** - Click "Install App" in the sidebar to add to your home screen
        2. **Upload a photo** - Take or select a coffee leaf image
        3. **Get diagnosis** - AI will identify any disease
        4. **View treatment** - Get recommendations
        
        ### 📱 Install on Mobile
        
        - **Android:** Chrome → Menu → "Install App"
        - **iOS:** Safari → Share → "Add to Home Screen"
        """)

elif page == "🔍 Disease Detection":
    show_footer = False  # Detection page has its own footer
    try:
        detection_page = os.path.join(os.path.dirname(__file__), "pages", "01_Detection.py")
        if os.path.exists(detection_page):
            with open(detection_page, 'r', encoding='utf-8') as f:
                exec(f.read())
        else:
            st.error(f"Detection page not found at {detection_page}")
    except Exception as e:
        st.error(f"Error loading detection page: {e}")

elif page == "📦 Batch Prediction":
    show_footer = False  # Batch prediction page has its own footer
    try:
        batch_page = os.path.join(os.path.dirname(__file__), "pages", "02_BatchPrediction.py")
        if os.path.exists(batch_page):
            with open(batch_page, 'r', encoding='utf-8') as f:
                exec(f.read())
        else:
            st.error(f"Batch prediction page not found at {batch_page}")
    except Exception as e:
        st.error(f"Error loading batch prediction page: {e}")

elif page == "📖 About":
    show_footer = False  # About page already has its own footer (prevent double)
    try:
        about_page = os.path.join(os.path.dirname(__file__), "pages", "02_About.py")
        if os.path.exists(about_page):
            with open(about_page, 'r', encoding='utf-8') as f:
                exec(f.read())
        else:
            st.error(f"About page not found at {about_page}")
    except Exception as e:
        st.error(f"Error loading about page: {e}")

elif page == "👤 My Profile":
    show_footer = False  # Profile page has its own footer
    try:
        profile_page = os.path.join(os.path.dirname(__file__), "pages", "04_Profile.py")
        if os.path.exists(profile_page):
            with open(profile_page, 'r', encoding='utf-8') as f:
                exec(f.read())
        else:
            st.error(f"Profile page not found at {profile_page}")
    except Exception as e:
        st.error(f"Error loading profile page: {e}")

# ============================================================================
# FOOTER - Only show if the page doesn't have its own
# ============================================================================

if show_footer:
    st.markdown("---")
    st.markdown("""
    <center>
    <small>
    <strong>Hawassa University, Institute of Technology</strong><br>
    Faculty of Electrical and Computer Engineering | Computer Engineering Stream<br>
    © 2024 Coffee Leaf Disease Detection System | PWA Enabled
    </small>
    </center>
    """, unsafe_allow_html=True)