from rembg import remove
import io
from PIL import Image, ImageFilter, ImageEnhance, ImageOps


def remove_background_logic(input_image: Image.Image) -> Image.Image:
    """Return subject with transparent background (PNG)."""
    buf = io.BytesIO()
    input_image.save(buf, format="PNG")
    data = buf.getvalue()
    cut = remove(data)
    img = Image.open(io.BytesIO(cut)).convert("RGBA")
    return img


def _erode_alpha(img: Image.Image, radius: int = 2) -> Image.Image:
    """Slightly shrink the alpha mask to remove halos around edges."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    r, g, b, a = img.split()
    a = a.filter(ImageFilter.MinFilter(radius=radius))
    img.putalpha(a)
    return img


def compose_portrait_canvas(
    subject_img: Image.Image,
    background_file: str,
    canvas_ratio: float = 9 / 16,
    blur_bg: bool = True,
) -> Image.Image:
    """
    Create a vertical 'selfie-style' canvas:
    - Canvas aspect is 9:16 (good for phone & web).
    - Background is cropped & resized to fill canvas.
    - Subject stays sharp; background can be blurred.
    - Background is sized around the subject (same height).
    """

    # 1. Prepare subject (cutout)
    subject = subject_img.convert("RGBA")
    subject = _erode_alpha(subject, radius=2)

    subj_w, subj_h = subject.size

    # 2. Define canvas size based on subject height
    #    Make canvas height ≈ subject height * 1.2 (headroom)
    canvas_h = int(subj_h * 1.2)
    canvas_w = int(canvas_h * canvas_ratio)

    # Ensure canvas is at least as wide as subject
    if canvas_w < subj_w:
        canvas_w = subj_w
        canvas_h = int(canvas_w / canvas_ratio)

    # 3. Load and prepare background
    bg = Image.open(f"assets/{background_file}").convert("RGB")
    bg_w, bg_h = bg.size
    bg_ratio = bg_w / bg_h

    # Need to resize+crop background to exactly canvas size
    if bg_ratio > canvas_ratio:
        # Background is wider than canvas: match height, crop width
        new_h = canvas_h
        new_w = int(new_h * bg_ratio)
    else:
        # Background is taller: match width, crop height
        new_w = canvas_w
        new_h = int(new_w / bg_ratio)

    bg_resized = bg.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Center crop to canvas size
    left = (new_w - canvas_w) // 2
    top = (new_h - canvas_h) // 2
    bg_cropped = bg_resized.crop((left, top, left + canvas_w, top + canvas_h))

    if blur_bg:
        bg_cropped = bg_cropped.filter(ImageFilter.GaussianBlur(2))

    bg_cropped = bg_cropped.convert("RGBA")

    # 4. Scale subject relative to canvas (keep natural size)
    # Subject should occupy about 70% of canvas height.
    target_h = int(canvas_h * 0.7)
    scale = target_h / subj_h
    target_w = int(subj_w * scale)
    subject_resized = subject.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # 5. Position subject anchored to bottom
    x = (canvas_w - target_w) // 2
    y = canvas_h - target_h  # bottom aligned

    # 6. Composite
    final_img = bg_cropped.copy()
    final_img.paste(subject_resized, (x, y), subject_resized)

    # 7. Small global color/contrast tweaks (optional but keeps quality)
    final_rgb = final_img.convert("RGB")
    enhancer = ImageEnhance.Contrast(final_rgb)
    final_rgb = enhancer.enhance(1.03)
    enhancer = ImageEnhance.Color(final_rgb)
    final_rgb = enhancer.enhance(1.02)

    return final_rgb
