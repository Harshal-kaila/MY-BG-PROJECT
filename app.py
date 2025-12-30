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
            transparent_img = remove_background_logic(user_img)
            st.session_state["transparent_img"] = transparent_img
            st.success("Background Removed!")

    # If we already have a transparent image
    if "transparent_img" in st.session_state:
        st.subheader("2. Background Removed Result")

        # Show the cut-out image
        st.image(
            st.session_state["transparent_img"],
            caption="Transparent PNG (no background)",
            width=350,
        )

        # Download only background-removed image
        buf_png = io.BytesIO()
        st.session_state["transparent_img"].save(buf_png, format="PNG")
        bg_removed_bytes = buf_png.getvalue()

        st.download_button(
            label="💾 Download PNG (No Background)",
            data=bg_removed_bytes,
            file_name="removed_background.png",
            mime="image/png",
        )

        st.divider()
        st.subheader("3. Place yourself into a destination")

        # Exact mapping of your files
        bg_options = {
            "Hawaii": "Hawaii image.jpg",
            "Paris": "paris image.webp",
            "Taj Mahal": "Taj Mahal.jpg",
        }

        # User selects destination
        location_choice = st.selectbox(
            "Select a destination:", list(bg_options.keys())
        )

        actual_filename = bg_options[location_choice]

        if st.button(f"🚀 Travel to {location_choice}!"):
            with st.spinner(f"Flying to {location_choice}..."):
                final_result = merge_background(
                    st.session_state["transparent_img"], actual_filename
                )

                st.image(
                    final_result,
                    caption=f"You in {location_choice}!",
                    use_container_width=True,  # Show at full quality
                )

                # Prepare high-quality download
                buf_jpg = io.BytesIO()
                final_result.save(buf_jpg, format="JPEG", quality=95)  # High quality
                merged_bytes = buf_jpg.getvalue()

                st.download_button(
                    label=f"💾 Download {location_choice} Photo",
                    data=merged_bytes,
                    file_name=f"trip_to_{location_choice}.jpg",
                    mime="image/jpeg",
                )
