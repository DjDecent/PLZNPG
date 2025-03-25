"""Graphic element classes for ZPL conversion."""

import os
import math
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from .base import BaseElement


class LineElement(BaseElement):
    """Element for rendering lines on labels."""
    
    def __init__(self, x, y, width, height, thickness=1, line_color=(0, 0, 0), reverse=False):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.thickness = thickness
        self.line_color = line_color
        self.reverse = reverse

    def draw(self, draw):
        # Apply reverse effect to line color if needed
        line_color = self.line_color
        if self.reverse:
            line_color = (255, 255, 255) if self.line_color == (0, 0, 0) else (0, 0, 0)

        if self.width > self.height:
            # Horizontal line
            for i in range(self.thickness):
                draw.line([(self.x, self.y + i), (self.x + self.width - 1, self.y + i)], fill=line_color)
        else:
            # Vertical line
            for i in range(self.thickness):
                draw.line([(self.x + i, self.y), (self.x + i, self.y + self.height - 1)], fill=line_color)

    def __str__(self):
        return f"LineElement(x={self.x}, y={self.y}, width={self.width}, height={self.height}, thickness={self.thickness}, line_color={self.line_color}, reverse={self.reverse})"

class BoxElement(BaseElement):
    """Element for rendering boxes on labels."""
    
    def __init__(self, x, y, width, height, thickness=1, line_color=(0, 0, 0), fill_color=None, reverse=False):
        super().__init__(x, y)
        self.width = max(width, 1)  # Ensure minimum width of 1
        self.height = max(height, 1)  # Ensure minimum height of 1
        self.thickness = thickness
        self.line_color = line_color
        self.fill_color = fill_color
        self.reverse = reverse

    def draw(self, draw):
        try:
            if self.reverse:
                temp = self.line_color
                self.line_color = self.fill_color or (255, 255, 255)
                self.fill_color = temp

            if self.fill_color:
                draw.rectangle([self.x, self.y, self.x + self.width, self.y + self.height], fill=self.fill_color)

            for i in range(self.thickness):
                draw.rectangle([self.x + i, self.y + i, self.x + self.width - i, self.y + self.height - i], outline=self.line_color)

        except Exception as e:
            import traceback
            traceback.print_exc()

    def __str__(self):
        return f"BoxElement(x={self.x}, y={self.y}, width={self.width}, height={self.height}, thickness={self.thickness}, line_color={self.line_color}, fill_color={self.fill_color}, reverse={self.reverse})"

    def __repr__(self):
        return self.__str__()

class LogoElement(BaseElement):
    """Element for rendering logo images on labels."""
    
    def __init__(self, x, y, image_path, width=None, height=None):
        super().__init__(x, y)
        self.image_path = image_path
        self.width = width if width is not None else 100  # Default width
        self.height = height if height is not None else 100  # Default height

    def draw(self, draw):
        try:
            if os.path.exists(self.image_path):
                logo = Image.open(self.image_path)
                logo = logo.resize((self.width, self.height))
                draw._image.paste(logo, (self.x, self.y))
            else:
                # Draw a placeholder
                draw.rectangle([self.x, self.y, self.x + self.width, self.y + self.height], outline="black")
                draw.text((self.x + 5, self.y + self.height // 2), "Logo", fill="black")
        except Exception as e:
            # Draw an error placeholder
            draw.rectangle([self.x, self.y, self.x + self.width, self.y + self.height], outline="red")
            draw.text((self.x + 5, self.y + self.height // 2), "Error", fill="red")

class ImageElement(BaseElement):
    """Element for rendering bitmap images on labels."""
    
    def __init__(self, x, y, width, height, image_data, format='A'):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.image_data = image_data
        self.format = format
        self.widthBytes = (width + 7) // 8
        self.total = self.widthBytes * height
        self.mapCode = self.initialize_map_code()
        self._cache = None  # Initialize cache

    @staticmethod
    def initialize_map_code():
        mapCode = {}
        for i in range(1, 20):
            mapCode[i] = chr(ord('G') + i - 1)
        for i in range(20, 401, 20):
            mapCode[i] = chr(ord('g') + (i // 20) - 1)
        return mapCode

    def gfa_to_image(self):
        hex_data = self.ascii_to_hex(self.image_data)
        binary_data = self.hex_to_binary(hex_data)
        image = Image.new('1', (self.width, self.height))
        pixels = image.load()

        for y in range(self.height):
            for x in range(self.width):
                byte_index = (y * self.widthBytes) + (x // 8)
                bit_index = 7 - (x % 8)
                if byte_index < len(binary_data):
                    pixel = (binary_data[byte_index] >> bit_index) & 1
                    pixels[x, y] = 255 if pixel == 0 else 0  # 0 for black, 255 for white

        return image

    def ascii_to_hex(self, ascii_data):
        hex_lines = []
        current_line = ""
        previous_line = ""
        
        for char in ascii_data:
            if char in '0123456789ABCDEF':
                current_line += char
            elif char in self.mapCode.values():
                count = next(key for key, value in self.mapCode.items() if value == char)
                current_line += '0' * count
            elif char == ',':
                # Pad the current line to the full width before adding it
                padded_line = self.pad_line(current_line)
                if padded_line:
                    hex_lines.append(padded_line)
                    previous_line = padded_line
                current_line = ""
            elif char == ':':
                if previous_line:
                    hex_lines.append(previous_line)
            # Ignore other characters

        # Don't forget to add the last line if there's no trailing comma
        if current_line:
            padded_line = self.pad_line(current_line)
            if padded_line:
                hex_lines.append(padded_line)

        return '\n'.join(hex_lines)

    def pad_line(self, line):
        # Calculate how many hex characters we need for a full line
        full_line_length = self.widthBytes * 2
        if len(line) > full_line_length:
            # If the line is too long, truncate it
            padded_line = line[:full_line_length]
            return padded_line
        elif len(line) < full_line_length:
            # If the line is too short, pad it with '0's
            padded_line = line.ljust(full_line_length, '0')
            return padded_line
        else:
            # If the line is exactly the right length, return it as is
            return line

    def hex_to_binary(self, hex_data):
        binary_data = bytearray()
        for line in hex_data.split('\n'):
            for i in range(0, len(line), 2):
                if i + 1 < len(line):
                    binary_data.append(int(line[i:i+2], 16))
                else:
                    binary_data.append(int(line[i] + '0', 16))
        return binary_data

    def draw(self, draw):
        if self._cache:
            draw._image.paste(self._cache, (self.x, self.y))
            return

        if self.format == 'A':  # ASCII format
            try:
                image = self.gfa_to_image()
                draw._image.paste(image, (self.x, self.y))
                self._cache = image  # Cache the image
            except Exception as e:
                import traceback
                traceback.print_exc()
        else:
            pass
