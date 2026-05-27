import streamlit as st
from utils.auth import get_user_history, check_authentication
import pandas as pd
from utils.translations import get_text

st.set_page_config(page_title="History", page_icon="📜")

language = st.sidebar.radio(
    get_text('language', 'en'),
    options=['en', 'am', 'om'],
    format_func=lambda x: {"en": "English", "am": "አማርኛ", "om": "Afaan Oromo"}.get(x, x),
    horizontal=True
)

if not check_authentication():
    st.stop()

st.title(get_text('history_title', language))

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
    st.subheader(get_text('your_statistics', language))
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(get_text('total_predictions', language), len(history))
    with col2:
        st.metric(get_text('avg_confidence', language), f"{df['confidence'].str.replace('%', '').astype(float).mean():.1f}%")
    with col3:
        most_common = df['predicted_disease'].mode().iloc[0] if not df.empty else "None"
        st.metric(get_text('most_common_disease', language), most_common)
else:
    st.info(get_text('no_predictions_yet', language))