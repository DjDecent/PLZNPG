import os
import math
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageColor, ImageFilter
from barcode import Code128
from barcode.writer import ImageWriter
from barcode.charsets import code128
from pystrich.code128 import Code128Encoder
from pystrich.datamatrix import DataMatrixEncoder

class Text:
    def __init__(self, x, y, text, font_size=12, font=None):
        self.x = x
        self.y = y
        self.text = text
        self.font_size = font_size
        self.font = font if font else ImageFont.load_default()

    def draw(self, draw: ImageDraw.Draw):
        draw.text((self.x, self.y), self.text, font=self.font, fill="black")

class BaseElement:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def draw(self, draw):
        pass

"""Text element classes for ZPL conversion."""

import os
from PIL import Image, ImageFont, ImageDraw
from .base import BaseElement

class TextElement(BaseElement):
    """Element for rendering text on labels."""
    
    def __init__(self, x, y, text, font_size=12, bold=False, reverse=False, rotation=0):
        super().__init__(x, y)
        self.text = text
        self.font_size = font_size
        self.bold = bold
        self.reverse = reverse
        self.rotation = rotation
        self.font_path = self._get_font_path()

    def _get_font_path(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        font_name = "RobotoCondensed-Bold.ttf" if self.bold else "RobotoCondensed-Regular.ttf"
        font_path = os.path.join(base_dir, "fonts", font_name)
        return font_path

    def draw(self, draw):
        try:
            font = ImageFont.truetype(self.font_path, self.font_size)
            text_color = (255, 255, 255) if self.reverse else (0, 0, 0)
            
            # Get text dimensions using textbbox
            bbox = draw.textbbox((0, 0), self.text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Add padding to avoid text cutoff
            padding = max(10, self.font_size // 2)
            
            # Draw according to rotation
            if self.rotation == 0:
                # Standard orientation
                draw.text((self.x, self.y), self.text, font=font, fill=text_color, anchor="lt")
            
            elif self.rotation == 90:
                # Rotate 90 degrees (clockwise)
                # Create larger temp image with proper padding
                temp_img = Image.new('RGBA', (text_height + padding*2, text_width + padding*2), (255, 255, 255, 0))
                temp_draw = ImageDraw.Draw(temp_img)
                
                # Draw text in the center of the temp image
                temp_draw.text((temp_img.width // 2, temp_img.height // 2), self.text, 
                              font=font, fill=text_color, anchor="mm")
                
                # Rotate clockwise (270 degrees counter-clockwise is actually 90 degrees clockwise)
                rotated = temp_img.rotate(270, expand=True, resample=Image.BICUBIC)
                
                # Adjust position to maintain alignment with original position - moved to the left
                draw._image.paste(rotated, (self.x - padding, self.y - padding), rotated)
            
            elif self.rotation == 180:
                # Rotate 180 degrees
                temp_img = Image.new('RGBA', (text_width + padding*2, text_height + padding*2), (255, 255, 255, 0))
                temp_draw = ImageDraw.Draw(temp_img)
                temp_draw.text((temp_img.width // 2, temp_img.height // 2), self.text, 
                              font=font, fill=text_color, anchor="mm")
                rotated = temp_img.rotate(180, expand=True, resample=Image.BICUBIC)
                draw._image.paste(rotated, (self.x - padding, self.y - padding), rotated)
            
            elif self.rotation == 270:
                # Rotate 270 degrees (counter-clockwise)
                temp_img = Image.new('RGBA', (text_height + padding * 2, text_width + padding * 2), (255, 255, 255, 0))
                temp_draw = ImageDraw.Draw(temp_img)
                temp_draw.text((temp_img.width // 2, temp_img.height // 2), self.text, 
                               font=font, fill=text_color, anchor="mm")
                rotated = temp_img.rotate(90, expand=True, resample=Image.BICUBIC)
                draw._image.paste(rotated, (self.x - padding, self.y - padding), rotated)
                print(f"Drew text: '{self.text}' at ({self.x}, {self.y}) with rotation {self.rotation}°")
                print(f"Drew text: '{self.text}' at ({self.x}, {self.y}) with rotation {self.rotation}°")
        except Exception as e:
            print(f"Error drawing TextElement: {str(e)}")
            import traceback
            traceback.print_exc()

