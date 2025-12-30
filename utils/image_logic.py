from rembg import remove
import io
from PIL import Image, ImageFilter, ImageEnhance


def remove_background_logic(input_image):
    """Cuts the subject out and makes the background transparent."""
    img_byte_arr = io.BytesIO()
    input_image.save(img_byte_arr, format='PNG')
    raw_data = img_byte_arr.getvalue()
    clean_data = remove(raw_data)
    return Image.open(io.BytesIO(clean_data))


def merge_background(subject_img, full_filename):
    """
    Places the cut-out person onto a background in a more realistic way:
    - Maintains background at full resolution
    - Scales person proportionally based on background
    - Adds subtle shadow for depth
    - Positions person intelligently
    """
    # Build the path
    bg_path = f"assets/{full_filename}"
    
    # 1. Open background at full quality
    background = Image.open(bg_path).convert("RGBA")
    bg_w, bg_h = background.size
    
    # 2. Prepare subject
    subject = subject_img.convert("RGBA")
    subj_w, subj_h = subject.size
    
    # 3. Smart sizing: Person should be 30-45% of background height
    # (This maintains realistic proportions)
    target_height = int(bg_h * 0.42)
    scale_ratio = target_height / subj_h
    target_width = int(subj_w * scale_ratio)
    
    # Resize subject with high-quality resampling
    subject_resized = subject.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # 4. Create a subtle drop shadow for realism
    shadow = Image.new('RGBA', subject_resized.size, (0, 0, 0, 0))
    shadow_layer = Image.new('RGBA', subject_resized.size, (0, 0, 0, 80))  # Semi-transparent black
    shadow.paste(shadow_layer, (0, 0), subject_resized)  # Use subject as mask
    shadow = shadow.filter(ImageFilter.GaussianBlur(15))  # Blur the shadow
    
    # 5. Smart positioning: Bottom-center with margin
    margin_bottom = int(bg_h * 0.08)  # 8% margin from bottom
    x_position = (bg_w - target_width) // 2  # Center horizontally
    y_position = bg_h - target_height - margin_bottom
    
    # Shadow offset (slightly down and to the right)
    shadow_offset_x = x_position + 5
    shadow_offset_y = y_position + 8
    
    # 6. Composite the layers
    # First paste shadow
    background.paste(shadow, (shadow_offset_x, shadow_offset_y), shadow)
    # Then paste person on top
    background.paste(subject_resized, (x_position, y_position), subject_resized)
    
    # 7. Optional: Slight sharpening to maintain quality
    result = background.convert("RGB")
    enhancer = ImageEnhance.Sharpness(result)
    result = enhancer.enhance(1.1)  # Slight sharpening
    
    return result
