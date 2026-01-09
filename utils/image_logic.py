from rembg import remove
import io
import os
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageStat

def remove_background_logic(input_image):
    """Removes background and applies edge softening."""
    buf = io.BytesIO()
    input_image.save(buf, format='PNG')
    input_data = buf.getvalue()
    
    output_data = remove(input_data)
    result = Image.open(io.BytesIO(output_data)).convert("RGBA")
    
    # Edge Feathering
    alpha = result.split()[-1]
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=1.5))
    result.putalpha(alpha)
    
    return result

def match_colors(subject, background):
    """Adjusts the selfie's lighting to match the background mood."""
    subj_rgb = subject.convert("RGB")
    bg_rgb = background.convert("RGB")
    
    subj_stat = ImageStat.Stat(subj_rgb)
    bg_stat = ImageStat.Stat(bg_rgb)
    
    r_ratio = bg_stat.mean[0] / (subj_stat.mean[0] + 1e-5)
    g_ratio = bg_stat.mean[1] / (subj_stat.mean[1] + 1e-5)
    b_ratio = bg_stat.mean[2] / (subj_stat.mean[2] + 1e-5)
    
    r_weight, g_weight, b_weight = 0.3, 0.3, 0.3
    
    matrix = (
        r_ratio * r_weight + (1 - r_weight), 0, 0, 0,
        0, g_ratio * g_weight + (1 - g_weight), 0, 0,
        0, 0, b_ratio * b_weight + (1 - b_weight), 0
    )
    
    matched_rgb = subj_rgb.convert("RGB", matrix)
    result = matched_rgb.convert("RGBA")
    result.putalpha(subject.split()[-1])
    
    return result

def merge_with_background(subject_img, bg_filename):
    """Composites the subject onto a background."""
    bg_path = os.path.join("assets", bg_filename)
    
    if not os.path.exists(bg_path):
        raise FileNotFoundError(f"Missing asset: {bg_path}")

    background = Image.open(bg_path).convert("RGBA")
    
    # Canvas setup
    canvas_w, canvas_h = 1080, 1350
    bg_resized = ImageOps.fit(background, (canvas_w, canvas_h), Image.Resampling.LANCZOS)
    
    # Subject resize
    subj_w, subj_h = subject_img.size
    target_h = int(canvas_h * 0.75)
    target_w = int(subj_w * (target_h / subj_h))
    subject_resized = subject_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Natural Fit: Color Match
    subject_resized = match_colors(subject_resized, bg_resized)
    
    # Positioning
    x = (canvas_w - target_w) // 2
    y = canvas_h - target_h
    
    # Natural Fit: Shadow
    shadow = subject_resized.split()[-1].point(lambda p: p * 0.2)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=20))
    
    final_image = bg_resized.copy()
    final_image.paste((0, 0, 0, 80), (x + 5, y + 10), mask=shadow)
    final_image.alpha_composite(subject_resized, (x, y))
    
    return final_image.convert("RGB")