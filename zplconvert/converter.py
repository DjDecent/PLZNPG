"""Core ZPL conversion functionality."""

import os
from .parser import parse_zpl
from .optimizer import optimize_image, optimize_zpl


def convert_zpl_to_image(zpl_data, width=812, height=1218, dpi=203, optimize=False):
    """Convert ZPL data to a PIL Image.

    Default size matches a typical 4x6" shipping label at 8 dpmm (203 dpi).
    """
    if optimize:
        zpl_data = optimize_zpl(zpl_data)

    label = parse_zpl(zpl_data, width, height, dpi)
    image = label.render()

    if optimize:
        image = optimize_image(image, max_size=(image.width, image.height))

    return image


def convert_zpl_file_to_image(zpl_file, output_file=None, width=812, height=1218, dpi=203):
    """Convert a ZPL file to an image file."""
    with open(zpl_file, 'r') as f:
        zpl_data = f.read()

    image = convert_zpl_to_image(zpl_data, width, height, dpi)

    if output_file:
        directory = os.path.dirname(output_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        image.save(output_file)
        return None
    return image
