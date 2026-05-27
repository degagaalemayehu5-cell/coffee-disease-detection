"""
Coffee Leaf Disease Detection - Detection Page
Main page for uploading and detecting diseases
Saves prediction history to MongoDB
Includes feedback collection system
"""

import streamlit as st
import streamlit.components.v1 as components
import tensorflow as tf
import numpy as np
from PIL import Image
import json
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_cropper import st_cropper
from datetime import datetime

# Import utilities
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.translations import get_text
from utils.model_loader import load_model_compatible
from utils.pwa import get_pwa_install_html
from utils.auth import (
    check_authentication,
    save_prediction_to_db,
    get_db_stats,
    save_feedback_to_db
)
from utils.disease_info import DISEASE_INFO

# ============================================================================
# AUTH CHECK
# ============================================================================

if not check_authentication():
    st.stop()

# ============================================================================
# SESSION STATE
# ============================================================================

if 'show_correction_form' not in st.session_state:
    st.session_state.show_correction_form = False

if 'last_prediction_id' not in st.session_state:
    st.session_state.last_prediction_id = None

if 'last_prediction_class' not in st.session_state:
    st.session_state.last_prediction_class = None

if 'last_prediction_confidence' not in st.session_state:
    st.session_state.last_prediction_confidence = None

if 'crop_applied' not in st.session_state:
    st.session_state.crop_applied = False

if 'cropped_image' not in st.session_state:
    st.session_state.cropped_image = None

