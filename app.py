import streamlit as st
from PIL import Image
from utils.image_logic import remove_background_logic, merge_background
import io

# Page Config - Responsive Layout
st.set_page_config(page_title="AI Virtual Travel", layout="centered")

st.title("✈️ AI Virtual Travel Agent")
st.write("Take a selfie, travel the world! 🌍")

# --- Step 1: Upload ---
uploaded_file = st.file_uploader("Upload your selfie (Portrait style works best):", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Open image
    user_img = Image.open(uploaded_file)
    
    # Display centered and responsive
    st.image(user_img, caption="Original Photo", width=300)

    # --- Step 2: Remove Background ---
    if st.button("✂️ 1. Remove Background"):
        with st.spinner("Processing..."):
            transparent_img = remove_background_logic(user_img)
            st.session_state["transparent_img"] = transparent_img
            st.success("Background Removed Successfully!")

    # Check if we have the processed image in history
    if "transparent_img" in st.session_state:
        
        st.divider()
        st.subheader("2. Choose Your Destination")
        
        # Dictionary linking names to filenames
        bg_options = {
            "Hawaii Beach": "Hawaii image.jpg",
            "Paris (Eiffel Tower)": "paris image.webp",
            "India (Taj Mahal)": "Taj Mahal.jpg",
        }

        # Dropdown selection
        location_choice = st.selectbox("Where do you want to go?", list(bg_options.keys()))
        actual_filename = bg_options[location_choice]

        if st.button(f"🚀 Fly to {location_choice}"):
            with st.spinner("Merging images with AI..."):
                final_result = merge_background(
                    st.session_state["transparent_img"], 
                    actual_filename
                )
                
                # --- FINAL DISPLAY ---
                # use_container_width=True makes it perfect on Mobile/Tablet
                st.image(
                    final_result, 
                    caption=f"Welcome to {location_choice}!", 
                    use_container_width=True
                )
                
                # High Quality Download
                buf = io.BytesIO()
                final_result.save(buf, format="JPEG", quality=100, subsampling=0)
                byte_im = buf.getvalue()

                st.download_button(
                    label="📥 Download High-Quality Photo",
                    data=byte_im,
                    file_name=f"My_Trip_To_{location_choice}.jpg",
                    mime="image/jpeg",
                )
