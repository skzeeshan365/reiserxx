from PIL import Image
import io


def handle_uploaded_image(f):
    # Open the uploaded image in RGBA format
    img = Image.open(f)
    # Convert the image to RGB format
    img = img.convert('RGB')
    # Save the image to a byte stream
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=75)
    output.seek(0)
    # Return the byte stream
    return output