import streamlit as st
from utils.auth import get_user_history, check_authentication
import pandas as pd

st.set_page_config(page_title="History", page_icon="📜")

if not check_authentication():
    st.stop()

st.title("📜 Your Prediction History")

history = get_user_history(st.session_state.user_email)

if history:
    df = pd.DataFrame(history)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['confidence'] = df['confidence'].apply(lambda x: f"{x*100:.1f}%")
    
    st.dataframe(
        df[['created_at', 'predicted_disease', 'confidence', 'image_name']],
        use_container_width=True
    )
    
    # Statistics
    st.subheader("📊 Your Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Predictions", len(history))
    with col2:
        st.metric("Avg Confidence", f"{df['confidence'].str.replace('%', '').astype(float).mean():.1f}%")
    with col3:
        most_common = df['predicted_disease'].mode().iloc[0] if not df.empty else "None"
        st.metric("Most Common Disease", most_common)
else:
    st.info("No predictions yet. Go to the Detection page to analyze coffee leaves!")