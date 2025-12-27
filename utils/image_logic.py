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
    """
    Places the cut-out selfie onto a location image from the assets folder
    in a more realistic way (smaller size, bottom-center).
    """
    # Build the path using the exact full filename you provided
    bg_path = f"assets/{full_filename}"

    # 1. Open the background
    background = Image.open(bg_path).convert("RGBA")

    # 2. Prepare subject (transparent selfie)
    subject = subject_img.convert("RGBA")

    # 3. Resize subject to be smaller relative to the background
    bg_w, bg_h = background.size

    # Make subject about 40% of background width
    target_width = int(bg_w * 0.4)
    # Keep aspect ratio
    scale = target_width / subject.width
    target_height = int(subject.height * scale)

    subject = subject.resize((target_width, target_height), Image.LANCZOS)

    # 4. Choose position: bottom-center
    x = (bg_w - target_width) // 2
    y = bg_h - target_height - int(bg_h * 0.05)  # little margin from bottom

    # 5. Paste the subject onto background using alpha channel
    background.paste(subject, (x, y), subject)

    # 6. Return final merged RGB image
    return background.convert("RGB")
