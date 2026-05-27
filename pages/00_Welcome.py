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
from utils.translations import get_text

st.set_page_config(
    page_title="Coffee Leaf Disease Detection",
    page_icon="🌿",
    layout="wide"
)

language = st.sidebar.radio(
    get_text('language', 'en'),
    options=['en', 'am', 'om'],
    format_func=lambda x: {"en": "English", "am": "አማርኛ", "om": "Afaan Oromo"}.get(x, x),
    horizontal=True
)

# PWA Install Banner at top
components.html(get_pwa_install_html(), height=260, scrolling=False)

# PWA Status
st.markdown(get_pwa_status_html(), unsafe_allow_html=True)

# Hero Section
st.markdown(f"""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #2c3e50, #27ae60); border-radius: 15px; color: white; margin-bottom: 2rem;">
    <h1 style="font-size: 2.5rem;">{get_text('welcome_title', language)}</h1>
    <p style="font-size: 1.2rem;">{get_text('welcome_subtitle', language)}</p>
    <p>🎯 98% Accuracy | 📱 {get_text('installable_app_title', language)} | 📴 {get_text('offline_support_title', language)}</p>
</div>
""", unsafe_allow_html=True)

# Features
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem;">
        <span style="font-size: 2rem;">🔍</span>
        <h3>{get_text('instant_detection_title', language)}</h3>
        <p>{get_text('instant_detection_desc', language)}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem;">
        <span style="font-size: 2rem;">📱</span>
        <h3>{get_text('installable_app_title', language)}</h3>
        <p>{get_text('installable_app_desc', language)}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem;">
        <span style="font-size: 2rem;">📴</span>
        <h3>{get_text('offline_support_title', language)}</h3>
        <p>{get_text('offline_support_desc', language)}</p>
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