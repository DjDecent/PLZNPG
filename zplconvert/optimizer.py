"""
Optimizer module for improving ZPL conversion performance.
"""

from PIL import Image


def optimize_image(image, quality=85, max_size=None):
    """Optimize an image for faster rendering without changing label geometry."""
    if max_size is None:
        max_size = (image.width, image.height)

    if image.width > max_size[0] or image.height > max_size[1]:
        image = image.copy()
        image.thumbnail(max_size, Image.Resampling.NEAREST)

    if image.mode != 'RGB':
        image = image.convert('RGB')

    optimized = Image.new('RGB', image.size, (255, 255, 255))
    optimized.paste(image)
    return optimized


def optimize_zpl(zpl_data):
    """Analyze ZPL data and remove redundant or unnecessary commands."""
    # Support both real newlines and literal \n sequences from stored files
    if '\\n' in zpl_data and '\n' not in zpl_data.replace('\\n', ''):
        zpl_data = zpl_data.replace('\\n', '\n')
    zpl_data = zpl_data.replace('\\n', '\n')

    lines = zpl_data.split('\n')
    lines = [line for line in lines if line.strip() and not line.strip().startswith('^FX')]

    last_command = None
    optimized_lines = []

    for line in lines:
        if line.strip() == '^FS' and last_command == '^FS':
            continue
        optimized_lines.append(line)
        last_command = line.strip()

    return '\n'.join(optimized_lines)
