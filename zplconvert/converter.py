"""Core ZPL conversion functionality."""

import os
from .parser import parse_zpl
from .optimizer import optimize_image, optimize_zpl  # Add this import

def convert_zpl_to_image(zpl_data, width=850, height=1200, dpi=203, optimize=False):
    """Convert ZPL data to a PIL Image.
    
    Args:
        zpl_data (str): ZPL commands as text
        width (int): Width of the output image in pixels
        height (int): Height of the output image in pixels
        dpi (int): Dots per inch resolution
        optimize (bool): Whether to apply optimization
        
    Returns:
        PIL.Image: Rendered label image
    """
    # Optimize ZPL code if requested
    if optimize:
        zpl_data = optimize_zpl(zpl_data)
        # Adjust dimensions for faster rendering
        width = min(width, 800)
        height = min(height, 1200)
    
    # Parse ZPL and get the label
    label = parse_zpl(zpl_data, width, height, dpi)
    
    # Render the label
    image = label.render()
    
    # Optimize the image if requested
    if optimize:
        image = optimize_image(image)
    
    return image

def convert_zpl_file_to_image(zpl_file, output_file=None, width=850, height=1200, dpi=203):
    """Convert a ZPL file to an image file.
    
    Args:
        zpl_file (str): Path to ZPL file
        output_file (str, optional): Path to output image file. If None, returns the image object.
        width (int): Width of the output image in pixels
        height (int): Height of the output image in pixels
        dpi (int): Dots per inch resolution
        
    Returns:
        PIL.Image if output_file is None, otherwise None
    """
    # Read ZPL data from file
    with open(zpl_file, 'r') as f:
        zpl_data = f.read()
    
    # Convert ZPL data to image
    image = convert_zpl_to_image(zpl_data, width, height, dpi)
    
    # Save image or return it
    if output_file:
        directory = os.path.dirname(output_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        image.save(output_file)
        return None
    else:
        return image
