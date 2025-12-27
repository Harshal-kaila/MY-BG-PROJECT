import streamlit as st
from PIL import Image
from utils.image_logic import remove_background_logic, merge_background
import io

# 1. Page Configuration
st.set_page_config(page_title="AI Virtual Travel", layout="centered")
st.title("✈️ AI Virtual Travel Agent")

# 2. Step 1: Upload Selfie
uploaded_file = st.file_uploader("Upload your selfie...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    user_img = Image.open(uploaded_file)
    st.image(user_img, caption="1. Your Original Photo", width=350)
    
    # 3. Step 2: Remove Background
    if st.button("✂️ Remove Background"):
        with st.spinner("Cutting you out..."):
            st.session_state['transparent_img'] = remove_background_logic(user_img)
            st.success("Background Removed!")

    # 4. Step 3: Choose Location & Merge
    if 'transparent_img' in st.session_state:
        st.divider()
        st.subheader("2. Where do you want to go?")
        
        # Exact mapping of your files
        bg_options = {
            "Hawaii": "Hawaii image.jpg",
            "Paris": "paris image.webp",
            "Taj Mahal": "Taj Mahal.jpg"
        }
        
        # User selects friendly name
        location_choice = st.selectbox("Select a destination:", list(bg_options.keys()))
        
        # Get the actual filename from the choice
        actual_filename = bg_options[location_choice]

        if st.button(f"🚀 Travel to {location_choice}!"):
            with st.spinner(f"Flying to {location_choice}..."):
                # Call the Logic with the EXACT filename
                final_result = merge_background(st.session_state['transparent_img'], actual_filename)
                
                st.image(final_result, caption=f"You in {location_choice}!", width=500)
                
                # Prepare Download
                buf = io.BytesIO()
                final_result.save(buf, format="JPEG")
                byte_im = buf.getvalue()
                
                st.download_button(
                    label=f"💾 Download {location_choice} Photo",
                    data=byte_im,
                    file_name=f"trip_to_{location_choice}.jpg",
                    mime="image/jpeg"
                )
