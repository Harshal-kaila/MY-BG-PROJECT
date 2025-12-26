from rembg import remove
import io
from PIL import Image

def remove_background_logic(input_image):
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    input_image.save(img_byte_arr, format='PNG')
    raw_data = img_byte_arr.getvalue()
    
    # AI Processing
    clean_data = remove(raw_data)
    
    # Return as displayable PIL image
    return Image.open(io.BytesIO(clean_data))
