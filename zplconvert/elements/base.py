"""Base element class for ZPL elements."""

import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

class BaseElement:
    """Base class for all ZPL elements."""
    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def draw(self, draw):
        """Draw the element on the given drawing context.
        
        Args:
            draw: PIL.ImageDraw object
        """
        raise NotImplementedError("Subclasses must implement the draw method.")