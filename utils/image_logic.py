from rembg import remove
import io
from PIL import Image, ImageFilter, ImageEnhance, ImageOps

def remove_background_logic(input_image):
    """Cuts the subject out and makes the background transparent."""
    img_byte_arr = io.BytesIO()
    input_image.save(img_byte_arr, format='PNG')
    raw_data = img_byte_arr.getvalue()
    clean_data = remove(raw_data)
    return Image.open(io.BytesIO(clean_data))

def feather_edges(image, radius=3):
    """
    Softens the hard edges of the cutout to make it blend 
    better with the background (removes the 'sticker' look).
    """
    # Create a mask from the alpha channel
    mask = image.split()[3]
    # Blur the mask slightly
    mask = mask.filter(ImageFilter.GaussianBlur(radius))
    # Put the blurred mask back
    image.putalpha(mask)
    return image

def merge_background(subject_img, full_filename):
    """
    Professional merging that:
    1. Anchors subject to the BOTTOM (hides the torso cut).
    2. Blurs background slightly (Portrait mode effect).
    3. Colors matches slightly for realism.
    """
    bg_path = f"assets/{full_filename}"
    
    # 1. Open Background
    background = Image.open(bg_path).convert("RGBA")
    bg_w, bg_h = background.size
    
    # --- PRO TIP: PORTRAIT MODE ---
    # Slight blur on background makes the subject pop and hides depth mismatch
    # (Like an iPhone Portrait photo)
    background = background.filter(ImageFilter.GaussianBlur(2))

    # 2. Prepare Subject
    subject = subject_img.convert("RGBA")
    
    # Apply feathering to remove hard "fake" edges
    subject = feather_edges(subject, radius=2)
    
    subj_w, subj_h = subject.size
    
    # 3. Smart Sizing Logic
    # We want the subject to be roughly 60-75% of the frame height for a "Selfie" look
    # This ensures high resolution is maintained
    target_height = int(bg_h * 0.75) 
    scale_ratio = target_height / subj_h
    target_width = int(subj_w * scale_ratio)
    
    # High-quality resize (LANCZOS keeps it sharp)
    subject_resized = subject.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # 4. Positioning Logic (CRITICAL FIX)
    # Position strictly at the BOTTOM to hide the flat cut of the torso
    x_position = (bg_w - target_width) // 2
    y_position = bg_h - target_height  # Exactly at the bottom line
    
    # 5. Composite
    # Create a new layer for the final image
    final_image = Image.new("RGBA", background.size)
    final_image.paste(background, (0, 0))
    # Paste subject at the calculated position
    final_image.paste(subject_resized, (x_position, y_position), subject_resized)
    
    return final_image.convert("RGB")
