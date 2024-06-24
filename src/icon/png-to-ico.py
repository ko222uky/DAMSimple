from PIL import Image

def convert_png_to_ico(png_file_path, ico_file_path, icon_size=(64, 64)):
    """
    Convert a PNG image to an ICO file.

    Parameters:
    - png_file_path: Path to the source PNG file.
    - ico_file_path: Path where the ICO file will be saved.
    - icon_size: A tuple (width, height) for the icon size. Default is 64x64.
    """
    # Open the PNG file
    img = Image.open(png_file_path)
    
    # Convert the image to the desired resolution
    img = img.resize(icon_size)   
    # Save the image as an ICO file
    img.save(ico_file_path, format='ICO')

# Example usage
convert_png_to_ico('damnsimple-fly.png', 'fly.ico', (64, 64))