if 'cropper_key' not in st.session_state:
    st.session_state.cropper_key = "manual_cropper_v2"

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
.prediction-card {
    padding: 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.healthy-card {
    background: linear-gradient(135deg, #d4edda, #c3e6cb);
    border-left: 5px solid #28a745;
}
.disease-card {
    background: linear-gradient(135deg, #fff3cd, #ffeaa7);
    border-left: 5px solid #ffc107;
}
.severe-card {
    background: linear-gradient(135deg, #f8d7da, #f5c6cb);
    border-left: 5px solid #dc3545;
}
.confidence-high { color: #28a745; font-weight: bold; }
.confidence-medium { color: #ffc107; font-weight: bold; }
.confidence-low { color: #dc3545; font-weight: bold; }
.upload-warning {
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}
.crop-instruction {
    background-color: #d4edda;
    padding: 0.8rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    font-size: 0.85rem;
    color: #155724;
    border-left: 4px solid #28a745;
}
.feedback-container {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
}
.correction-box {
    background-color: #fff3cd;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    border-left: 4px solid #ffc107;
}
.stCropper {
    width: 100% !important;
    overflow: hidden !important;
}
.stCropper canvas {
    max-width: 100% !important;
    height: auto !important;
    transform: scale(1) !important;
}
.stCropper img {
    max-width: 100% !important;
    height: auto !important;
    object-fit: contain !important;
    transform: none !important;
}
.cropper-container,
.cropper-canvas,
.cropper-wrap-box,
.cropper-drag-box,
.cropper-crop-box {
    transition: none !important;
    animation: none !important;
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
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.header(get_text('settings', language))
    components.html(get_pwa_install_html(), height=260, scrolling=False)

    models_dir = 'models'
    model_files = [f for f in os.listdir(models_dir) if f.endswith('.h5') or f.endswith('.keras')] if os.path.exists(models_dir) else []

    if model_files:
        default_index = 0
        for i, f in enumerate(model_files):
            if 'mobilenet' in f.lower() and 'best' in f.lower():
                default_index = i
                break
        selected_model = st.selectbox(get_text('select_model', language), model_files, index=default_index)
    else:
        st.error("No model files found in 'models/' folder!")
        st.stop()

    st.markdown("---")
    st.header("✂️ Image Preprocessing")
    crop_option = st.radio(
        "Select cropping option:",
        ["No cropping", "Manual (draw rectangle)", "Auto center crop"],
        help="Cropping helps focus on the affected area for better predictions"
    )
    if crop_option == "Auto center crop":
        zoom_factor = st.slider("Zoom factor", 0.5, 0.95, 0.8, 0.05)

    if crop_option != "Manual (draw rectangle)":
        st.session_state.crop_applied = False
        st.session_state.cropped_image = None

    st.markdown("---")
    st.header("📊 Your Statistics")
    stats = get_db_stats(st.session_state.user_email)
    if stats:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Predictions", stats.get('total_predictions', 0))
        with col2:
            st.metric("Avg Confidence", f"{stats.get('avg_confidence', 0):.1f}%")

    st.markdown("---")
    st.header("👤 Account")
    st.info(f"Logged in as: **{st.session_state.user_email}**")
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("---")
    st.header(get_text('about', language))
    if language == 'am':
        st.markdown("""
        **የሚታወቁ በሽታዎች:**
        - ✅ ጤናማ
        - 🍂 ሰርኮስፖራ
        - ⚠️ የቡና ዝገት
        - 🐛 የቡና ቆፋሪ
        - 🍂 ፎማ
        """)
    elif language == 'om':
        st.markdown("""
        **Dhukkuboota Beekamoo:**
        - ✅ Fayyaa qaba
        - 🍂 Cerkosoporaa
        - ⚠️ Dhulluun Bunaa
        - 🐛 Xuuxxuu Bunaa
        - 🍂 Foomawwan
        """)
    else:
        st.markdown("""
        **Supported Diseases:**
        - ✅ Healthy
        - 🍂 Cercospora Leaf Spot
        - ⚠️ Coffee Leaf Rust
        - 🐛 Coffee Leaf Miner
        - 🍂 Phoma Leaf Spot
        """)

# ============================================================================
# MAIN CONTENT
# ============================================================================

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(get_text('upload_title', language))
    uploaded_file = st.file_uploader(
        "Choose an image...",
        type=['jpg', 'jpeg', 'png', 'bmp', 'webp'],
        help="Upload a clear image of a coffee leaf"
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert('RGB')
        final_image = image
        crop_applied = False

        if crop_option == "Manual (draw rectangle)":
            st.markdown("""
            <div class="crop-instruction">
            ✂️ <strong>Draw directly on the image.</strong><br>
            The cropped image updates automatically while dragging.
            </div>
            """, unsafe_allow_html=True)
            st.markdown("### Crop Area")
            try:
                cropped = st_cropper(image, realtime_update=True, box_color="#00ff00", return_type="image", key=st.session_state.cropper_key, stroke_width=2)
            except Exception:
                cropped = st_cropper(image, realtime_update=True, box_color="#00ff00", return_type="image", key=st.session_state.cropper_key)

            if cropped is not None:
                if cropped.size != image.size:
                    st.session_state.cropped_image = cropped
                    st.session_state.crop_applied = True
                    final_image = cropped
                    crop_applied = True
                    st.image(cropped, caption="Live Cropped Image", width=300)
                else:
                    st.session_state.crop_applied = False
                    final_image = image

        elif crop_option == "Auto center crop":
            w, h = image.size
            new_w, new_h = int(w * zoom_factor), int(h * zoom_factor)
            left, top = (w - new_w) // 2, (h - new_h) // 2
            final_image = image.crop((left, top, left + new_w, top + new_h))
            crop_applied = True
            st.info(f"✨ Auto center crop applied (zoom: {zoom_factor*100:.0f}%)")
            st.image(final_image, caption='Cropped Image', width=300)
        else:
            st.image(image, caption='Uploaded Image', width=300)

        if st.button(get_text('detect_button', language), type="primary", use_container_width=True):
            with st.spinner(get_text('loading', language)):
                try:
                    if crop_option == "Manual (draw rectangle)" and st.session_state.get('crop_applied', False):
                        final_image = st.session_state.cropped_image
                    elif crop_option == "Auto center crop":
                        pass
                    else:
                        final_image = image

                    with open('models/class_names.json', 'r') as f:
                        class_names = json.load(f)

                    model_path = os.path.join('models', selected_model)
                    model = load_model_compatible(model_path)

                    if model is None:
                        st.error("❌ Failed to load model. Please check that the model file exists and is valid.")
                        st.stop()

                    resized = final_image.resize((224, 224))
                    img_array = np.array(resized) / 255.0
                    img_array = np.expand_dims(img_array, axis=0)

                    predictions = model.predict(img_array, verbose=0)
                    predicted_idx = np.argmax(predictions[0])
                    predicted_class = class_names[predicted_idx]
                    confidence = float(predictions[0][predicted_idx])

                    all_probs = {class_names[i]: float(predictions[0][i]) for i in range(len(class_names))}

                    prediction_data = {
                        'image_name': uploaded_file.name,
                        'image_url': '',
                        'predicted_disease': predicted_class,
                        'confidence': confidence,
                        'all_probabilities': all_probs,
                        'crop_used': crop_applied
                    }
                    prediction_id = save_prediction_to_db(st.session_state.user_email, prediction_data)
                    st.session_state.last_prediction_id = prediction_id
                    st.session_state.last_prediction_class = predicted_class
                    st.session_state.last_prediction_confidence = confidence

                    with col2:
                        st.subheader(get_text('diagnosis_results', language))
                        if confidence < 0.6:
                            st.markdown("""
                            <div class="upload-warning">
                            ⚠️ <strong>Low confidence prediction</strong><br>
                            Please try a clearer image or use the manual crop feature.
                            </div>
                            """, unsafe_allow_html=True)

                        info = DISEASE_INFO.get(predicted_class, {})
                        if language == 'am':
                            disease_name = info.get('name_am', predicted_class)
                            severity_text = info.get('severity_am', info.get('severity', 'Unknown'))
                            description_text = info.get('description_am', info.get('description', 'No description available.'))
                            treatment_text = info.get('treatment_am', info.get('treatment', 'Consult with local agricultural expert.'))
                            prevention_text = info.get('prevention_am', info.get('prevention', 'Regular monitoring recommended.'))
                        elif language == 'om':
                            disease_name = info.get('name_om', predicted_class)
                            severity_text = info.get('severity_om', info.get('severity', 'Unknown'))
                            description_text = info.get('description_om', info.get('description', 'No description available.'))
                            treatment_text = info.get('treatment_om', info.get('treatment', 'Consult with local agricultural expert.'))
                            prevention_text = info.get('prevention_om', info.get('prevention', 'Regular monitoring recommended.'))
                        else:
                            disease_name = info.get('name', predicted_class)
                            severity_text = info.get('severity', 'Unknown')
                            description_text = info.get('description', 'No description available.')
                            treatment_text = info.get('treatment', 'Consult with local agricultural expert.')
                            prevention_text = info.get('prevention', 'Regular monitoring recommended.')

                        icon = info.get('icon', '🔬')
                        if predicted_class == 'Healthy':
                            card_class = "healthy-card"
                        elif predicted_class in ['Leaf_rust', 'Leaf rust']:
                            card_class = "severe-card"
                        else:
                            card_class = "disease-card"

                        confidence_class = "confidence-high" if confidence > 0.8 else "confidence-medium" if confidence > 0.6 else "confidence-low"

                        st.markdown(f"""
                        <div class="prediction-card {card_class}">
                            <h2>{icon} {disease_name}</h2>
                            <p><strong>{get_text('confidence', language)}:</strong> 
                            <span class="{confidence_class}">{confidence*100:.2f}%</span></p>
                            <p><strong>{get_text('severity', language)}:</strong> {severity_text}</p>
                            <p><strong>{get_text('description', language)}:</strong> {description_text}</p>
                            <p><strong>{get_text('treatment', language)}:</strong> {treatment_text}</p>
                            <p><strong>{get_text('prevention', language)}:</strong> {prevention_text}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        fig_gauge = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=confidence * 100,
                            title={'text': f"Confidence: {disease_name}", 'font': {'size': 14}},
                            domain={'x': [0, 1], 'y': [0, 1]},
                            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#27ae60"},
                                   'steps': [{'range': [0, 50], 'color': "#ffcccc"}, {'range': [50, 75], 'color': "#ffebcc"}, {'range': [75, 100], 'color': "#ccffcc"}]}
                        ))
                        fig_gauge.update_layout(height=250)
                        st.plotly_chart(fig_gauge, use_container_width=True)

                        prob_df = pd.DataFrame({'Disease': list(all_probs.keys()), 'Probability': [v * 100 for v in all_probs.values()]}).sort_values('Probability', ascending=True)
                        if language == 'am':
                            prob_df['Display Name'] = prob_df['Disease'].apply(lambda x: DISEASE_INFO.get(x, {}).get('name_am', x))
                        elif language == 'om':
                            prob_df['Display Name'] = prob_df['Disease'].apply(lambda x: DISEASE_INFO.get(x, {}).get('name_om', x))
                        else:
                            prob_df['Display Name'] = prob_df['Disease'].apply(lambda x: DISEASE_INFO.get(x, {}).get('name', x))

                        fig_bar = px.bar(prob_df, x='Probability', y='Display Name', orientation='h', title='Prediction Probabilities', color='Probability', color_continuous_scale='Viridis', text=prob_df['Probability'].apply(lambda x: f'{x:.1f}%'))
                        fig_bar.update_layout(height=350)
                        st.plotly_chart(fig_bar, use_container_width=True)

                        st.markdown("---")
                        st.markdown('<div class="feedback-container">', unsafe_allow_html=True)
                        st.subheader("📝 Was this prediction correct?")

                        col_fb1, col_fb2 = st.columns(2)
                        with col_fb1:
                            if st.button("✅ Yes, Correct", use_container_width=True, key="feedback_correct"):
                                feedback_data = {'prediction_id': str(prediction_id) if prediction_id else None, 'user_email': st.session_state.user_email, 'was_correct': True, 'predicted_disease': predicted_class, 'confidence': confidence, 'image_name': uploaded_file.name, 'created_at': datetime.now().isoformat()}
                                save_feedback_to_db(feedback_data)
                                st.success("🙏 Thank you for your feedback!")
                                st.balloons()
                        with col_fb2:
                            if st.button("❌ No, Wrong", use_container_width=True, key="feedback_wrong"):
                                st.session_state.show_correction_form = True

                        if st.session_state.show_correction_form:
                            st.markdown('<div class="correction-box">', unsafe_allow_html=True)
                            st.markdown("#### 🔧 Help us improve!")
                            st.markdown("What is the correct disease for this image?")
                            disease_options = [c for c in class_names if c != predicted_class]
                            correct_disease = st.selectbox("Select correct disease:", disease_options, format_func=lambda x: DISEASE_INFO.get(x, {}).get('name', x), key="correct_disease")
                            comment = st.text_area("Additional comments (optional):", placeholder="e.g., This leaf actually has...", key="feedback_comment")
                            col_sub1, col_sub2 = st.columns(2)
                            with col_sub1:
                                if st.button("📤 Submit Correction", use_container_width=True):
                                    feedback_data = {'prediction_id': str(prediction_id) if prediction_id else None, 'user_email': st.session_state.user_email, 'was_correct': False, 'predicted_disease': predicted_class, 'actual_disease': correct_disease, 'confidence': confidence, 'comment': comment, 'image_name': uploaded_file.name, 'created_at': datetime.now().isoformat()}
                                    save_feedback_to_db(feedback_data)
                                    st.success("🙏 Thank you for the correction! This helps us improve the model.")
                                    st.session_state.show_correction_form = False
                                    st.rerun()
                            with col_sub2:
                                if st.button("Cancel", use_container_width=True):
                                    st.session_state.show_correction_form = False
                                    st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.success(f"✅ Prediction saved to your history! Total predictions: {stats.get('total_predictions', 0) + 1 if stats else 1}")

                except Exception as e:
                    st.error(f"Error during prediction: {str(e)}")
                    st.info("Please try again with a different image.")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(f"<center><small>{get_text('footer', language)}</small></center>", unsafe_allow_html=True)