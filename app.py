import streamlit as st
from PIL import Image
import io
from utils.image_logic import remove_background_logic, merge_with_background

st.set_page_config(page_title="AI Virtual Travel", layout="wide")
st.title("✈️ AI Virtual Travel Agent")
st.markdown("Upload your selfie and transport yourself anywhere in the world!")

# Initialize state
if 'bg_removed' not in st.session_state:
    st.session_state['bg_removed'] = None

uploaded_file = st.file_uploader("📸 Step 1: Upload Selfie", type=['png','jpeg','jpg'])

if uploaded_file:
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption='Your Original Photo', use_container_width=True)
    
    if st.button('✂️ Remove Background'):
        with st.spinner('Making cutout...'):
            st.session_state['bg_removed'] = remove_background_logic(image)
            st.success('Background removed perfectly!')

    if st.session_state['bg_removed'] is not None:
        with col2:
            st.image(st.session_state['bg_removed'], caption='Clean Cutout', use_container_width=True)
        
        st.divider()
        
        # Background Selection
        st.subheader("🌍 Step 2: Select Your Destination")
        bg_options = {
            "Hawaii Beach": "Hawaii image.jpg",
            "Paris": "paris image.webp",
            "Taj Mahal": "Taj Mahal.jpg"
        }
        selected_name = st.selectbox("Where do you want to go?", list(bg_options.keys()))
        
        if st.button('🚀 Create Travel Photo'):
            with st.spinner('Matching colors and blending...'):
                final = merge_with_background(st.session_state['bg_removed'], bg_options[selected_name])
                st.session_state['final_image'] = final
        
        # Display and Download Result
        if 'final_image' in st.session_state:
            st.image(st.session_state['final_image'], caption='Your New Travel Photo!', use_container_width=True)
            
            buf = io.BytesIO()
            st.session_state['final_image'].save(buf, format='JPEG', quality=95)
            st.download_button("💾 Download High-Res Image", buf.getvalue(), "travel_result.jpg", "image/jpeg")

st.markdown("---")
st.caption("AI Logic: Edge Feathering + Linear Color Transfer + Alpha Compositing")