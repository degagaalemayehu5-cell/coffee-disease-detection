"""
Welcome Page with Login/Signup and PWA Install
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.auth import check_authentication, show_login_signup
from utils.pwa import get_pwa_install_html, get_pwa_status_html

st.set_page_config(
    page_title="Coffee Leaf Disease Detection",
    page_icon="🌿",
    layout="wide"
)

# PWA Install Banner at top
components.html(get_pwa_install_html(), height=260, scrolling=False)

# PWA Status
st.markdown(get_pwa_status_html(), unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #2c3e50, #27ae60); border-radius: 15px; color: white; margin-bottom: 2rem;">
    <h1 style="font-size: 2.5rem;">🌿 Coffee Leaf Disease Detection</h1>
    <p style="font-size: 1.2rem;">AI-Powered Diagnosis for Ethiopian Coffee Farmers</p>
    <p>🎯 98% Accuracy | 📱 Install App | 📴 Works Offline</p>
</div>
""", unsafe_allow_html=True)

# Features
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <span style="font-size: 2rem;">🔍</span>
        <h3>Instant Detection</h3>
        <p>Upload a photo and get disease diagnosis instantly</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <span style="font-size: 2rem;">📱</span>
        <h3>Installable App</h3>
        <p>Install on your phone for easy access anytime</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <span style="font-size: 2rem;">📴</span>
        <h3>Offline Support</h3>
        <p>Works even without internet connection</p>
    </div>
    """, unsafe_allow_html=True)

# Login/Signup Section
show_login_signup()

# Footer
st.markdown("---")
st.markdown("""
<center>
<small>
<strong>Hawassa University, Institute of Technology</strong><br>
Faculty of Electrical and Computer Engineering | Computer Engineering Stream
</small>
</center>
""", unsafe_allow_html=True)