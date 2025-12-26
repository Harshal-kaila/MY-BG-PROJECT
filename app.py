import streamlit as st
from PIL import Image
from utils.image_logic import remove_background_logic
import io

# 1. Page Config
st.set_page_config(page_title="AI BG Remover", layout="centered")

st.title("✂️ Professional BG Remover")
st.markdown("---")

# 2. File Upload (Reduced width for cleaner look)
uploaded_file = st.file_uploader("Upload your selfie...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Open image
    user_img = Image.open(uploaded_file)
    
    # Show Original (Smaller Size)
    st.subheader("1. Original Image")
    st.image(user_img, caption="Uploaded Photo", width=400)
    
    # 3. Processing Button
    if st.button("🚀 Remove Background"):
        with st.spinner("Processing..."):
            # Call Logic Engine
            final_output = remove_background_logic(user_img)
            
            # Save to 'Session State' so it doesn't disappear
            st.session_state['result_img'] = final_output
            st.success("Done!")

    # 4. Display Result and Download
    if 'result_img' in st.session_state:
        st.subheader("2. Final Result")
        st.image(st.session_state['result_img'], caption="Background Removed", width=400)
        
        # Prepare for Download
        buf = io.BytesIO()
        st.session_state['result_img'].save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="💾 Download PNG",
            data=byte_im,
            file_name="removed_bg.png",
            mime="image/png"
        )
