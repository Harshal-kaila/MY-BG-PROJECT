from rembg import remove
import io
import os
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageStat, ImageEnhance

def remove_background_logic(input_image):
    """Removes background and applies edge softening."""
    buf = io.BytesIO()
    input_image.save(buf, format='PNG')
    input_data = buf.getvalue()
    
    # Remove background
    output_data = remove(input_data)
    result = Image.open(io.BytesIO(output_data)).convert("RGBA")
    
    # Edge Feathering (Makes the cutout less sharp)
    alpha = result.split()[-1]
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=1.5))
    result.putalpha(alpha)
    
    return result

def match_colors(subject, background):
    """Adjusts the selfie's lighting and brightness to match the background."""
    subj_rgb = subject.convert("RGB")
    bg_rgb = background.convert("RGB")
    
    subj_stat = ImageStat.Stat(subj_rgb)
    bg_stat = ImageStat.Stat(bg_rgb)
    
    # Calculate color ratios
    r_ratio = bg_stat.mean[0] / (subj_stat.mean[0] + 1e-5)
    g_ratio = bg_stat.mean[1] / (subj_stat.mean[1] + 1e-5)
    b_ratio = bg_stat.mean[2] / (subj_stat.mean[2] + 1e-5)
    
    # Apply a gentle correction
    matrix = (
        r_ratio * 0.3 + 0.7, 0, 0, 0,
        0, g_ratio * 0.3 + 0.7, 0, 0,
        0, 0, b_ratio * 0.3 + 0.7, 0
    )
    
    matched_rgb = subj_rgb.convert("RGB", matrix)
    
    # Auto-adjust brightness to match background intensity
    bg_brightness = sum(bg_stat.mean) / 3
    subj_brightness = sum(subj_stat.mean) / 3
    brightness_factor = bg_brightness / (subj_brightness + 1e-5)
    
    enhancer = ImageEnhance.Brightness(matched_rgb)
    matched_rgb = enhancer.enhance(max(0.8, min(brightness_factor, 1.2)))
    
    result = matched_rgb.convert("RGBA")
    result.putalpha(subject.split()[-1])
    return result

def merge_with_background(subject_img, bg_filename):
    """Composites the subject to fill the background naturally."""
    bg_path = os.path.join("assets", bg_filename)
    if not os.path.exists(bg_path):
        raise FileNotFoundError(f"Missing asset: {bg_path}")

    background = Image.open(bg_path).convert("RGBA")
    
    # 1. Resize background to a standard high-quality canvas
    canvas_w, canvas_h = 1080, 1350
    bg_resized = ImageOps.fit(background, (canvas_w, canvas_h), Image.Resampling.LANCZOS)
    
    # OPTIONAL: Slightly blur the background to create depth (Bokeh effect)
    bg_blurred = bg_resized.filter(ImageFilter.GaussianBlur(radius=2))
    
    # 2. Scale subject to "FILL" the frame (usually 85-90% of height for travel photos)
    subj_w, subj_h = subject_img.size
    target_h = int(canvas_h * 0.85) 
    target_w = int(subj_w * (target_h / subj_h))
    subject_resized = subject_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # 3. Apply Color and Lighting Match
    subject_resized = match_colors(subject_resized, bg_blurred)
    
    # 4. Positioning (Bottom Center)
    x = (canvas_w - target_w) // 2
    y = canvas_h - target_h
    
    # 5. Create a soft contact shadow at the bottom
    shadow = subject_resized.split()[-1].point(lambda p: p * 0.25)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=15))
    
    # Final Assembly
    final_image = bg_blurred.copy()
    final_image.paste((0, 0, 0, 100), (x, y + 5), mask=shadow) # Contact shadow
    final_image.alpha_composite(subject_resized, (x, y))
    
    return final_image.convert("RGB")