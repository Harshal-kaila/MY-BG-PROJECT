import streamlit as st
from PIL import Image
import io
from utils.image_logic import remove_background_logic, merge_with_background

st.set_page_config(page_title="AI Virtual Travel", layout="wide")
st.title("✈️ AI Virtual Travel Agent")

# File uploader
uploaded_file = st.file_uploader("📸 Step 1: Upload Selfie", type=['png','jpeg','jpg'])

if uploaded_file:
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption='Original Photo', use_container_width=True)
    
    if st.button('✂️ Remove Background'):
        with st.spinner('Processing...'):
            st.session_state['bg_removed'] = remove_background_logic(image)
            st.success('Background Removed!')

    # If background is removed, show it and provide download
    if 'bg_removed' in st.session_state and st.session_state['bg_removed'] is not None:
        with col2:
            st.image(st.session_state['bg_removed'], caption='Transparent Cutout', use_container_width=True)
            
            # DOWNLOAD 1: Transparent PNG
            buf_png = io.BytesIO()
            st.session_state['bg_removed'].save(buf_png, format='PNG')
            st.download_button("💾 Download PNG (No BG)", buf_png.getvalue(), "cutout.png", "image/png")
        
        st.divider()
        
        # Step 2: Destination
        st.subheader("🌍 Step 2: Choose Destination")
        bg_options = {
            "Hawaii Beach": "Hawaii image.jpg",
            "Paris": "paris image.webp",
            "Taj Mahal": "Taj Mahal.jpg"
        }
        selected_name = st.selectbox("Where are we going?", list(bg_options.keys()))
        
        if st.button('🚀 Create Travel Photo'):
            with st.spinner('Blending and matching lighting...'):
                final = merge_with_background(st.session_state['bg_removed'], bg_options[selected_name])
                st.session_state['final_image'] = final
        
        # If final image is generated, show it and provide download
        if 'final_image' in st.session_state:
            st.image(st.session_state['final_image'], caption='Your Travel Result', use_container_width=True)
            
            # DOWNLOAD 2: Final Travel Photo
            buf_jpg = io.BytesIO()
            st.session_state['final_image'].save(buf_jpg, format='JPEG', quality=95)
            st.download_button("📸 Download Travel Photo", buf_jpg.getvalue(), "travel_photo.jpg", "image/jpeg")

st.markdown("---")
st.caption("Features: Edge Feathering, Bokeh Background, Color Matching & Brightness Auto-Adjust.")