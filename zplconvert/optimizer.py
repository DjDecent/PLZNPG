"""
Optimizer module for improving ZPL conversion performance.
"""

from PIL import Image

def optimize_image(image, quality=85, max_size=(800, 1200)):
    """Optimize an image for faster rendering.
    
    Args:
        image (PIL.Image): The image to optimize
        quality (int): JPEG quality (1-100)
        max_size (tuple): Maximum width and height
        
    Returns:
        PIL.Image: The optimized image
    """
    # Resize if larger than max_size
    if image.width > max_size[0] or image.height > max_size[1]:
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
    # Convert to RGB if needed (for JPEG)
    if image.mode != 'RGB':
        image = image.convert('RGB')
        
    # Create a new optimized image
    optimized = Image.new('RGB', image.size, (255, 255, 255))
    optimized.paste(image)
    
    return optimized

def optimize_zpl(zpl_data):
    """Analyze ZPL data and remove redundant or unnecessary commands.
    
    Args:
        zpl_data (str): The ZPL data to optimize
        
    Returns:
        str: Optimized ZPL data
    """
    # Split into lines
    lines = zpl_data.split('\n')
    
    # Remove empty lines and comments
    lines = [line for line in lines if line.strip() and not line.strip().startswith('^FX')]
    
    # Remove duplicate field separator commands
    last_command = None
    optimized_lines = []
    
    for line in lines:
        # Skip consecutive field separators
        if line.strip() == '^FS' and last_command == '^FS':
            continue
            
        optimized_lines.append(line)
        last_command = line.strip()
    
    return '\n'.join(optimized_lines)
