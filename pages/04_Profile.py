"""
Coffee Leaf Disease Detection - Profile Page
User profile management, statistics, and settings
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re

# Import utilities
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.auth import check_authentication, get_user_history, get_db_stats, update_user_profile, change_user_password
from utils.translations import get_text
from utils.disease_info import DISEASE_INFO


# Check if user is logged in
if not check_authentication():
    st.stop()

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .profile-header {
        background: linear-gradient(135deg, #2c3e50, #27ae60);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    .info-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .achievement-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LANGUAGE SELECTION
# ============================================================================

language = st.sidebar.radio(
    "🌐 Language / ቋንቋ / Afaan",
    options=['en', 'am', 'om'],
    format_func=lambda x: {"en": "English", "am": "አማርኛ", "om": "Afaan Oromo"}.get(x, x),
    horizontal=True
)

# ============================================================================
# HEADER
# ============================================================================


# ============================================================================
# GET USER DATA
# ============================================================================

user_email = st.session_state.user_email
stats = get_db_stats(user_email)
history = get_user_history(user_email)

# ============================================================================
# PROFILE OVERVIEW SECTION
# ============================================================================

st.subheader(get_text('profile_overview', language))

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <h2>{stats.get('total_predictions', 0)}</h2>
        <p>📊 {get_text('total_predictions', language)}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <h2>{stats.get('avg_confidence', 0):.1f}%</h2>
        <p>🎯 {get_text('avg_confidence', language)}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Calculate days since join (using first prediction or current date)
    if history:
        first_prediction = history[-1]['created_at'] if isinstance(history[-1]['created_at'], str) else history[-1]['created_at']
        if isinstance(first_prediction, str):
            first_prediction = datetime.fromisoformat(first_prediction.replace('Z', '+00:00'))
        days_active = (datetime.now() - first_prediction).days + 1
    else:
        days_active = 1
    
    st.markdown(f"""
    <div class="stat-card">
        <h2>{days_active}</h2>
        <p>📅 {get_text('days_active', language)}</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    # Calculate accuracy (based on feedback or just show model accuracy)
    st.markdown(f"""
    <div class="stat-card">
        <h2>98%</h2>
        <p>✅ {get_text('model_accuracy', language)}</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PROFILE INFORMATION
# ============================================================================

st.subheader(get_text('profile_information', language))

col1, col2 = st.columns(2)

with col1:
    with st.container():
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown(f"**📧 Email**")
        st.write(user_email)
        
        st.markdown(f"**📅 {get_text('member_since', language)}**")
        if history:
            first_date = history[-1]['created_at']
            if isinstance(first_date, str):
                first_date = datetime.fromisoformat(first_date.replace('Z', '+00:00'))
            st.write(first_date.strftime("%B %d, %Y"))
        else:
            st.write("Today")
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    with st.container():
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown(f"**🏆 {get_text('achievements', language)}**")
        
        # Achievements based on predictions
        total_pred = stats.get('total_predictions', 0)
        
        achievements = []
        if total_pred >= 1:
            achievements.append("🌱 First Prediction")
        if total_pred >= 10:
            achievements.append("⭐ 10 Predictions")
        if total_pred >= 50:
            achievements.append("🏅 50 Predictions")
        if total_pred >= 100:
            achievements.append("🎖️ 100 Predictions")
        if stats.get('avg_confidence', 0) > 90:
            achievements.append("🎯 High Accuracy Achiever")
        
        if achievements:
            for ach in achievements:
                st.write(f"✅ {ach}")
        else:
            st.write("📌 Make your first prediction to earn achievements!")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# PREDICTION HISTORY
# ============================================================================

st.subheader(get_text('history_title', language))

if history:
    # Convert history to DataFrame
    df = pd.DataFrame(history)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['date'] = df['created_at'].dt.date
    df['confidence_pct'] = df['confidence'].apply(lambda x: f"{x*100:.1f}%")
    
    # Add display names for diseases
    df['disease_display'] = df['predicted_disease'].apply(
        lambda x: DISEASE_INFO.get(x, {}).get('name', x)
    )
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(get_text('total_predictions', language), len(df))
    with col2:
        most_common = df['disease_display'].mode().iloc[0] if not df.empty else "None"
        st.metric(get_text('most_common_disease', language), most_common)
    with col3:
        recent_date = df['created_at'].max().strftime("%Y-%m-%d") if not df.empty else "None"
        st.metric(get_text('last_prediction', language), recent_date)
    
    # Filter options
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        date_filter = st.selectbox(
            get_text('filter_by_time_period', language),
            [get_text('all_time', language), get_text('last_7_days', language), get_text('last_30_days', language), get_text('last_90_days', language)]
        )
    with col2:
        disease_filter = st.selectbox(
            get_text('filter_by_disease', language),
            [get_text('all_diseases', language)] + list(df['disease_display'].unique())
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if date_filter != get_text('all_time', language):
        filter_map = {
            get_text('last_7_days', language): 7,
            get_text('last_30_days', language): 30,
            get_text('last_90_days', language): 90
        }
        days = filter_map.get(date_filter, None)
        if days is not None:
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_df = filtered_df[filtered_df['created_at'] >= cutoff_date]
    
    if disease_filter != get_text('all_diseases', language):
        filtered_df = filtered_df[filtered_df['disease_display'] == disease_filter]
    
    # Display table
    st.dataframe(
        filtered_df[['created_at', 'disease_display', 'confidence_pct']].rename(columns={
            'created_at': 'Date',
            'disease_display': 'Disease',
            'confidence_pct': 'Confidence'
        }),
        use_container_width=True,
        height=300
    )
    
    # Download button
    csv = filtered_df[['created_at', 'predicted_disease', 'confidence']].to_csv(index=False)
    st.download_button(
        label=get_text('download_history_csv', language),
        data=csv,
        file_name=f"prediction_history_{user_email}.csv",
        mime="text/csv"
    )
    
    # ============================================================
    # VISUALIZATIONS
    # ============================================================
    st.subheader(get_text('analytics', language))
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Disease distribution pie chart
        disease_counts = filtered_df['disease_display'].value_counts()
        if not disease_counts.empty:
            fig = px.pie(
                values=disease_counts.values,
                names=disease_counts.index,
                title=get_text('disease_distribution', language),
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(get_text('no_data_available', language))
    
    with col2:
        # Predictions over time
        if not filtered_df.empty:
            daily_counts = filtered_df.set_index('created_at').resample('D').size().reset_index()
            daily_counts.columns = ['Date', 'Count']
            
            fig = px.line(
                daily_counts,
                x='Date',
                y='Count',
                title=get_text('predictions_over_time', language),
                markers=True
            )
            fig.update_layout(xaxis_title=get_text('date', language), yaxis_title=get_text('number_of_predictions', language))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(get_text('no_data_available', language))
    
    # Confidence trend
    if not filtered_df.empty:
        filtered_df['created_at_sorted'] = filtered_df['created_at']
        filtered_df = filtered_df.sort_values('created_at')
        
        fig = px.line(
            filtered_df,
            x='created_at',
            y='confidence',
            title="Confidence Trend Over Time",
            markers=True,
            color='disease_display'
        )
        fig.update_layout(xaxis_title="Date", yaxis_title="Confidence")
        st.plotly_chart(fig, use_container_width=True)
    
else:
    st.info(get_text('no_predictions_yet', language))
    
    # Show sample image link
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem;">
        <p>👉 <a href="#" onclick="alert('Please go to Detection page from sidebar')">{get_text('go_to_detection', language)}</a></p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# ACCOUNT SETTINGS
# ============================================================================

st.subheader(get_text('account_settings', language))

with st.expander(get_text('change_password', language)):
    with st.form("change_password_form"):
        current_password = st.text_input(get_text('current_password', language), type="password")
        new_password = st.text_input(get_text('new_password', language), type="password")
        confirm_password = st.text_input(get_text('confirm_new_password', language), type="password")
        
        submitted = st.form_submit_button(get_text('update_password', language))
        
        if submitted:
            if not current_password or not new_password:
                st.error("Please fill all fields")
            elif new_password != confirm_password:
                st.error("New passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                # Call password change function
                success, message = change_user_password(user_email, current_password, new_password)
                if success:
                    st.success(message)
                    # Clear session and ask to login again
                    st.info(get_text('please_login_again', language))
                    if st.button(get_text('logout_now', language)):
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()
                else:
                    st.error(message)

with st.expander(get_text('delete_my_account', language)):
    st.warning(get_text('delete_account_warning', language))
    
    with st.form("delete_account_form"):
        confirm_email = st.text_input(get_text('confirm_email_delete', language))
        delete_password = st.text_input(get_text('enter_your_password', language), type="password")
        
        submitted = st.form_submit_button(get_text('delete_my_account', language), type="primary")
        
        if submitted:
            if confirm_email != user_email:
                st.error("Email does not match")
            else:
                # Call delete function
                success, message = delete_user_account(user_email, delete_password)
                if success:
                    st.error(message)
                    st.info("Logging out...")
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
                else:
                    st.error(message)

# ============================================================================
# EXPORT DATA
# ============================================================================

with st.expander(get_text('export_my_data', language)):
    st.markdown(get_text('export_my_data', language))
    
    if history:
        # Prepare export data
        export_data = {
            'user_email': user_email,
            'export_date': datetime.now().isoformat(),
            'total_predictions': len(history),
            'statistics': stats,
            'predictions': [
                {
                    'date': str(p['created_at']),
                    'disease': p['predicted_disease'],
                    'confidence': p['confidence'],
                    'crop_used': p.get('crop_used', False)
                }
                for p in history
            ]
        }
        
        import json
        json_data = json.dumps(export_data, indent=2, default=str)
        
        st.download_button(
            label=get_text('download_all_data', language),
            data=json_data,
            file_name=f"coffee_disease_data_{user_email}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
    else:
        st.info(get_text('no_data_to_export', language))

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    f"<center><small>{get_text('footer', language)}</small></center>",
    unsafe_allow_html=True
)