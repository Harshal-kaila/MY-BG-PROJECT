import streamlit as st
from PIL import Image
import io
from utils.image_logic import remove_background_logic, merge_with_background

st.set_page_config(page_title="AI Virtual Travel", layout="wide")
st.title("✈️ AI Virtual Travel Agent")

if 'bg_removed' not in st.session_state:
    st.session_state['bg_removed'] = None

uploaded_file = st.file_uploader("📸 Upload Selfie", type=['png','jpeg','jpg'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption='Original', width=300)
    
    if st.button('✂️ Remove Background'):
        with st.spinner('Processing...'):
            st.session_state['bg_removed'] = remove_background_logic(image)
            st.success('Done!')

    if st.session_state['bg_removed'] is not None:
        st.image(st.session_state['bg_removed'], caption='Cutout', width=300)
        
        bg_options = {
            "Hawaii Beach": "Hawaii image.jpg",
            "Paris": "paris image.webp",
            "Taj Mahal": "Taj Mahal.jpg"
        }
        selected_name = st.selectbox("Destination:", list(bg_options.keys()))
        
        if st.button('🚀 Create Travel Photo'):
            final = merge_with_background(st.session_state['bg_removed'], bg_options[selected_name])
            st.image(final, caption='Result', use_container_width=True)