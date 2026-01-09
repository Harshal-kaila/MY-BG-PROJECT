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

def match_colors(subject, background):
    """Adjusts the selfie's lighting to match the background mood."""
    # Ensure both are RGB for stat calculation
    subj_rgb = subject.convert("RGB")
    bg_rgb = background.convert("RGB")
    
    subj_stat = ImageStat.Stat(subj_rgb)
    bg_stat = ImageStat.Stat(bg_rgb)
    
    # Calculate color ratios
    r_ratio = bg_stat.mean[0] / (subj_stat.mean[0] + 1e-5)
    g_ratio = bg_stat.mean[1] / (subj_stat.mean[1] + 1e-5)
    b_ratio = bg_stat.mean[2] / (subj_stat.mean[2] + 1e-5)
    
    # Apply a gentle 30% correction
    r_weight, g_weight, b_weight = 0.3, 0.3, 0.3
    
    # We apply the transformation to the RGB version then put the alpha back
    # This prevents the 'ValueError: image has wrong mode'
    matrix = (
        r_ratio * r_weight + (1 - r_weight), 0, 0, 0,
        0, g_ratio * g_weight + (1 - g_weight), 0, 0,
        0, 0, b_ratio * b_weight + (1 - b_weight), 0
    )
    
    # Transform the RGB part
    matched_rgb = subj_rgb.convert("RGB", matrix)
    
    # Put the original transparency (alpha) back onto the color-matched image
    result = matched_rgb.convert("RGBA")
    result.putalpha(subject.split()[-1])
    
    return result