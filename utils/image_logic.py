from rembg import remove
import io
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageStat

def remove_background_logic(input_image):
    """Removes background and applies edge softening (feathering)."""
    buf = io.BytesIO()
    input_image.save(buf, format='PNG')
    input_data = buf.getvalue()
    
    # Remove background
    output_data = remove(input_data)
    result = Image.open(io.BytesIO(output_data)).convert("RGBA")
    
    # --- NATURAL FIT STEP 1: Edge Feathering ---
    # We blur the alpha mask slightly so the edges aren't sharp/jagged
    alpha = result.split()[-1]
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=1.5))
    result.putalpha(alpha)
    
    return result

def match_colors(subject, background):
    """Adjusts the selfie's lighting to match the background mood."""
    # Get average color stats for both images
    subj_stat = ImageStat.Stat(subject.convert("RGB"))
    bg_stat = ImageStat.Stat(background.convert("RGB"))
    
    # Calculate color ratios (how much red, green, and blue to shift)
    r_ratio = bg_stat.mean[0] / (subj_stat.mean[0] + 1e-5)
    g_ratio = bg_stat.mean[1] / (subj_stat.mean[1] + 1e-5)
    b_ratio = bg_stat.mean[2] / (subj_stat.mean[2] + 1e-5)
    
    # Apply a gentle 40% correction to avoid looking 'filtered'
    matrix = (
        r_ratio * 0.4 + 0.6, 0, 0, 0,
        0, g_ratio * 0.4 + 0.6, 0, 0,
        0, 0, b_ratio * 0.4 + 0.6, 0
    )
    return subject.convert("RGB", matrix).convert("RGBA")

def merge_with_background(subject_img, bg_filename):
    """Composites the subject onto a background with lighting and shadows."""
    # Load and prep background
    bg_path = f"assets/{bg_filename}"
    background = Image.open(bg_path).convert("RGBA")
    
    # Standardize canvas size (e.g., 1080x1350 for high quality)
    canvas_w, canvas_h = 1080, 1350
    bg_resized = ImageOps.fit(background, (canvas_w, canvas_h), Image.Resampling.LANCZOS)
    
    # Resize subject (approx 75% of canvas height)
    subj_w, subj_h = subject_img.size
    target_h = int(canvas_h * 0.75)
    target_w = int(subj_w * (target_h / subj_h))
    subject_resized = subject_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # --- NATURAL FIT STEP 2: Color Matching ---
    subject_resized = match_colors(subject_resized, bg_resized)
    
    # Position (Centered at bottom)
    x = (canvas_w - target_w) // 2
    y = canvas_h - target_h
    
    # --- NATURAL FIT STEP 3: Subtle Drop Shadow ---
    # Creates a very faint shadow to anchor the person to the ground
    shadow = subject_resized.split()[-1].point(lambda p: p * 0.2)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=20))
    
    # Final Assembly
    final_image = bg_resized.copy()
    # Paste shadow slightly offset
    final_image.paste((0,0,0,80), (x+5, y+10), mask=shadow)
    # Paste subject using Alpha Composite for smooth blending
    final_image.alpha_composite(subject_resized, (x, y))
    
    return final_image.convert("RGB")