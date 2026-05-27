"""
Coffee Leaf Disease Detection - Batch Prediction Page
Upload and analyze multiple coffee leaf images at once
"""

import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import json
import os
import pandas as pd
import plotly.express as px
from datetime import datetime

# Import utilities
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.translations import get_text
from utils.model_loader import load_model_compatible
from utils.auth import (
    check_authentication,
    save_prediction_to_db,
    get_db_stats
)
from utils.disease_info import DISEASE_INFO

# ============================================================================
# PAGE CONFIG
# ============================================================================



# ============================================================================
# AUTH CHECK
# ============================================================================

if not check_authentication():
    st.stop()

# ============================================================================
# SESSION STATE
# ============================================================================

if 'batch_results' not in st.session_state:
    st.session_state.batch_results = None

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2c3e50, #27ae60);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #27ae60;
    }
    .success-badge {
        background-color: #d4edda;
        color: #155724;
        padding: 0.2rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
    }
    .confidence-high { color: #28a745; font-weight: bold; }
    .confidence-medium { color: #ffc107; font-weight: bold; }
    .confidence-low { color: #dc3545; font-weight: bold; }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .supported-formats {
        background-color: #e7f3ff;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
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
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.header(get_text('settings', language))
    
    # Model selection
    models_dir = 'models'
    model_files = [f for f in os.listdir(models_dir) if f.endswith('.h5')] if os.path.exists(models_dir) else []
    
    if model_files:
        default_index = 0
        for i, f in enumerate(model_files):
            if 'mobilenet' in f.lower() and 'best' in f.lower():
                default_index = i
                break
        selected_model = st.selectbox(get_text('select_model', language), model_files, index=default_index)
    else:
        st.error(get_text('no_model', language))
        st.stop()
    
    st.markdown("---")
    
    # User stats
    st.header(get_text('your_statistics', language))
    stats = get_db_stats(st.session_state.user_email)
    if stats:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(get_text('total_predictions', language), stats.get('total_predictions', 0))
        with col2:
            avg_conf = stats.get('avg_confidence', 0)
            st.metric(get_text('avg_confidence', language), f"{avg_conf:.1f}%")
    
    st.markdown("---")
    
    # User info
    st.header(get_text('account', language))
    st.info(f"{get_text('logged_in_as', language)}: **{st.session_state.user_email}**")
    
    if st.button(get_text('logout', language), use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ============================================================================
# BATCH PREDICTION FUNCTIONS
# ============================================================================

def process_batch_images(uploaded_files, model, class_names):
    """Process multiple images and return results"""
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"📸 Processing image {idx + 1} of {len(uploaded_files)}: {uploaded_file.name}")
        
        try:
            # Load image
            image = Image.open(uploaded_file).convert('RGB')
            original_size = image.size
            
            # Preprocess
            resized = image.resize((224, 224))
            img_array = np.array(resized) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            # Predict
            predictions = model.predict(img_array, verbose=0)
            predicted_idx = np.argmax(predictions[0])
            predicted_class = class_names[predicted_idx]
            confidence = float(predictions[0][predicted_idx])
            
            # Get all probabilities
            all_probs = {class_names[i]: float(predictions[0][i]) for i in range(len(class_names))}
            
            # Save to database
            prediction_data = {
                'image_name': uploaded_file.name,
                'image_url': '',
                'predicted_disease': predicted_class,
                'confidence': confidence,
                'all_probabilities': all_probs,
                'crop_used': False
            }
            prediction_id = save_prediction_to_db(st.session_state.user_email, prediction_data)
            
            results.append({
                'index': idx + 1,
                'filename': uploaded_file.name,
                'image': image,
                'original_size': original_size,
                'predicted_class': predicted_class,
                'confidence': confidence,
                'all_probs': all_probs,
                'prediction_id': prediction_id,
                'success': True
            })
            
        except Exception as e:
            results.append({
                'index': idx + 1,
                'filename': uploaded_file.name,
                'error': str(e),
                'success': False
            })
        
        # Update progress
        progress_bar.progress((idx + 1) / len(uploaded_files))
    
    status_text.empty()
    progress_bar.empty()
    
    return results

def display_batch_results(results, language):
    """Display batch prediction results"""
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    # ============================================================
    # SUMMARY STATISTICS
    # ============================================================
    st.subheader(get_text('your_statistics', language))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <h2>{len(results)}</h2>
            <p>{get_text('total_predictions', language)}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stats-card" style="background: linear-gradient(135deg, #28a745, #20c997);">
            <h2>{len(successful)}</h2>
            <p>{get_text('successful', language) if get_text('successful', language) != 'successful' else 'Successful'}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stats-card" style="background: linear-gradient(135deg, #dc3545, #c82333);">
            <h2>{len(failed)}</h2>
            <p>Failed</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        if successful:
            avg_conf = sum(r['confidence'] for r in successful) / len(successful)
            st.markdown(f"""
            <div class="stats-card" style="background: linear-gradient(135deg, #17a2b8, #138496);">
                <h2>{avg_conf*100:.1f}%</h2>
                <p>{get_text('avg_confidence', language)}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ============================================================
    # DISEASE DISTRIBUTION
    # ============================================================
    if successful:
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown(f"**📈 {get_text('disease_distribution', language)}**")
            disease_counts = {}
            for r in successful:
                disease = r['predicted_class']
                disease_counts[disease] = disease_counts.get(disease, 0) + 1
            
            for disease, count in sorted(disease_counts.items(), key=lambda x: -x[1]):
                info = DISEASE_INFO.get(disease, {})
                if language == 'am':
                    name = info.get('name_am', disease)
                elif language == 'om':
                    name = info.get('name_om', disease)
                else:
                    name = info.get('name', disease)
                percent = count / len(successful) * 100
                st.markdown(f"- **{name}**: {count} ({percent:.1f}%)")
        
        with col_b:
            # Pie chart
            fig = px.pie(
                values=list(disease_counts.values()),
                names=[DISEASE_INFO.get(d, {}).get('name', d) for d in disease_counts.keys()],
                title=get_text('disease_distribution', language),
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    # ============================================================
    # INDIVIDUAL RESULTS
    # ============================================================
    st.markdown("---")
    st.subheader(get_text('detailed_results', language))
    
    for result in results:
        if result['success']:
            info = DISEASE_INFO.get(result['predicted_class'], {})
            
            if language == 'am':
                disease_name = info.get('name_am', result['predicted_class'])
                treatment_text = info.get('treatment_am', info.get('treatment', 'Consult expert'))
            elif language == 'om':
                disease_name = info.get('name_om', result['predicted_class'])
                treatment_text = info.get('treatment_om', info.get('treatment', 'Consult expert'))
            else:
                disease_name = info.get('name', result['predicted_class'])
                treatment_text = info.get('treatment', 'Consult expert')
            
            confidence_pct = result['confidence'] * 100
            
            if confidence_pct >= 80:
                conf_class = "confidence-high"
            elif confidence_pct >= 60:
                conf_class = "confidence-medium"
            else:
                conf_class = "confidence-low"
            
            with st.expander(f"📷 {result['filename']} - {disease_name} ({confidence_pct:.1f}%)"):
                col_img, col_info = st.columns([1, 1])
                
                with col_img:
                    st.image(result['image'], caption=result['filename'], use_container_width=True)
                
                with col_info:
                    st.markdown(f"""
                    **Predicted Disease:** {disease_name}<br>
                    **Confidence:** <span class="{conf_class}">{confidence_pct:.2f}%</span><br>
                    **Image Size:** {result['original_size'][0]} x {result['original_size'][1]} pixels<br><br>
                    **💊 Treatment:** {treatment_text}<br><br>
                    **📅 Predicted on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """, unsafe_allow_html=True)
                    
                    # Probability bar chart for this image
                    prob_df = pd.DataFrame({
                        'Disease': list(result['all_probs'].keys()),
                        'Probability': [v * 100 for v in result['all_probs'].values()]
                    }).sort_values('Probability', ascending=True)
                    
                    if language == 'am':
                        prob_df['Display'] = prob_df['Disease'].apply(lambda x: DISEASE_INFO.get(x, {}).get('name_am', x))
                    elif language == 'om':
                        prob_df['Display'] = prob_df['Disease'].apply(lambda x: DISEASE_INFO.get(x, {}).get('name_om', x))
                    else:
                        prob_df['Display'] = prob_df['Disease'].apply(lambda x: DISEASE_INFO.get(x, {}).get('name', x))
                    
                    fig = px.bar(prob_df, x='Probability', y='Display', orientation='h',
                                 title=get_text('prediction_probabilities', language),
                                 color='Probability',
                                 color_continuous_scale='Viridis',
                                 text=prob_df['Probability'].apply(lambda x: f'{x:.1f}%'))
                    fig.update_layout(height=250)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            with st.expander(f"❌ {result['filename']} - Failed"):
                st.error(f"Error: {result.get('error', 'Unknown error')}")
                st.info("Please try again with a different image format.")
    
    # ============================================================
    # EXPORT RESULTS
    # ============================================================
    if successful:
        st.markdown("---")
        st.subheader(get_text('export_results', language))
        
        # Create CSV export
        export_data = []
        for r in successful:
            info = DISEASE_INFO.get(r['predicted_class'], {})
            export_data.append({
                'Filename': r['filename'],
                'Predicted Disease': r['predicted_class'],
                'Confidence (%)': f"{r['confidence']*100:.2f}",
                'Treatment': info.get('treatment', ''),
                'Prevention': info.get('prevention', ''),
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        df = pd.DataFrame(export_data)
        csv = df.to_csv(index=False)
        
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            st.download_button(
                label=get_text('download_results_csv', language),
                data=csv,
                file_name=f"batch_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_exp2:
            # Create JSON export
            import json
            json_data = json.dumps(export_data, indent=2, default=str)
            st.download_button(
                label=get_text('download_results_json', language),
                data=json_data,
                file_name=f"batch_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        st.success(f"✅ {get_text('successfully_processed', language)} {len(successful)} {get_text('images_and_saved_history', language)}")

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.subheader(get_text('upload_multiple_images', language))

st.markdown(f"""
<div class="supported-formats">
📷 <strong>{get_text('supported_formats_text', language)}</strong><br>
💡 <strong>Tip:</strong> {get_text('select_multiple_images', language)}<br>
📊 <strong>{get_text('batch_limit_text', language)}</strong>
</div>
""", unsafe_allow_html=True)

# File uploader for multiple images
uploaded_files = st.file_uploader(
    get_text('choose_images', language),
    type=['jpg', 'jpeg', 'png', 'bmp', 'webp'],
    accept_multiple_files=True,
    help="Select multiple coffee leaf images for batch analysis",
    key="batch_uploader"
)

if uploaded_files:
    # Limit to 50 images
    if len(uploaded_files) > 50:
        st.warning(f"{get_text('batch_limit_text', language)}")
        uploaded_files = uploaded_files[:50]
    
    st.info(f"📸 {len(uploaded_files)} {get_text('image_selected_info', language)}")
    
    # Preview selected images
    with st.expander(f"📷 Preview Selected Images ({len(uploaded_files)} images)"):
        cols = st.columns(min(6, len(uploaded_files)))
        for idx, file in enumerate(uploaded_files[:6]):
            with cols[idx % 6]:
                try:
                    img = Image.open(file).convert('RGB')
                    st.image(img, caption=file.name[:20], use_container_width=True)
                except:
                    st.write(f"❌ {file.name[:20]}")
        if len(uploaded_files) > 6:
            st.caption(f"... and {len(uploaded_files) - 6} more images")
    
    # Start batch prediction button
    if st.button(get_text('start_batch_prediction', language), type="primary", use_container_width=True):
        with st.spinner(get_text('loading_model', language)):
            # Load class names
            with open('models/class_names.json', 'r') as f:
                class_names = json.load(f)
            
            # Load model
            model_path = os.path.join('models', selected_model)
            model = load_model_compatible(model_path)
            
            if model is None:
                st.error(get_text('failed_to_load_model', language))
                st.stop()
        
        # Process batch
        results = process_batch_images(uploaded_files, model, class_names)
        
        # Store in session state
        st.session_state.batch_results = results
        
        # Display results
        display_batch_results(results, language)
        
        st.balloons()

else:
    st.info(get_text('no_images_selected', language))

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    f"<center><small>{get_text('batch_prediction_footer', language)}</small></center>",
    unsafe_allow_html=True
)