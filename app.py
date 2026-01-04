import streamlit as st
from PIL import Image
from utils.image_logic import remove_background_logic, compose_portrait_canvas
import io

st.set_page_config(page_title="AI Virtual Travel", layout="centered")

st.title("✈️ AI Virtual Travel Agent")
st.write("Upload your selfie, remove background, and place yourself anywhere in the world.")

uploaded_file = st.file_uploader(
    "Upload a clear portrait photo (jpg/png):", type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    original = Image.open(uploaded_file)
    st.image(original, caption="Original Photo", width=300)

    if st.button("1️⃣ Remove Background"):
        with st.spinner("Removing background..."):
            cutout = remove_background_logic(original)
            st.session_state["cutout"] = cutout
        st.success("Background removed!")

if "cutout" in st.session_state:
    st.divider()
    st.subheader("2️⃣ Choose Background")

    bg_map = {
        "Hawaii Beach": "Hawaii image.jpg",
        "Paris": "paris image.webp",
        "Taj Mahal": "Taj Mahal.jpg",
    }

    place = st.selectbox("Select destination:", list(bg_map.keys()))
    if st.button("2️⃣ Generate Final Photo"):
        with st.spinner("Composing high‑quality image..."):
            final_img = compose_portrait_canvas(
                st.session_state["cutout"], bg_map[place]
            )
            st.session_state["final"] = final_img

    if "final" in st.session_state:
        st.image(
            st.session_state["final"],
            caption=f"You at {place}",
            use_container_width=True,  # responsive on mobile / tablet / desktop
        )

        buf = io.BytesIO()
        st.session_state["final"].save(
            buf, format="JPEG", quality=100, subsampling=0
        )
        st.download_button(
            "📥 Download High‑Quality JPEG",
            data=buf.getvalue(),
            file_name=f"trip_to_{place}.jpg",
            mime="image/jpeg",
        )
