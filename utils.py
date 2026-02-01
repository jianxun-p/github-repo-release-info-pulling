import base64
from PIL import Image, ImageDraw

screenshot_path = "screenshot.png"
url = "https://github.com"



width, height = 1280, 720
box_pos = [0, 0, 1280, 720]


# Function to encode the image
def encode_image(image_path):
    """
    returns base64 encoding of image
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def draw_box(out_path, in_path, rect, alpha=128):
    """
    Crop/draw the box from the input screenshot
    """
    
    # draw the shaded rectangle version (for visualization only)
    with Image.open(in_path) as img:
        base = img.convert("RGBA")
        
        # 2. Create a transparent overlay the same size as the image
        overlay = Image.new("RGBA", base.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        # 4. Draw the red rectangle on the overlay
        draw.rectangle((rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3]), fill=(255, 0, 0, alpha))
        # 5. Alpha composite the overlay onto the base image
        result = Image.alpha_composite(base, overlay)
        
        # 6. Convert back to RGB if you want to save as JPEG, or keep as RGBA for PNG
        result.convert("RGB").save(out_path)

    # crop screenshot (for the model)
    with Image.open(in_path) as img:
        # 1. Perform the crop
        # The crop box is defined as a 4-tuple (x0, y0, x1, y1)
        x0 = max(0, rect[0])
        x1 = min(width, rect[0] + rect[2])
        y0 = max(0, rect[1] - rect[3])
        y1 = min(height, rect[1] + rect[3])
        cropped_img = img.crop((x0, y0, x1, y1))
        cropped_img.save("croped.png")

