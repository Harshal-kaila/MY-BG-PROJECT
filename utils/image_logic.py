from rembg import remove
import io
from PIL import Image

def remove_background_logic(input_image):
    """Cuts the subject out and makes the background transparent."""
    img_byte_arr = io.BytesIO()
    input_image.save(img_byte_arr, format='PNG')
    raw_data = img_byte_arr.getvalue()
    clean_data = remove(raw_data)
    return Image.open(io.BytesIO(clean_data))

def merge_background(subject_img, full_filename):
    """Glues the cut-out selfie onto a location image from the assets folder."""
    # Build the path using the exact full filename you provided
    bg_path = f"assets/{full_filename}"
    
    # 1. Open the background (works for both .jpg and .webp)
    background = Image.open(bg_path).convert("RGBA")
    
    # 2. Convert subject to RGBA for transparency
    subject = subject_img.convert("RGBA")
    
    # 3. Resize background to match selfie size
    background = background.resize(subject.size)
    
    # 4. Paste the subject
    background.paste(subject, (0, 0), subject)
    
    return background.convert("RGB")
