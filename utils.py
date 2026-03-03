import base64

# Function to encode the image
def encode_image(image_path):
    """
    returns base64 encoding of image
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
